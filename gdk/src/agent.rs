//! The GDK agent: one goose-agent `StateMachine` per run, over a conversation the app keeps.
//!
//! Steps, in priority order:
//! 1. `SlashCommandOperation` with [`SkillCommands`]: `/small-storyworld lighthouse` appends the loaded
//!    skill to the conversation.
//! 2. `TextToolCalls` turns `<tool_call>` text into tool requests (text-mode servers, and native
//!    replies the server left unparsed).
//! 3. `ToolApprovalOperation` with [`Approval`]: read-only tools and `load_skill` run; workspace writes
//!    need `--approve write` (the default); a call identical to one that already failed twice is refused
//!    with the last error.
//! 4. `ToolOperation` dispatches approved calls to the Storyworld MCP server and the skill provider.
//! 5. `UnhandledToolCallsOperation` answers calls nothing handled.
//! 6. `MaxTurnsOperation` caps model turns per run.
//! 7. `StoryworldPrompt` contributes the app, skill index and server instructions.
//! 8. `InferenceRunner` calls the local model through `goose-providers`; [`PacketPreparer`] elides
//!    older large tool results before each request when the run has a packet budget (small mode).

use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

use anyhow::Result;
use async_trait::async_trait;
use goose_agent::inference::{InferenceEffect, InferenceRequestPreparer, InferenceRunner, PreparedInferenceRequest};
use goose_agent::machine::{EffectHandler, MachineSession, SessionLoader, StateMachine, Step};
use goose_agent::max_turns::MaxTurnsOperation;
use goose_agent::operation::{ConversationEffect, Emitter, InferenceInput, MachineEffect, Operation};
use goose_agent::slash_command::SlashCommandOperation;
use goose_agent::tool::ToolOperation;
use goose_agent::tool_approval::{ApprovalDecision, ToolApproval, ToolApprovalOperation};
use goose_agent::unhandled_tool_calls::UnhandledToolCallsOperation;
use goose_provider_types::conversation::message::{Message, MessageContent, ToolRequest};
use goose_provider_types::conversation::token_usage::ProviderUsage;
use goose_provider_types::conversation::{effective_role, Conversation, EffectiveRole};
use goose_provider_types::model::ModelConfig;
use goose_providers::api_client::{ApiClient, AuthMethod};
use goose_providers::openai_compatible::OpenAiCompatibleProvider;
use rmcp::model::{CallToolResult, ContentBlock};
use serde_json::{json, Value};
use tokio::sync::mpsc;
use tokio_util::sync::CancellationToken;

use crate::mcp::{Mode, StoryworldTools};
use crate::skills::{SkillCommands, SkillSet, SkillTools, LOAD_SKILL};
use crate::text_tools::{protocol_prompt, render_as_text, result_text, TextToolCalls};

pub const GDK: &str = "goose-agent 0.1.0-alpha.14";

const APP_INSTRUCTIONS: &str = "You are Storyworld, the GPTStoryworld authoring and eval agent, running on the \
operator's own computer with a local model. You build and edit SweepWeave storyworlds (encounters, options, \
reactions, effects, spools, endings) and build exact-graded hypergame evals. The Storyworld tools own the truth: \
they hold the worlds, run sweepweave_validator on every write, run the quality gate and rehearsal, and grade eval \
families exactly. Never state a validator result, quality check, rehearsal number, baseline or score that a tool \
did not return, and never call a world valid unless a tool said so. When a tool refuses a call, read its error \
code and detail, fix the call or choose another edit; do not repeat a refused call unchanged. Finish with a short \
report: the world or family, what changed, what the tools measured, and what to do next.";

// ---- session, effects, runtime ----

#[derive(Clone)]
pub struct Session {
    pub id: String,
    pub conversation: Conversation,
}

impl MachineSession for Session {
    fn id(&self) -> &str {
        &self.id
    }
    fn conversation(&self) -> Option<&Conversation> {
        Some(&self.conversation)
    }
}

pub enum Effect {
    Conversation(ConversationEffect),
    Usage(ProviderUsage),
}

impl MachineEffect for Effect {
    fn ensure_message_ids(&mut self) {
        if let Effect::Conversation(effect) = self {
            effect.ensure_message_ids();
        }
    }
}

impl From<Message> for Effect {
    fn from(message: Message) -> Self {
        Effect::Conversation(ConversationEffect::AppendMessage(message))
    }
}

impl From<ConversationEffect> for Effect {
    fn from(effect: ConversationEffect) -> Self {
        Effect::Conversation(effect)
    }
}

