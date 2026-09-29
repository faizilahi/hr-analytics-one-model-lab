"""Generate synthetic HRIS-style data for educational use only."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)


def main(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    n_employees = 800
    departments = [
        ("D001", "Engineering", "TECH"),
        ("D002", "Sales", "GTM"),
        ("D003", "Operations", "OPS"),
        ("D004", "People", "HR"),
        ("D005", "Finance", "FIN"),
    ]
    dept_df = pd.DataFrame(departments, columns=["department_id", "department_name", "cost_center"])

    genders = ["Female", "Male", "Non-binary", "Prefer not to say"]
    ethnicities = ["Asian", "Black", "Hispanic", "White", "Other", "Two or more"]
    levels = ["IC1", "IC2", "IC3", "M1", "M2", "Director"]

    emp_ids = [f"E{i:05d}" for i in range(1, n_employees + 1)]
    hire_dates = pd.to_datetime(RNG.choice(pd.date_range("2018-01-01", "2024-06-01"), n_employees))
    dept_ids = RNG.choice([d[0] for d in departments], n_employees)
    manager_pool = emp_ids.copy()
    managers = RNG.choice(manager_pool, n_employees, replace=True)
    managers = np.where(RNG.random(n_employees) < 0.12, None, managers)

    employees = pd.DataFrame(
        {
            "employee_id": emp_ids,
            "hire_date": hire_dates,
            "department_id": dept_ids,
            "manager_id": managers,
            "job_level": RNG.choice(levels, n_employees),
            "gender": RNG.choice(genders, n_employees, p=[0.48, 0.47, 0.03, 0.02]),
            "ethnicity_proxy": RNG.choice(ethnicities, n_employees),
            "fte": RNG.choice([0.5, 0.8, 1.0], n_employees, p=[0.05, 0.1, 0.85]),
            "is_active": True,
        }
    )

    term_mask = RNG.random(n_employees) < 0.18
    term_dates = pd.to_datetime(RNG.choice(pd.date_range("2022-01-01", "2025-03-01"), term_mask.sum()))
    employees.loc[term_mask, "termination_date"] = term_dates.values
    employees.loc[term_mask, "is_active"] = False
    employees["termination_date"] = pd.to_datetime(employees.get("termination_date"))

    events = []
    for _, row in employees.iterrows():
        events.append(
            {
                "event_id": f"EV-H-{row.employee_id}",
                "employee_id": row.employee_id,
                "event_type": "HIRE",
                "event_date": row.hire_date,
            }
        )
        if pd.notna(row.get("termination_date")):
            events.append(
                {
                    "event_id": f"EV-T-{row.employee_id}",
                    "employee_id": row.employee_id,
                    "event_type": "TERMINATION",
                    "event_date": row.termination_date,
                }
            )
    events_df = pd.DataFrame(events)

    dept_df.to_csv(out_dir / "dim_department.csv", index=False)
    employees.to_csv(out_dir / "dim_employee.csv", index=False)
    events_df.to_csv(out_dir / "fact_workforce_event.csv", index=False)
    print(f"Wrote HR synthetic data to {out_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    args = parser.parse_args()
    main(args.out)
