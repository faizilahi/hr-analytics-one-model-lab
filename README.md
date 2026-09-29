# Headcount That Disagreed With Payroll

[Faiz Elahi](https://www.linkedin.com/in/faizilahi) — [pendataco.com](https://pendataco.com) — [github.com/faizilahi](https://github.com/faizilahi)

Synthetic data only. No vendor-customer employment claim.

HRIS headcount was **4,218**; payroll counted **4,173**. The grain difference was
leave status: HRIS kept leavers active through month-end while payroll dropped
them on termination date.

## The grain

HRIS: `employee_id × month` where `hr_status in (Active, Leave)`.
Payroll: paid employees with `pay_end_date >= month_start`.

## The leaver

**45** employees terminated mid-September still active on the HRIS September
snapshot.

## The one definition

Finance-approved: count employees with `termination_date IS NULL OR termination_date > month_end`.
One-model headcount **4,173** — matches payroll.

```powershell
pip install -r requirements.txt
python scripts/generate_synthetic_data.py
python src/run_headcount.py
```
