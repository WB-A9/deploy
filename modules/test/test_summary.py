from modules.stats import Summary
import pandas as pd

df = pd.read_csv("../../data/df_daily_summary.csv")

summarizer = Summary(df)

def test_summary():
    pass