impl InferenceEffect for Effect {
    fn record_usage(usage: ProviderUsage) -> Self {
        Effect::Usage(usage)
    }
}

fn apply_conversation_effect(conversation: &mut Conversation, effect: &ConversationEffect) {
    match effect {
        ConversationEffect::AppendMessage(message) => conversation.push(message.clone()),
        ConversationEffect::ReplaceConversation(replacement) => *conversation = replacement.clone(),
        ConversationEffect::PatchToolRequestMeta { tool_call_id, patch } => {
            for message in conversation.messages_mut().iter_mut() {
                for content in message.content.iter_mut() {
                    if let MessageContent::ToolRequest(request) = content {
                        if &request.id == tool_call_id {
                            let meta = request.tool_meta.get_or_insert_with(|| json!({}));
                            if let (Some(meta), Some(patch)) = (meta.as_object_mut(), patch.as_object()) {
                                for (key, value) in patch {
                                    meta.insert(key.clone(), value.clone());
                                }
                            }
                        }
                    }
                }
            }
        }
        ConversationEffect::SetMessageOperationNote { message_id, operation, key, value } => {
            if let Some(message) = conversation.messages_mut().iter_mut().find(|m| m.id.as_deref() == Some(message_id)) {
                message.metadata.set_operation_note(operation, key, value.clone());
            }
        }
        ConversationEffect::SetMessageVisibility { message_id, user_visible, agent_visible } => {
            if let Some(message) = conversation.messages_mut().iter_mut().find(|m| m.id.as_deref() == Some(message_id)) {
                message.metadata.user_visible = *user_visible;
                message.metadata.agent_visible = *agent_visible;
            }
        }
    }
}

pub struct Runtime {
    pub session: Mutex<Session>,
    pub usage: Mutex<Vec<ProviderUsage>>,
}

impl Runtime {
    pub fn new() -> Arc<Self> {
        Arc::new(Self {
            session: Mutex::new(Session { id: "storyworld".into(), conversation: Conversation::empty() }),
            usage: Mutex::new(Vec::new()),
        })
    }

    pub fn conversation(&self) -> Conversation {
        self.session.lock().unwrap().conversation.clone()
    }
}

#[async_trait]
impl SessionLoader<Session> for Runtime {
    async fn load(&self, _session_id: &str) -> Result<Session> {
        Ok(self.session.lock().unwrap().clone())
    }
}

#[async_trait]
impl EffectHandler<Session, Effect> for Runtime {
    async fn apply_effects(&self, _session: &Session, effects: &mut [Effect], _emit: &Emitter) -> Result<()> {
        for effect in effects.iter() {
            match effect {
                Effect::Conversation(effect) => apply_conversation_effect(&mut self.session.lock().unwrap().conversation, effect),
                Effect::Usage(usage) => self.usage.lock().unwrap().push(usage.clone()),
            }
        }
        Ok(())
    }
}

// ---- approval ----

/// What a headless run may do.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum ApprovePolicy {
    /// Read worlds, run the validator, quality gate, rehearsal and scoring only.
    ReadOnly,
    /// Also write worlds and eval families in the workspace (and held-out sets to the directory a freeze names).
    Write,
}

impl ApprovePolicy {
    pub fn parse(raw: &str) -> Option<Self> {
        match raw {
            "read-only" => Some(Self::ReadOnly),
            "write" => Some(Self::Write),
            _ => None,
        }
    }
    pub fn as_str(self) -> &'static str {
        match self {
            Self::ReadOnly => "read-only",
            Self::Write => "write",
        }
    }
}

pub struct Approval {
    pub tools: Arc<StoryworldTools>,
    pub policy: ApprovePolicy,
}

impl Approval {
    pub fn decide(&self, name: &str) -> ApprovalDecision {
        if name == LOAD_SKILL || self.tools.read_only.contains(name) {
            return ApprovalDecision::Allow;
        }
        if !self.tools.names().contains(name) {
            return ApprovalDecision::Deny { reason: format!("{name} is not a Storyworld tool in this session's mode.") };
        }
        if self.policy == ApprovePolicy::ReadOnly {
            return ApprovalDecision::Deny {
                reason: format!("{name} writes the workspace; this run is read-only (storyworld --approve write)."),
            };
        }
        ApprovalDecision::Allow
    }
}

/// How many times an identical call (name and arguments) may fail before the app refuses to send it.
pub const MAX_IDENTICAL_FAILURES: usize = 2;

