//! storyworld: the Storyworld GDK app.
//!
//!   storyworld run (--prompt TEXT | --skill NAME [--args TEXT]) [options]
//!   storyworld skills [--root DIR] [--skills-dir DIR]...
//!   storyworld tools [--mode MODE] [options]
//!   storyworld bench --track builder|small|hypergames [--split dev|test] [--limit N] [--task ID]... [options]
//!
//! `--skill storyworld-builder | small-storyworld | hypergames` picks the server's tool mode and the
//! context defaults for that skill; `--mode` overrides it. Each run prints one JSON receipt and appends
//! it to `--receipts` (default `<work>/receipts.jsonl`).
//!
//! `bench` runs StoryworldBench tasks (`python -m benchmarks.storyworld_bench`) through the app: each task gets a
//! fresh workspace and a server that refuses the task's grading-only files; builder tasks run the
//! storyworld-builder skill and are scored on the world they leave in the workspace, the other tracks are
//! scored on the final answer. Results go to `<work>/bench/<track>-<split>/`.

use std::io::Write;
use std::path::PathBuf;
use std::sync::Arc;
use std::time::{Duration, Instant};

use anyhow::{anyhow, bail, Result};
use serde_json::{json, Value};
use storyworld_gdk::agent::{Agent, AgentSetup, ApprovePolicy, ToolMode};
use storyworld_gdk::mcp::{Mode, ServerSpec, StoryworldTools};
use storyworld_gdk::skills::SkillSet;
use tokio_util::sync::CancellationToken;

const USAGE: &str = "usage: storyworld (run (--prompt TEXT | --skill NAME [--args TEXT]) | skills | tools | bench --track T \
[--split dev|test] [--limit N] [--task ID]... [--confirm-one-shot]) [--root DIR] \
[--python PY] [--base-url URL] [--model ID] [--mode builder|small|hypergames|all] [--tool-mode native|text] \
[--approve read-only|write] [--max-turns N] [--max-tokens N] [--context N] [--card-budget N] [--read-budget N] \
[--keep-results N|all] [--temperature F] [--timeout-secs N] [--work DIR] [--receipts FILE] [--skills-dir DIR]...";

/// Context defaults per mode: (context tokens, max output tokens, card budget, read budget, newest long results kept).
fn defaults(mode: Mode) -> (usize, i32, usize, usize, Option<usize>) {
    match mode {
        Mode::Small => (8192, 1024, 2500, 6000, Some(2)),
        Mode::Builder => (65536, 8192, 6144, 40000, None),
        Mode::Hypergames => (32768, 4096, 6144, 24000, None),
        Mode::All => (32768, 4096, 6144, 24000, None),
    }
}

struct Args {
    command: String,
    root: PathBuf,
    python: String,
    base_url: String,
    model: String,
    mode: Option<Mode>,
    tool_mode: ToolMode,
    approve: ApprovePolicy,
    max_turns: u32,
    max_tokens: Option<i32>,
    context: Option<usize>,
    card_budget: Option<usize>,
    read_budget: Option<usize>,
    keep_results: Option<Option<usize>>,
    temperature: f32,
    timeout_secs: u64,
    work: Option<PathBuf>,
    receipts: Option<PathBuf>,
    skills_dirs: Vec<PathBuf>,
    prompt: Option<String>,
    skill: Option<String>,
    skill_args: String,
    track: Option<String>,
    split: String,
    limit: Option<usize>,
    task_ids: Vec<String>,
    confirm_one_shot: bool,
}

fn env_or(name: &str, default: &str) -> String {
    std::env::var(name).ok().filter(|v| !v.is_empty()).unwrap_or_else(|| default.to_string())
}

fn loopback(url: &str) -> bool {
    ["http://127.0.0.1:", "http://localhost:", "http://[::1]:"].iter().any(|prefix| url.starts_with(prefix))
}

