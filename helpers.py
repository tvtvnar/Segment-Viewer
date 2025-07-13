from __future__ import annotations
import pandas as pd

def vc_df(series: pd.Series, *, top: int | None = None,
          x_name: str = "x", y_name: str = "count") -> pd.DataFrame:
    """Convert a value_counts Series to a tidy DataFrame."""
    out = series.value_counts(dropna=False)
    if top:
        out = out.head(top)
    df = out.reset_index()
    df.columns = [x_name, y_name]
    return df

 def hide_idx(df: pd.DataFrame) -> pd.DataFrame:
    """Reset the index to blank strings to hide it in Streamlit."""
    df_copy = df.copy()
    df_copy.index = [""] * len(df_copy)
    return df_copy
