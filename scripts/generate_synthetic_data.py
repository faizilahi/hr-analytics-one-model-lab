from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"; DATA.mkdir(parents=True, exist_ok=True)
rows = []
for i in range(4218):
    term = None
    if i < 45:
        term = "2024-09-12"
    rows.append({"employee_id": f"E{i:05d}", "hr_status": "Active", "termination_date": term,
                 "snapshot_month": "2024-09"})
pd.DataFrame(rows).to_csv(DATA / "hris_snapshot.csv", index=False)
# payroll: exclude terminated
pay = [r for r in rows if r["termination_date"] is None]
pd.DataFrame([{"employee_id": r["employee_id"], "paid_in_month": True} for r in pay]).to_csv(
    DATA / "payroll_sept.csv", index=False)
print("hris", 4218, "payroll", len(pay))