fn parse_args() -> Result<Args> {
    let mut raw = std::env::args().skip(1).peekable();
    let command = match raw.peek().map(String::as_str) {
        Some("run" | "skills" | "tools" | "bench") => raw.next().unwrap(),
        Some("--help" | "-h") | None => bail!("{USAGE}"),
        Some(_) => "run".to_string(),
    };
    let mut args = Args {
        command,
        root: PathBuf::from(env_or("STORYWORLD_ROOT", ".")),
        python: env_or("STORYWORLD_PYTHON", "python"),
        base_url: env_or("STORYWORLD_BASE_URL", "http://127.0.0.1:18090/v1"),
        model: env_or("STORYWORLD_MODEL", "inkling-2-mini"),
        mode: None,
        tool_mode: ToolMode::Native,
        approve: ApprovePolicy::Write,
        max_turns: 40,
        max_tokens: None,
        context: None,
        card_budget: None,
        read_budget: None,
        keep_results: None,
        temperature: 0.2,
        timeout_secs: 900,
        work: None,
        receipts: None,
        skills_dirs: Vec::new(),
        prompt: None,
        skill: None,
        skill_args: String::new(),
        track: None,
        split: "dev".to_string(),
        limit: None,
        task_ids: Vec::new(),
        confirm_one_shot: false,
    };
    while let Some(flag) = raw.next() {
        let mut value = || raw.next().ok_or_else(|| anyhow!("{flag} needs a value"));
        match flag.as_str() {
            "--root" => args.root = PathBuf::from(value()?),
            "--python" => args.python = value()?,
            "--base-url" => args.base_url = value()?,
            "--model" => args.model = value()?,
            "--mode" => {
                let raw = value()?;
                args.mode = Some(Mode::parse(&raw).ok_or_else(|| anyhow!("--mode {raw}: builder, small, hypergames or all"))?);
            }
            "--tool-mode" => {
                args.tool_mode = match value()?.as_str() {
                    "native" => ToolMode::Native,
                    "text" => ToolMode::Text,
                    other => bail!("--tool-mode {other}: native or text"),
                }
            }
            "--approve" => {
                let raw = value()?;
                args.approve = ApprovePolicy::parse(&raw).ok_or_else(|| anyhow!("--approve {raw}: read-only or write"))?;
            }
            "--max-turns" => args.max_turns = value()?.parse()?,
            "--max-tokens" => args.max_tokens = Some(value()?.parse()?),
            "--context" => args.context = Some(value()?.parse()?),
            "--card-budget" => args.card_budget = Some(value()?.parse()?),
            "--read-budget" => args.read_budget = Some(value()?.parse()?),
            "--keep-results" => {
                let raw = value()?;
                args.keep_results = Some(if raw == "all" { None } else { Some(raw.parse()?) });
            }
            "--temperature" => args.temperature = value()?.parse()?,
            "--timeout-secs" => args.timeout_secs = value()?.parse()?,
            "--work" => args.work = Some(PathBuf::from(value()?)),
            "--receipts" => args.receipts = Some(PathBuf::from(value()?)),
            "--skills-dir" => args.skills_dirs.push(PathBuf::from(value()?)),
            "--prompt" => args.prompt = Some(value()?),
            "--skill" => args.skill = Some(value()?),
            "--args" => args.skill_args = value()?,
            "--track" => args.track = Some(value()?),
            "--split" => args.split = value()?,
            "--limit" => args.limit = Some(value()?.parse()?),
            "--task" => args.task_ids.push(value()?),
            "--confirm-one-shot" => args.confirm_one_shot = true,
            "--help" | "-h" => bail!("{USAGE}"),
            other => bail!("unknown flag {other}\n{USAGE}"),
        }
    }
    args.root = std::fs::canonicalize(&args.root).map_err(|e| anyhow!("--root {}: {e}", args.root.display()))?;
    if args.skills_dirs.is_empty() {
        args.skills_dirs.push(args.root.join("gdk").join("skills"));
    }
    if !loopback(&args.base_url) {
        bail!("{}: Storyworld talks to local model servers only (http://127.0.0.1:PORT/v1)", args.base_url);
    }
    if !args.base_url.ends_with('/') {
        args.base_url.push('/');
    }
    if args.command == "run" && args.prompt.is_none() && args.skill.is_none() {
        bail!("run needs --prompt or --skill\n{USAGE}");
    }
    if args.command == "bench" {
        match args.track.as_deref() {
            Some("builder" | "small" | "hypergames") => {}
            _ => bail!("bench needs --track builder, small or hypergames\n{USAGE}"),
        }
        if !matches!(args.split.as_str(), "dev" | "test") {
            bail!("--split {}: dev or test", args.split);
        }
        if args.split == "test" && !args.confirm_one_shot {
            bail!("the test split is for one-shot reporting; pass --confirm-one-shot to run it");
        }
    }
    if let (None, Some(skill)) = (args.mode, &args.skill) {
        args.mode = Some(Mode::for_skill(skill).ok_or_else(|| anyhow!("--skill {skill} has no default mode; pass --mode"))?);
    }
    Ok(args)
}

fn mode(args: &Args) -> Mode {
    args.mode.unwrap_or(Mode::All)
}

fn work_dir(args: &Args) -> PathBuf {
    args.work.clone().unwrap_or_else(|| args.root.join("gdk").join("work"))
}

async fn connect(args: &Args, mode: Mode, work: PathBuf, deny: Vec<String>) -> Result<Arc<StoryworldTools>> {
    let (_, _, card, read, _) = defaults(mode);
    StoryworldTools::connect(&ServerSpec {
        python: args.python.clone(),
        root: args.root.clone(),
        work,
        mode,
        card_budget: args.card_budget.unwrap_or(card),
        read_budget: args.read_budget.unwrap_or(read),
        read_only: args.approve == ApprovePolicy::ReadOnly,
        deny,
    })
    .await
}

