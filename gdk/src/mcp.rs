//! The Storyworld MCP server (`python -m storyworld_mcp.server`) as a goose-agent tool provider. The
//! client speaks newline-delimited JSON-RPC 2.0 over the server's stdio, like Data Goblin (`DataGoblin
//! gdk/src/mcp.rs`) and the goblin GDK apps in HybridTRMLDT `MCP/goose_gdk_app`.

use std::collections::HashSet;
use std::path::{Path, PathBuf};
use std::sync::Arc;

use anyhow::{anyhow, bail, Context, Result};
use async_trait::async_trait;
use goose_agent::operation::Emitter;
use goose_agent::tool::ToolProvider;
use rmcp::model::{CallToolRequestParams, CallToolResult, ErrorData, Tool};
use serde_json::{json, Value};
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader, Lines};
use tokio::process::{Child, ChildStdin, ChildStdout, Command};
use tokio::sync::Mutex;

pub struct McpClient {
    _child: Child,
    stdin: ChildStdin,
    stdout: Lines<BufReader<ChildStdout>>,
    next_id: i64,
    pub instructions: String,
}

impl McpClient {
    /// Start the server and complete the initialize handshake. Its stdin is a pipe, never ours.
    pub async fn spawn(program: &str, args: &[String], cwd: &Path, env: &[(String, String)]) -> Result<Self> {
        let mut command = Command::new(program);
        command
            .args(args)
            .current_dir(cwd)
            .envs(env.iter().map(|(k, v)| (k.as_str(), v.as_str())))
            .stdin(std::process::Stdio::piped())
            .stdout(std::process::Stdio::piped())
            .stderr(std::process::Stdio::inherit())
            .kill_on_drop(true);
        let mut child = command
            .spawn()
            .with_context(|| format!("mcp_start_error: spawning {program} in {}", cwd.display()))?;
        let stdin = child.stdin.take().ok_or_else(|| anyhow!("MCP server has no stdin"))?;
        let stdout = BufReader::new(child.stdout.take().ok_or_else(|| anyhow!("MCP server has no stdout"))?).lines();
        let mut client = Self { _child: child, stdin, stdout, next_id: 0, instructions: String::new() };
        let init = client
            .request(
                "initialize",
                json!({"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "storyworld", "version": env!("CARGO_PKG_VERSION")}}),
            )
            .await
            .context("mcp_start_error: initialize (is --root a GPTStoryworld checkout and --python Python 3.11+?)")?;
        client.instructions = init["instructions"].as_str().unwrap_or_default().to_string();
        client.send(json!({"jsonrpc": "2.0", "method": "notifications/initialized"})).await?;
        Ok(client)
    }

    async fn send(&mut self, message: Value) -> Result<()> {
        let mut line = serde_json::to_vec(&message)?;
        line.push(b'\n');
        self.stdin.write_all(&line).await?;
        self.stdin.flush().await?;
        Ok(())
    }

    pub async fn request(&mut self, method: &str, params: Value) -> Result<Value> {
        self.next_id += 1;
        let id = self.next_id;
        self.send(json!({"jsonrpc": "2.0", "id": id, "method": method, "params": params})).await?;
        while let Some(line) = self.stdout.next_line().await? {
            let Ok(message) = serde_json::from_str::<Value>(&line) else { continue };
            if message.get("id").and_then(Value::as_i64) == Some(id) {
                if let Some(error) = message.get("error") {
                    bail!("MCP error from {method}: {error}");
                }
                return Ok(message["result"].clone());
            }
        }
        bail!("MCP server closed its output")
    }
}

/// Which tools the server lists, from the skill being run.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Mode {
    Builder,
    Small,
    Hypergames,
    All,
}

impl Mode {
    pub fn parse(raw: &str) -> Option<Self> {
        match raw {
            "builder" => Some(Self::Builder),
            "small" => Some(Self::Small),
            "hypergames" => Some(Self::Hypergames),
            "all" => Some(Self::All),
            _ => None,
        }
    }
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Builder => "builder",
            Self::Small => "small",
            Self::Hypergames => "hypergames",
            Self::All => "all",
        }
    }
    /// The mode a skill runs in.
    pub fn for_skill(skill: &str) -> Option<Self> {
        match skill {
            "storyworld-builder" => Some(Self::Builder),
            "small-storyworld" => Some(Self::Small),
            "hypergames" => Some(Self::Hypergames),
            _ => None,
        }
    }
}