fn call_key(name: &str, arguments: &Value) -> String {
    format!("{name} {arguments}")
}

/// Failed calls so far in the conversation, by name and arguments: (count, last error text).
pub fn failed_calls(conversation: &Conversation) -> HashMap<String, (usize, String)> {
    let mut keys = HashMap::new();
    for content in conversation.iter().flat_map(|message| message.content.iter()) {
        if let MessageContent::ToolRequest(request) = content {
            if let Ok(call) = &request.tool_call {
                keys.insert(request.id.clone(), call_key(&call.name, &json!(call.arguments.clone().unwrap_or_default())));
            }
        }
    }
    let mut failures: HashMap<String, (usize, String)> = HashMap::new();
    for content in conversation.iter().flat_map(|message| message.content.iter()) {
        if let MessageContent::ToolResponse(response) = content {
            let failed = !matches!(&response.tool_result, Ok(result) if result.is_error != Some(true));
            if let (true, Some(key)) = (failed, keys.get(&response.id)) {
                let entry = failures.entry(key.clone()).or_insert((0, String::new()));
                entry.0 += 1;
                entry.1 = result_text(response).chars().take(400).collect();
            }
        }
    }
    failures
}

#[async_trait]
impl ToolApproval<Session> for Approval {
    async fn check(&self, _session: &Session, conversation: &Conversation, requests: &[&ToolRequest]) -> Result<Vec<ApprovalDecision>> {
        let failures = failed_calls(conversation);
        Ok(requests
            .iter()
            .map(|request| match &request.tool_call {
                Ok(call) => {
                    let arguments = json!(call.arguments.clone().unwrap_or_default());
                    match failures.get(&call_key(&call.name, &arguments)) {
                        Some((count, error)) if *count >= MAX_IDENTICAL_FAILURES => ApprovalDecision::Deny {
                            reason: format!(
                                "This exact {} call has already failed {count} times ({error}). Do not send it again: \
                                 change the arguments the error names or make a different edit.",
                                call.name
                            ),
                        },
                        _ => self.decide(&call.name),
                    }
                }
                Err(error) => ApprovalDecision::Deny { reason: format!("unreadable tool call: {}", error.message) },
            })
            .collect())
    }
}

// ---- packet budget ----

/// Tool results longer than this many characters are elided once they are not among the newest ones.
pub const ELIDE_CHARS: usize = 400;

/// The conversation with all but the newest `keep` long tool results replaced by a one-line stub, so a
/// low-context model sees the skill, the task, its own calls and the latest cards, not every card so far.
pub fn elide_old_results(conversation: &Conversation, keep: usize) -> Conversation {
    let mut names = HashMap::new();
    let mut long = Vec::new();
    for content in conversation.iter().flat_map(|message| message.content.iter()) {
        match content {
            MessageContent::ToolRequest(request) => {
                if let Ok(call) = &request.tool_call {
                    names.insert(request.id.clone(), call.name.to_string());
                }
            }
            MessageContent::ToolResponse(response) if result_text(response).chars().count() > ELIDE_CHARS => {
                long.push(response.id.clone());
            }
            _ => {}
        }
    }
    let cut: HashSet<String> = long.iter().take(long.len().saturating_sub(keep)).cloned().collect();
    if cut.is_empty() {
        return conversation.clone();
    }
    let messages = conversation.messages().iter().map(|message| {
        let mut message = message.clone();
        for content in message.content.iter_mut() {
            if let MessageContent::ToolResponse(response) = content {
                if cut.contains(&response.id) {
                    let name = names.get(&response.id).cloned().unwrap_or_else(|| "tool".into());
                    response.tool_result = Ok(CallToolResult::success(vec![ContentBlock::text(format!(
                        "[earlier {name} result elided to keep this request inside the packet budget; call {name} again if you need it]"
                    ))]));
                }
            }
        }
        message
    });
    Conversation::new_unvalidated(messages.collect::<Vec<_>>())
}

/// Prepares each inference request: elides old tool results under a packet budget, and in text mode
/// renders tool traffic as `<tool_call>` text with the tool list in the system prompt.
pub struct PacketPreparer {
    pub tool_mode: ToolMode,
    pub keep_results: Option<usize>,
}

#[async_trait]
impl InferenceRequestPreparer<Session> for PacketPreparer {
    async fn prepare_session(&self, session: &Session) -> Result<Option<Session>> {
        let mut conversation = match self.keep_results {
            Some(keep) => elide_old_results(&session.conversation, keep),
            None => session.conversation.clone(),
        };
        if self.tool_mode == ToolMode::Text {
            conversation = render_as_text(&conversation);
        }
        Ok(Some(Session { id: session.id.clone(), conversation }))
    }

