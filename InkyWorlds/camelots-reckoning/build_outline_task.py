"""Plumbing only: build the one planning prompt that asks the teacher for the
campaign outline (cast, 11 endings, branch budget). No story content authored here.
"""
import json
from pathlib import Path

RUN = Path(__file__).parent
ticket = json.loads((RUN / "outline_ticket.json").read_text(encoding="utf-8"))

prompt = f"""You are the teacher in a DataGoblin AGN-04 storyworld-authoring pipeline, acting as \
the lead designer for one campaign. Everything you write is a PROPOSAL the operator will review \
before any encounter is generated against it.

TICKET:
{json.dumps(ticket, indent=2)}

Produce a single JSON object with exactly these top-level keys: "cast", "setting", "endings", \
"branch_outline", "design_note" -- matching the shapes described in the ticket's \
"requested_output". "endings" must be a JSON array of exactly 11 objects. "branch_outline" must \
be an object with keys "trunk" (an object with "description" and "encounter_budget") and \
"branches" (a JSON array of exactly 11 objects, each with "ending_id" matching one endings[].\
ending_id, "throughline", and "encounter_budget"). The trunk's encounter_budget plus the sum of \
all 11 branch encounter_budgets must equal 300. Reply with the JSON object only, no surrounding \
prose.
"""

(RUN / "outline_task.txt").write_text(prompt, encoding="utf-8")
print(f"wrote {RUN / 'outline_task.txt'} ({len(prompt)} chars)")
