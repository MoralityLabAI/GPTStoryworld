"""Interactive or reproducible public-only Cairo hyperworld play session."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from hyperworld_engine import ACTIONS, CairoHyperworld

DEFAULT_ACTIONS=("brief","audit","brief","charter","audit","charter","charter")


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed",type=int,default=17)
    p.add_argument("--auto",action="store_true",help="run preregistered demonstration choices")
    p.add_argument("--out",type=Path,help="write public-only JSONL turn trace")
    args=p.parse_args()
    game=CairoHyperworld(args.seed)
    trace=[]
    for turn in range(7):
        before=game.view()
        print(f"\n{turn+1}/7: {before['encounter']['title']}")
        print(before['encounter']['text'])
        print(f"Posterior entropy {before['posterior_entropy_bits']:.3f} bits over 1,024 possible states")
        print("Selected first-order beliefs (Nūr's estimates; -1 to +1):")
        for belief in before['first_order_and_second_order_beliefs']['first_order'][:4]:
            print(f"  {belief['target']}: {belief['pValue']:+.2f}")
        print("Nested beliefs (Nūr's estimated alignment between two officials):")
        for belief in before['first_order_and_second_order_beliefs']['second_order'][:2]:
            print(f"  {belief['believer']} about {belief['target']}: {belief['p2Value']:+.2f}")
        for j,choice in enumerate(before["choices"],1):
            print(f" {j}. {choice['text']}")
        if args.auto: action=DEFAULT_ACTIONS[turn]
        else:
            raw=input("Choice (1-3): ").strip()
            if raw not in ("1","2","3"): raise SystemExit("invalid choice")
            action=ACTIONS[int(raw)-1]
        after=game.step(action)
        event=after["seen_evidence"][-1]
        print(f"Nūr chose {action}. {event['title']}; evidence bit={event['observed_parity']}.")
        print(f"Source root={event['source_root']}, new independent evidence={event['counted_as_independent']}")
        trace.append({"turn":turn,"action":action,"before":before,"after":after})
    print("\nOfficial ending:",game.ending.replace("_"," "))
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text("".join(json.dumps(z,sort_keys=True)+"\n" for z in trace),encoding="utf-8")
        print("Public-only log:",args.out)

if __name__=="__main__":main()