    async fn prepare(&self, _session: &Session, _conversation: &Conversation, input: InferenceInput) -> Result<PreparedInferenceRequest> {
        let mut parts: Vec<String> = input.prompt_parts.into_iter().map(|(_, part)| part).collect();
        if self.tool_mode == ToolMode::Text {
            parts.push(protocol_prompt(&input.tools));
            return Ok(PreparedInferenceRequest { system_prompt: parts.join("\n\n"), tools: Vec::new(), additional_messages: Vec::new() });
        }
        Ok(PreparedInferenceRequest { system_prompt: parts.join("\n\n"), tools: input.tools, additional_messages: Vec::new() })
    }
}

// ---- prompt ----

struct StoryworldPrompt {
    parts: Vec<(String, String)>,
}

#[async_trait]
impl Operation<Session, Effect> for StoryworldPrompt {
    fn name(&self) -> &'static str {
        "storyworld_prompt"
    }

    async fn prompt_parts(&self, _session: &Session, _conversation: &Conversation) -> Result<Vec<(String, String)>> {
        Ok(self.parts.clone())
    }
}

// ---- agent ----

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ToolMode {
    Native,
    Text,
}

impl ToolMode {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Native => "native",
            Self::Text => "text",
        }
    }
}

pub struct AgentSetup {
    pub base_url: String,
    pub served_model: String,
    pub tool_mode: ToolMode,
    pub mode: Mode,
    pub context_tokens: usize,
    pub max_tokens: i32,
    pub max_turns: u32,
    pub temperature: f32,
    pub policy: ApprovePolicy,
    pub timeout: Duration,
    /// Keep only this many newest long tool results in each request (small mode); `None` keeps all.
    pub keep_results: Option<usize>,
}

pub struct Agent {
    pub runtime: Arc<Runtime>,
    pub tools: Arc<StoryworldTools>,
    pub skills: Arc<SkillSet>,
    pub setup: AgentSetup,
    provider: Arc<OpenAiCompatibleProvider>,
}

impl Agent {
    pub fn new(setup: AgentSetup, tools: Arc<StoryworldTools>, skills: Arc<SkillSet>) -> Result<Self> {
        let api = ApiClient::with_timeout_and_tls(setup.base_url.clone(), AuthMethod::NoAuth, setup.timeout, None)?;
        let provider = Arc::new(OpenAiCompatibleProvider::new("local".into(), api, String::new()).with_supports_streaming(false));
        Ok(Self { runtime: Runtime::new(), tools, skills, setup, provider })
    }

    pub fn push_user(&self, text: &str) {
        self.runtime.session.lock().unwrap().conversation.push(Message::user().with_text(text).with_generated_id_if_missing());
    }

    fn prompt_parts(&self) -> Vec<(String, String)> {
        let mut parts = vec![("storyworld_gdk".to_string(), APP_INSTRUCTIONS.to_string())];
        let index = self.skills.index_prompt();
        if !index.is_empty() {
            parts.push(("storyworld_skills".to_string(), index));
        }
        if !self.tools.instructions.is_empty() {
            parts.push(("storyworld_server".to_string(), self.tools.instructions.clone()));
        }
        parts
    }

    /// The system prompt the parts form, as recorded in receipts.
    pub fn system_prompt(&self) -> String {
        self.prompt_parts().into_iter().map(|(_, part)| part).collect::<Vec<_>>().join("\n\n")
    }

