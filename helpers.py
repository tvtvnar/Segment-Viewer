# helpers.py
"""Utility helpers (value_counts → tidy DataFrame, hide index)."""
from __future__ import annotations
import pandas as pd

def vc_df(series: pd.Series, *, top: int | None = None,
          x_name: str = "x", y_name: str = "count") -> pd.DataFrame:
    out = series.value_counts(dropna=False)
    if top:
        out = out.head(top)
    out = out.reset_index()
    out.columns = [x_name, y_name]          # гарантировано уникальны
    return out

def hide_idx(df: pd.DataFrame) -> pd.DataFrame:
    """Просто прибиваем RangeIndex в колонку, чтобы Streamlit не рисовал индекс."""
    df = df.copy()
    df.index = [""] * len(df)
    return df