fn setup(args: &Args, mode: Mode) -> AgentSetup {
    let (context, max_tokens, _, _, keep) = defaults(mode);
    AgentSetup {
        base_url: args.base_url.clone(),
        served_model: args.model.clone(),
        tool_mode: args.tool_mode,
        mode,
        context_tokens: args.context.unwrap_or(context),
        max_tokens: args.max_tokens.unwrap_or(max_tokens),
        max_turns: args.max_turns,
        temperature: args.temperature,
        policy: args.approve,
        timeout: Duration::from_secs(args.timeout_secs),
        keep_results: args.keep_results.unwrap_or(keep),
    }
}

fn append_receipt(args: &Args, receipt: &Value) -> Result<()> {
    let path = args.receipts.clone().unwrap_or_else(|| work_dir(args).join("receipts.jsonl"));
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut file = std::fs::OpenOptions::new().create(true).append(true).open(&path)?;
    writeln!(file, "{receipt}")?;
    Ok(())
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = parse_args()?;
    let skills = Arc::new(SkillSet::discover(&args.skills_dirs));
    if args.command == "skills" {
        for skill in &skills.entries {
            println!(
                "{}",
                json!({"name": skill.name, "description": skill.description, "path": skill.path,
                       "mode": Mode::for_skill(&skill.name).map(Mode::as_str), "supportingFiles": skill.supporting_files.len()})
            );
        }
        return Ok(());
    }
    if args.command == "bench" {
        std::process::exit(bench(&args, skills).await?);
    }
    let tools = connect(&args, mode(&args), work_dir(&args), Vec::new()).await?;
    if args.command == "tools" {
        let mut names: Vec<String> = tools.names().into_iter().collect();
        names.sort();
        let agent_setup = setup(&args, mode(&args));
        println!(
            "{}",
            json!({"mode": mode(&args).as_str(), "tools": names, "readOnly": tools.read_only, "skills": skills.names(),
                   "approve": args.approve.as_str(), "contextTokens": agent_setup.context_tokens,
                   "maxTokens": agent_setup.max_tokens, "keepResults": agent_setup.keep_results,
                   "instructions": tools.instructions})
        );
        return Ok(());
    }
    let prompt = match (&args.prompt, &args.skill) {
        (Some(prompt), _) => prompt.clone(),
        (None, Some(skill)) => format!("/{skill} {}", args.skill_args).trim_end().to_string(),
        (None, None) => unreachable!(),
    };
    let started = Instant::now();
    let agent = Agent::new(setup(&args, mode(&args)), tools, skills)?;
    agent.push_user(&prompt);
    let error = agent.run(CancellationToken::new()).await.err().map(|e| format!("agent_error: {e:#}"));
    let receipt = agent.receipt(&prompt, started, error);
    append_receipt(&args, &receipt)?;
    println!("{receipt}");
    std::process::exit(if receipt["error"].is_string() { 1 } else { 0 });
}

// ---- bench ----

/// Run the bench CLI in the checkout and return its stdout.
fn bench_cli(args: &Args, cli_args: &[&str]) -> Result<String> {
    let output = std::process::Command::new(&args.python)
        .args(["-m", "benchmarks.storyworld_bench"])
        .args(cli_args)
        .current_dir(&args.root)
        .env("PYTHONIOENCODING", "utf-8")
        .output()
        .map_err(|e| anyhow!("bench_error: running {} -m benchmarks.storyworld_bench: {e}", args.python))?;
    if !output.status.success() {
        bail!("bench_error: {cli_args:?} exited {}: {}", output.status, String::from_utf8_lossy(&output.stderr).trim());
    }
    Ok(String::from_utf8_lossy(&output.stdout).into_owned())
}

/// The message a bench task starts with. Builder tasks run the storyworld-builder skill on a workspace world;
/// small and hypergames tasks are answered directly (their skills author worlds and eval families, which these
/// tasks do not ask for), with that mode's tools available.
fn bench_prompt(task: &Value) -> String {
    let prompt = task["prompt"].as_str().unwrap_or_default();
    if task["track"] != json!("builder") {
        return format!("{prompt}\n\nReply with the artifact only, in this format: {}.", task["answer_format"].as_str().unwrap_or("JSON"));
    }
    let start = match task["inputs"]["world"].as_str() {
        Some(path) => format!("world_import `{path}` as world `bench`"),
        None => "create world `bench` with world_new".to_string(),
    };
    format!(
        "/storyworld-builder bench {prompt}\n\n---\nStoryworld app instructions for this benchmark task: do not print \
         the JSON. First {start}, then edit it with the tools until the requirements above hold, checking with \
         world_validate, world_quality and world_rehearse. The scorer reads world `bench` from the workspace. \
         When you are done, reply DONE."
    )
}