    /// Run the machine until it yields: a final answer, the turn cap, or `cancel`.
    pub async fn run(&self, cancel: CancellationToken) -> Result<()> {
        let mut names: HashSet<String> = self.tools.names();
        names.insert(LOAD_SKILL.to_string());
        let model = ModelConfig::new(&self.setup.served_model)
            .with_max_tokens(Some(self.setup.max_tokens))
            .with_temperature(Some(self.setup.temperature))
            .with_context_limit(Some(self.setup.context_tokens));
        let preparer: Arc<dyn InferenceRequestPreparer<Session>> =
            Arc::new(PacketPreparer { tool_mode: self.setup.tool_mode, keep_results: self.setup.keep_results });
        let approval = Arc::new(Approval { tools: self.tools.clone(), policy: self.setup.policy });
        let commands: Vec<Arc<dyn Operation<Session, Effect>>> = vec![Arc::new(SkillCommands { skills: self.skills.clone() })];
        let machine: StateMachine<'_, Session, Effect> = StateMachine::new(
            vec![
                Step::Operation(Arc::new(SlashCommandOperation::new(commands))),
                Step::Operation(Arc::new(TextToolCalls { names })),
                Step::Operation(Arc::new(ToolApprovalOperation::new(approval))),
                Step::Operation(Arc::new(
                    ToolOperation::new()
                        .with_provider(self.tools.clone())
                        .with_provider(Arc::new(SkillTools::new(self.skills.clone()))),
                )),
                Step::Operation(Arc::new(UnhandledToolCallsOperation::new())),
                Step::Operation(Arc::new(MaxTurnsOperation::new(self.setup.max_turns))),
                Step::Operation(Arc::new(StoryworldPrompt { parts: self.prompt_parts() })),
                Step::Inference(Arc::new(InferenceRunner::new(self.provider.clone(), model).with_request_preparer(preparer))),
            ],
            cancel.clone(),
        );
        let (tx, mut rx) = mpsc::unbounded_channel();
        let emit = Emitter::new(tx, cancel);
        tokio::spawn(async move { while rx.recv().await.is_some() {} });
        machine.run(&*self.runtime, "storyworld", &emit).await?;
        Ok(())
    }

    /// One JSON receipt for a run: answer, every tool call and its outcome, worlds and families touched
    /// with the last validator status the tools reported, usage, and an OpenAI-style transcript.
    pub fn receipt(&self, prompt: &str, started: Instant, error: Option<String>) -> Value {
        let conversation = self.runtime.conversation();
        let mut calls = Vec::new();
        let mut worlds: BTreeMap<String, Value> = BTreeMap::new();
        let mut families: BTreeMap<String, Value> = BTreeMap::new();
        let mut skills_loaded = BTreeSet::new();
        let (mut writes, mut refused) = (0, 0);
        for message in conversation.iter() {
            for content in &message.content {
                let MessageContent::ToolRequest(request) = content else { continue };
                let (name, arguments) = match &request.tool_call {
                    Ok(call) => (call.name.to_string(), json!(call.arguments.clone().unwrap_or_default())),
                    Err(error) => (String::new(), json!({"error": error.message})),
                };
                let response = conversation.iter().flat_map(|m| m.content.iter()).find_map(|c| match c {
                    MessageContent::ToolResponse(response) if response.id == request.id => Some(response),
                    _ => None,
                });
                let ok = response.map(|r| matches!(&r.tool_result, Ok(result) if result.is_error != Some(true)));
                let structured = response.and_then(|r| r.tool_result.as_ref().ok()).and_then(|r| r.structured_content.clone());
                let writes_tool = name != LOAD_SKILL && !self.tools.read_only.contains(&name);
                if writes_tool {
                    if ok == Some(true) {
                        writes += 1;
                    } else {
                        refused += 1;
                    }
                }
                if let Some(world) = arguments.get("world").and_then(Value::as_str) {
                    let entry = worlds.entry(world.to_string()).or_insert_with(|| json!({"calls": 0}));
                    entry["calls"] = json!(entry["calls"].as_i64().unwrap_or(0) + 1);
                    if let Some(valid) = structured.as_ref().and_then(|s| s.get("valid")).and_then(Value::as_bool) {
                        entry["valid"] = json!(valid);
                    }
                    if name == "world_quality" && ok == Some(true) {
                        if let Some(s) = &structured {
                            entry["quality"] = json!({"pass": s["pass"], "checks_passed": s["checks_passed"], "checks_total": s["checks_total"]});
                        }
                    }
                }
                if let Some(family) = arguments.get("family").and_then(Value::as_str) {
                    if ok == Some(true) {
                        if let Some(s) = &structured {
                            let entry = families.entry(family.to_string()).or_insert_with(|| json!({}));
                            for key in ["items", "accepted", "baselines", "score", "frozen"] {
                                if !s[key].is_null() {
                                    entry[key] = s[key].clone();
                                }
                            }
                        }
                    }
                }
                if name == LOAD_SKILL {
                    if let Some(skill) = arguments.get("name").and_then(Value::as_str) {
                        skills_loaded.insert(skill.to_string());
                    }
                }
                calls.push(json!({"id": request.id, "name": name, "arguments": arguments, "ok": ok,
                                  "result": response.map(result_text)}));
            }
        }
        let answer = conversation
            .iter()
            .filter(|m| effective_role(m) == EffectiveRole::Assistant && m.is_user_visible())
            .map(|m| m.as_concat_text())
            .filter(|text| !text.trim().is_empty())
            .last()
            .unwrap_or_default();
        let usage = self.runtime.usage.lock().unwrap().clone();
        json!({
            "app": "storyworld", "version": env!("CARGO_PKG_VERSION"), "gdk": GDK,
            "servedModel": self.setup.served_model, "baseUrl": self.setup.base_url, "mode": self.setup.mode.as_str(),
            "toolMode": self.setup.tool_mode.as_str(), "approve": self.setup.policy.as_str(),
            "contextTokens": self.setup.context_tokens, "keepResults": self.setup.keep_results,
            "prompt": prompt, "answer": answer, "toolCalls": calls, "writes": writes, "refusedCalls": refused,
            "worlds": worlds, "families": families, "skillsLoaded": skills_loaded,
            "inferenceCalls": usage.len(),
            "inputTokens": usage.iter().filter_map(|u| u.usage.input_tokens).sum::<i64>(),
            "maxInputTokens": usage.iter().filter_map(|u| u.usage.input_tokens).max(),
            "outputTokens": usage.iter().filter_map(|u| u.usage.output_tokens).sum::<i64>(),
            "seconds": started.elapsed().as_secs_f64(), "error": error,
            "transcript": transcript(&self.system_prompt(), &conversation),
        })
    }
}