/// How to start the Storyworld server.
pub struct ServerSpec {
    pub python: String,
    pub root: PathBuf,
    pub work: PathBuf,
    pub mode: Mode,
    pub card_budget: usize,
    pub read_budget: usize,
    pub read_only: bool,
    /// Repository paths no tool may read (a bench task's grading-only files).
    pub deny: Vec<String>,
}

/// The Storyworld tools, listed once at connect time.
pub struct StoryworldTools {
    client: Mutex<McpClient>,
    pub tools: Vec<Tool>,
    pub read_only: HashSet<String>,
    pub instructions: String,
}

impl StoryworldTools {
    pub async fn connect(spec: &ServerSpec) -> Result<Arc<Self>> {
        let gdk = spec.root.join("gdk");
        if !gdk.join("storyworld_mcp").join("server.py").is_file() {
            bail!("mcp_start_error: {} is not a GPTStoryworld checkout with gdk/storyworld_mcp", spec.root.display());
        }
        let mut args = vec![
            "-m".to_string(),
            "storyworld_mcp.server".to_string(),
            "--root".to_string(),
            spec.root.display().to_string(),
            "--work".to_string(),
            spec.work.display().to_string(),
            "--mode".to_string(),
            spec.mode.as_str().to_string(),
            "--card-budget".to_string(),
            spec.card_budget.to_string(),
            "--read-budget".to_string(),
            spec.read_budget.to_string(),
        ];
        if spec.read_only {
            args.push("--read-only".to_string());
        }
        for path in &spec.deny {
            args.extend(["--deny".to_string(), path.clone()]);
        }
        let separator = if cfg!(windows) { ";" } else { ":" };
        let mut python_path = gdk.display().to_string();
        if let Ok(existing) = std::env::var("PYTHONPATH") {
            if !existing.is_empty() {
                python_path = format!("{python_path}{separator}{existing}");
            }
        }
        let env = vec![("PYTHONPATH".to_string(), python_path), ("PYTHONIOENCODING".to_string(), "utf-8".to_string())];
        let mut client = McpClient::spawn(&spec.python, &args, &spec.root, &env).await?;
        let listed = client.request("tools/list", json!({})).await.context("mcp_start_error: tools/list")?;
        let raw = listed["tools"].as_array().cloned().unwrap_or_default();
        let read_only = raw
            .iter()
            .filter(|tool| tool["annotations"]["readOnlyHint"].as_bool() == Some(true))
            .filter_map(|tool| tool["name"].as_str().map(str::to_string))
            .collect();
        let tools: Vec<Tool> = serde_json::from_value(Value::Array(raw)).context("mcp_start_error: tool list")?;
        let instructions = client.instructions.clone();
        Ok(Arc::new(Self { client: Mutex::new(client), tools, read_only, instructions }))
    }

    pub fn names(&self) -> HashSet<String> {
        self.tools.iter().map(|tool| tool.name.to_string()).collect()
    }

    /// Call a tool directly (outside the agent loop) and return its structured content.
    pub async fn call_json(&self, name: &str, arguments: Value) -> Result<Value> {
        let raw = self.client.lock().await.request("tools/call", json!({"name": name, "arguments": arguments})).await?;
        if raw["isError"].as_bool() == Some(true) {
            bail!("{name} failed: {}", raw["structuredContent"]);
        }
        Ok(raw["structuredContent"].clone())
    }
}

#[async_trait]
impl<S: Send + Sync + 'static> ToolProvider<S> for StoryworldTools {
    async fn tools(&self, _session: &S) -> Result<Vec<Tool>> {
        Ok(self.tools.clone())
    }

    async fn call(&self, _session: &S, _request_id: &str, call: CallToolRequestParams, _emit: &Emitter) -> Result<CallToolResult, ErrorData> {
        let arguments = call.arguments.map(Value::Object).unwrap_or_else(|| json!({}));
        let raw = self
            .client
            .lock()
            .await
            .request("tools/call", json!({"name": call.name, "arguments": arguments}))
            .await
            .map_err(|error| ErrorData::internal_error(format!("tool_call_error: {error:#}"), None))?;
        serde_json::from_value(raw)
            .map_err(|error| ErrorData::internal_error(format!("tool_call_error: unreadable result: {error}"), None))
    }
}