async fn bench(args: &Args, skills: Arc<SkillSet>) -> Result<i32> {
    let track = args.track.clone().unwrap_or_default();
    let listing = bench_cli(args, &["tasks", "--track", &track, "--split", &args.split])?;
    let mut tasks: Vec<Value> =
        listing.lines().filter(|l| !l.trim().is_empty()).map(serde_json::from_str).collect::<Result<_, _>>()?;
    if !args.task_ids.is_empty() {
        tasks.retain(|t| args.task_ids.iter().any(|id| t["task_id"] == json!(id)));
    }
    if let Some(limit) = args.limit {
        tasks.truncate(limit);
    }
    if tasks.is_empty() {
        bail!("bench_error: no {track} tasks matched (split {})", args.split);
    }
    let run_dir = work_dir(args).join("bench").join(format!("{track}-{}", args.split));
    std::fs::create_dir_all(&run_dir)?;
    let results_path = run_dir.join("results.jsonl");
    let mut results = std::fs::File::create(&results_path)?;
    let (mut total, mut passed) = (0.0, 0);
    for task in &tasks {
        let task_id = task["task_id"].as_str().unwrap_or_default().to_string();
        let skill = task["skill"].as_str().unwrap_or_default();
        let task_mode = Mode::for_skill(skill).unwrap_or(Mode::All);
        let task_dir = run_dir.join(task_id.replace(['/', '\\', ':'], "_"));
        if task_dir.exists() {
            std::fs::remove_dir_all(&task_dir)?;
        }
        std::fs::create_dir_all(&task_dir)?;
        let deny: Vec<String> =
            task["grading_only"].as_array().into_iter().flatten().filter_map(|p| p.as_str().map(str::to_string)).collect();
        let tools = connect(args, task_mode, task_dir.join("work"), deny).await?;
        let mut task_setup = setup(args, task_mode);
        if let Some(budget) = task["budget_tokens"].as_i64() {
            task_setup.max_tokens = task_setup.max_tokens.max(budget as i32);
        }
        let prompt = bench_prompt(task);
        let started = Instant::now();
        let agent = Agent::new(task_setup, tools, skills.clone())?;
        agent.push_user(&prompt);
        let error = agent.run(CancellationToken::new()).await.err().map(|e| format!("agent_error: {e:#}"));
        let receipt = agent.receipt(&prompt, started, error);
        std::fs::write(task_dir.join("receipt.json"), serde_json::to_vec_pretty(&receipt)?)?;
        let world = task_dir.join("work").join("worlds").join("bench").join("storyworld.json");
        let artifact = if track == "builder" && world.is_file() {
            world
        } else {
            let path = task_dir.join("answer.txt");
            std::fs::write(&path, receipt["answer"].as_str().unwrap_or_default())?;
            path
        };
        let artifact_arg = artifact.display().to_string();
        let scored: Value = serde_json::from_str(&bench_cli(args, &["score", "--task", &task_id, "--artifact", &artifact_arg])?)?;
        total += scored["score"].as_f64().unwrap_or(0.0);
        passed += usize::from(scored["passed"] == json!(true));
        let row = json!({"task_id": task_id, "track": track, "skill": skill, "mode": task_mode.as_str(),
                         "score": scored["score"], "passed": scored["passed"], "checks": scored["checks"],
                         "scoreError": scored["error"], "artifact": artifact_arg,
                         "toolCalls": receipt["toolCalls"].as_array().map(Vec::len), "writes": receipt["writes"],
                         "refusedCalls": receipt["refusedCalls"], "inferenceCalls": receipt["inferenceCalls"],
                         "maxInputTokens": receipt["maxInputTokens"], "outputTokens": receipt["outputTokens"],
                         "seconds": receipt["seconds"], "agentError": receipt["error"]});
        writeln!(results, "{row}")?;
        println!("{}", json!({"task_id": row["task_id"], "score": row["score"], "passed": row["passed"],
                               "toolCalls": row["toolCalls"], "seconds": row["seconds"], "agentError": row["agentError"]}));
    }
    let n = tasks.len();
    let summary = json!({"app": "storyworld", "track": track, "split": args.split, "servedModel": args.model,
                         "baseUrl": args.base_url, "toolMode": args.tool_mode.as_str(), "n": n,
                         "mean_score": total / n as f64, "pass_rate": passed as f64 / n as f64,
                         "results": results_path.display().to_string()});
    std::fs::write(run_dir.join("summary.json"), serde_json::to_vec_pretty(&summary)?)?;
    println!("{summary}");
    Ok(0)
}