/// The conversation as OpenAI-style chat messages, the shape adapter trainers read.
pub fn transcript(system: &str, conversation: &Conversation) -> Vec<Value> {
    let mut out = vec![json!({"role": "system", "content": system})];
    for message in conversation.iter() {
        if !message.is_agent_visible() {
            continue;
        }
        let mut text = String::new();
        let mut calls = Vec::new();
        let mut responses = Vec::new();
        for content in &message.content {
            match content {
                MessageContent::ToolRequest(request) => {
                    if let Ok(call) = &request.tool_call {
                        let arguments = serde_json::to_string(&call.arguments.clone().unwrap_or_default()).unwrap_or_default();
                        calls.push(json!({"id": request.id, "type": "function",
                                          "function": {"name": call.name, "arguments": arguments}}));
                    }
                }
                MessageContent::ToolResponse(response) => {
                    responses.push(json!({"role": "tool", "tool_call_id": response.id, "content": result_text(response)}));
                }
                other => {
                    if let Some(chunk) = other.as_text() {
                        text.push_str(chunk);
                    }
                }
            }
        }
        if !responses.is_empty() {
            out.extend(responses);
            continue;
        }
        if text.trim().is_empty() && calls.is_empty() {
            continue;
        }
        let role = if effective_role(message) == EffectiveRole::Assistant { "assistant" } else { "user" };
        let mut entry = json!({"role": role, "content": text});
        if !calls.is_empty() {
            entry["tool_calls"] = json!(calls);
        }
        out.push(entry);
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use rmcp::model::CallToolRequestParams;

    fn conversation_with_results(lengths: &[usize]) -> Conversation {
        let mut conversation = Conversation::empty();
        conversation.push(Message::user().with_text("start"));
        for (i, len) in lengths.iter().enumerate() {
            let id = format!("call_{i}");
            conversation.push(
                Message::assistant().with_content(MessageContent::tool_request(id.clone(), Ok(CallToolRequestParams::new("encounter_card")))),
            );
            conversation.push(Message::user().with_content(MessageContent::tool_response(
                id,
                Ok(CallToolResult::success(vec![ContentBlock::text("x".repeat(*len))])),
            )));
        }
        conversation
    }

    fn texts(conversation: &Conversation) -> Vec<String> {
        conversation
            .iter()
            .flat_map(|m| m.content.iter())
            .filter_map(|c| match c {
                MessageContent::ToolResponse(r) => Some(result_text(r)),
                _ => None,
            })
            .collect()
    }

    #[test]
    fn keeps_the_newest_long_results_and_short_ones() {
        let elided = texts(&elide_old_results(&conversation_with_results(&[900, 50, 900, 900]), 2));
        assert!(elided[0].starts_with("[earlier encounter_card result elided"));
        assert_eq!(elided[1].len(), 50);
        assert_eq!(elided[2].len(), 900);
        assert_eq!(elided[3].len(), 900);
    }

    #[test]
    fn nothing_to_elide_returns_the_same_results() {
        let original = conversation_with_results(&[900, 900]);
        assert_eq!(texts(&elide_old_results(&original, 2)), texts(&original));
    }
}
