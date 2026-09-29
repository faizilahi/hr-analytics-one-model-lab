# Architecture — HR Analytics One-Model Pattern Lab

**Author:** Faiz Elahi  
**Purpose:** Educational demonstration of a people-analytics mart. **Not** affiliated with One Model SaaS.

## Layers

1. **Synthetic source (CSV)** — `dim_department`, `dim_employee`, `fact_workforce_event`
2. **DuckDB mart** — star-schema tables loaded for teaching SQL joins and grain
3. **Metrics & viz** — headcount, turnover proxy, diversity proxy, span of control

## Grain

- Employee dimension: one row per employee
- Event fact: hire and termination events (slowly changing workforce narrative)

See README mermaid for flow.
