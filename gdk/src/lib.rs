//! Storyworld, a Goose GDK app for GPTStoryworld.
//!
//! A goose-agent state machine drives a local model through one of three GDK skills: `storyworld-builder`
//! (whole-world authoring for large-context models), `small-storyworld` (one encounter at a time inside an
//! 8K packet budget) and `hypergames` (exact-graded eval families for frontier models). The Storyworld MCP
//! server (`python -m storyworld_mcp.server`, in `gdk/storyworld_mcp`) owns the worlds, the SweepWeave
//! validator, the quality gate, rehearsal and the hyperworld engine; the skill picks the server's tool mode.

pub mod agent;
pub mod mcp;
pub mod skills;
pub mod text_tools;
