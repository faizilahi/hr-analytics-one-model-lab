import json, sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from grain import hris_count, one_definition
DATA, OUT = ROOT / "data", ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)

def main():
    hris = pd.read_csv(DATA / "hris_snapshot.csv")
    pay = pd.read_csv(DATA / "payroll_sept.csv")
    leavers = int(hris["termination_date"].notna().sum())
    summary = {
        "hris_headcount": hris_count(hris),
        "payroll_headcount": int(len(pay)),
        "leavers_still_on_hris": leavers,
        "one_definition_headcount": one_definition(hris),
    }
    pd.DataFrame([summary]).to_csv(OUT / "headcount_reconcile.csv", index=False)
    print(json.dumps(summary, indent=2))
if __name__ == "__main__":
    main()
