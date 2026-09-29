"""Build people analytics mart in DuckDB and export charts."""
from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


def build_mart(data_dir: Path, db_path: Path) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(str(db_path))
    con.execute(
        f"""
        CREATE OR REPLACE TABLE dim_department AS
        SELECT * FROM read_csv_auto('{data_dir / "dim_department.csv"}');
        CREATE OR REPLACE TABLE dim_employee AS
        SELECT * FROM read_csv_auto('{data_dir / "dim_employee.csv"}');
        CREATE OR REPLACE TABLE fact_workforce_event AS
        SELECT * FROM read_csv_auto('{data_dir / "fact_workforce_event.csv"}');
        """
    )
    return con


def charts(con: duckdb.DuckDBPyConnection, img_dir: Path) -> None:
    img_dir.mkdir(parents=True, exist_ok=True)

    headcount = con.execute(
        """
        SELECT d.department_name, COUNT(*) AS active_headcount
        FROM dim_employee e
        JOIN dim_department d ON e.department_id = d.department_id
        WHERE e.is_active = TRUE
        GROUP BY 1 ORDER BY 2 DESC
        """
    ).df()
    plt.figure(figsize=(8, 5))
    plt.bar(headcount["department_name"], headcount["active_headcount"], color="#2E86AB")
    plt.title("Active Headcount by Department (Synthetic)")
    plt.ylabel("Employees")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(img_dir / "headcount_by_department.png", dpi=120)
    plt.close()

    turnover = con.execute(
        """
        WITH terms AS (
          SELECT department_id, COUNT(*) AS terminations
          FROM dim_employee WHERE termination_date IS NOT NULL GROUP BY 1
        ),
        active AS (
          SELECT department_id, COUNT(*) AS active_count
          FROM dim_employee WHERE is_active = TRUE GROUP BY 1
        )
        SELECT d.department_name,
               COALESCE(t.terminations, 0) * 1.0 / NULLIF(a.active_count, 0) AS turnover_rate
        FROM dim_department d
        LEFT JOIN terms t ON d.department_id = t.department_id
        LEFT JOIN active a ON d.department_id = a.department_id
        ORDER BY turnover_rate DESC
        """
    ).df()
    plt.figure(figsize=(8, 5))
    plt.bar(turnover["department_name"], turnover["turnover_rate"], color="#A23B72")
    plt.title("Simple Turnover Rate by Department (Synthetic)")
    plt.ylabel("Terminations / Active Headcount")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(img_dir / "turnover_by_department.png", dpi=120)
    plt.close()

    diversity = con.execute(
        """
        SELECT ethnicity_proxy, COUNT(*) AS n
        FROM dim_employee WHERE is_active = TRUE
        GROUP BY 1 ORDER BY n DESC
        """
    ).df()
    plt.figure(figsize=(7, 5))
    plt.pie(diversity["n"], labels=diversity["ethnicity_proxy"], autopct="%1.1f%%")
    plt.title("Workforce Composition Proxy (Synthetic — Not EEO Reporting)")
    plt.tight_layout()
    plt.savefig(img_dir / "diversity_proxy_pie.png", dpi=120)
    plt.close()

    span = con.execute(
        """
        SELECT m.employee_id AS manager_id,
               COUNT(*) AS direct_reports
        FROM dim_employee e
        JOIN dim_employee m ON e.manager_id = m.employee_id
        WHERE e.is_active = TRUE
        GROUP BY 1
        """
    ).df()
    plt.figure(figsize=(8, 5))
    plt.hist(span["direct_reports"], bins=range(1, span["direct_reports"].max() + 2), color="#F18F01", edgecolor="white")
    plt.title("Span of Control — Direct Reports per Manager (Synthetic)")
    plt.xlabel("Direct reports")
    plt.ylabel("Managers")
    plt.tight_layout()
    plt.savefig(img_dir / "span_of_control_hist.png", dpi=120)
    plt.close()

    metrics = con.execute(
        """
        SELECT
          (SELECT COUNT(*) FROM dim_employee WHERE is_active) AS active_headcount,
          (SELECT COUNT(*) FROM dim_employee WHERE termination_date IS NOT NULL) AS total_terminations,
          (SELECT AVG(direct_reports) FROM (
             SELECT manager_id, COUNT(*) AS direct_reports FROM dim_employee
             WHERE is_active AND manager_id IS NOT NULL
             GROUP BY manager_id)) AS avg_span
        """
    ).df()
    metrics.to_csv(img_dir.parent.parent / "data" / "people_metrics_summary.csv", index=False)
    print(metrics)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=root / "data")
    parser.add_argument("--db", type=Path, default=root / "data" / "hr_mart.duckdb")
    parser.add_argument("--images", type=Path, default=root / "docs" / "images")
    args = parser.parse_args()

    con = build_mart(args.data, args.db)
    charts(con, args.images)
    con.close()
    print("HR analysis complete.")


if __name__ == "__main__":
    main()
