"""FSI-01 audit of the published HG-07 six-seed neural CPU experiment.

Uses only HG-07's public seed-row CSV and frozen registration, never the
private HG-03 seeds. Tests use independent *seed/world* as the sample unit,
not 256 repeated states per seed. H3 is an equivalence claim and receives no
false confirmation from a directional/significance test.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from fractions import Fraction as Q
from pathlib import Path

from spiral_ln.evaluation_finite_sample import (
    signflip_cluster_p, holm_adjust, cluster_bootstrap_ci,
)

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "Hypergames/single_player/hg07_registration_v1.json"
CSV = ROOT / "output/evaluation_hypergames/hg07/hg07_public_seed_rows.csv"


def audit(reg_path: Path = REG, csv_path: Path = CSV) -> dict:
    reg_bytes, csv_bytes = reg_path.read_bytes(), csv_path.read_bytes()
    reg = json.loads(reg_bytes)
    if reg.get("schema") != "HG-07/raw-state-recurrent-v1":
        raise ValueError("unexpected HG-07 registration schema")
    with csv_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    seeds = [str(x) for x in reg["evaluation_seeds"]]
    arms = reg["model_arms"]
    cohorts = reg["cohorts"]
    klist = reg["goal_ranks"]
    budgets = reg["training_sizes"]
    index={}
    for row in rows:
        key=(row["seed"],row["cohort"],int(row["goal_rank"]),int(row["train_n"]),row["arm"])
        if key in index:
            raise ValueError(f"duplicate HG-07 scored row: {key}")
        index[key]=row
    expected={(seed,cohort,k,n,arm) for seed in seeds for cohort in cohorts
              for k in klist for n in budgets for arm in arms}
    if set(index) != expected or len(rows) != 360:
        raise ValueError(f"HG-07 registered census incomplete: {len(rows)} rows, "
                         f"missing={len(expected-set(index))}, extra={len(set(index)-expected)}")
    test_n=reg["test_size"]
    cal_n=reg["calibration_size"]
    if test_n != 256 or cal_n != 256:
        raise ValueError("HG-07 FSI audit assumes frozen 256/256 test/calibration")
    def get(seed: str, cohort: str, k: int, n: int, arm: str) -> dict:
        return index[(seed,cohort,k,n,arm)]
    def count(row: dict, key: str) -> int:
        v=int(row[key])
        if v < 0 or v > test_n:
            raise ValueError(f"invalid {key} count")
        return v

    h1=[];h2=[]
    for seed in seeds:
        flat=get(seed,"core_140",1,2048,"flat_task")
        loop=get(seed,"core_140",1,2048,"loop_task")
        aux=get(seed,"core_140",1,2048,"loop_true_fragment_aux")
        h1.append(count(aux,"composed_test_joint_correct")-
                  count(loop,"direct_test_joint_correct"))
        h2.append(count(loop,"direct_test_joint_correct")-
                  count(flat,"direct_test_joint_correct"))

    def classify(diffs: list[int], gate_positive: int, label: str) -> dict:
        effect=[Q(x,test_n) for x in diffs]
        p,method=signflip_cluster_p(effect)
        ci=cluster_bootstrap_ci(effect,Q(1,20),seed=20261117,resamples=4096)
        return {"name":label,"n_independent_seeds":len(seeds),
                "seed_differences_correct_per_256":diffs,
                "positive_seed_count":sum(x>0 for x in diffs),
                "negative_seed_count":sum(x<0 for x in diffs),
                "tie_seed_count":sum(x==0 for x in diffs),
                "registered_directional_gate":sum(x>0 for x in diffs)>=gate_positive,
                "macro_effect_exact":str(sum(effect,Q(0))/len(effect)),
                "macro_effect_pp":float(100*sum(effect,Q(0))/len(effect)),
                "seed_signflip_p_exact":str(p),"seed_signflip_p":float(p),
                "seed_test":method,
                "descriptive_seed_bootstrap_ci":list(ci) if ci else None,
                "inference_verdict":"inconclusive_six_seeds"}

    h1r=classify(h1,4,"H1 privileged composed vs task-only")
    h2r=classify(h2,4,"H2 tied recurrent vs flat")
    adjusted=holm_adjust([Q(h1r["seed_signflip_p_exact"]),Q(h2r["seed_signflip_p_exact"])])
    h1r["holm_two_superiority_tests"]=float(adjusted[0])
    h2r["holm_two_superiority_tests"]=float(adjusted[1])
    h1r["holm_exact"]=str(adjusted[0]); h2r["holm_exact"]=str(adjusted[1])

    h3={}
    for arm in arms:
        deltas=[count(get(seed,"core_140",1,2048,arm),"direct_test_joint_correct")-
                count(get(seed,"padded_512",1,2048,arm),"direct_test_joint_correct")
                for seed in seeds]
        hits=sum(Q(abs(x),test_n)<Q(1,20) for x in deltas)
        # H3's equivalence claim needs a simultaneous interval strictly inside
        # (-.05,.05). Hoeffding for bounded independent seed differences in
        # [-1,1] gives a two-sided radius sqrt(2 ln(2/alpha)/g).
        # At g=6, alpha=.05, this exceeds 1, hence is uninformative.
        radius=math.sqrt(2*math.log(2/0.05)/len(seeds))
        h3[arm]={"signed_core_minus_padded_correct":deltas,
                 "within_five_pp_seeds":hits,"registered_gate":hits>=4,
                 "empirical_macro_gap_pp":100*sum(deltas)/(len(seeds)*test_n),
                 "hoeffding_95_radius_pp":100*radius,
                 "equivalence_established":False,
                 "inference_note":"Six-seed direction count does not certify population-level equivalence."}

    gf2=[]
    for seed in seeds:
        for cohort in cohorts:
            for k in klist:
                v=get(seed,cohort,k,2048,"linear_task")
                rank=int(v["f2_rank"]); dim=int(v["dimension"])
                determined=int(v["f2_test_determined"])
                correct=int(v["f2_test_correct_if_determined"])
                gf2.append((seed,cohort,k,rank,dim,determined,correct))
    if len(gf2)!=36:
        raise AssertionError("unexpected GF2 cohort count")
    h4=all(rank==dim and determined==test_n and correct==test_n
           for _,_,_,rank,dim,determined,correct in gf2)

    release=[row for row in rows if row["direct_release"]=="1" or row["composed_release"]=="1"]
    release_rows=[{
        "seed":r["seed"],"cohort":r["cohort"],"goal_rank":int(r["goal_rank"]),
        "train_n":int(r["train_n"]),"arm":r["arm"],
        "direct_cal_correct":int(r["direct_cal_joint_correct"]),
        "direct_test_correct":int(r["direct_test_joint_correct"]),
        "direct_false_accept":int(r["direct_false_accept"]),
        "direct_true_utility":r["direct_true_utility"]
    } for r in release]

    return {
        "schema":"fsi01.hypergames.hg07.seed_audit.v1",
        "provenance":"public synthetic development seeds; no pretrained Qwen, narrative Storyworld or private HG03 test",
        "evidence_level":"neural development experiment + exact six-seed signed inference + GF2 structural checks",
        "source_sha256":{
            "registration":hashlib.sha256(reg_bytes).hexdigest(),
            "seed_csv":hashlib.sha256(csv_bytes).hexdigest()},
        "census":{"neural_fits":len(rows),"independent_seed_worlds":len(seeds),
                  "per_seed_test_states":test_n,"correlated_state_outcomes_are_not_new_seeds":True},
        "H1":h1r,"H2":h2r,"H3":h3,
        "H4":{"holds_on_registered_census":h4,"independent_generator_worlds":36,
              "matched_test_outcomes":sum(t[-1] for t in gf2),
              "number_test_outcomes":len(gf2)*test_n,
              "evidence_class":"algebraic_full_rank_parity_prior_with_finite_test_replay"},
        "release_failures":release_rows,
        "claim_boundary":"H2 registered 4/6 direction remains a weak directional PASS; its 6-seed signed p is 0.3125. H3 within-threshold counts are not an equivalence certificate. Neural benchmark uses public synthetic generator; no general storyworld alignment claims.",
    }


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registration",type=Path,default=REG)
    p.add_argument("--seed-csv",type=Path,default=CSV)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=audit(args.registration,args.seed_csv)
    payload=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
