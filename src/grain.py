import pandas as pd

def hris_count(df):
    return int(len(df[df["hr_status"].isin(["Active", "Leave"])]))

def one_definition(df, month_end="2024-09-30"):
    term = df["termination_date"]
    active = term.isna() | (term.astype(str) > month_end)
    return int(active.sum())
