import pandas as pd
import streamlit as st
from utils.api import ApiMethods


@st.cache()
def snapshot_to_df(snapshots, type):
    sd = []
    for snapshot in snapshots:
        data = {}
        data["date"] = snapshot["createdAt"]
        for k in snapshot.keys():
            try:
                if type == "skills":
                    val = snapshot[k]["experience"]
                else:
                    val = snapshot[k]["kills"]

                data[k] = val
            except Exception:
                pass

        sd.append(data)

    d = {}
    for k in sd[0].keys():
        d[k] = list(d[k] for d in sd)

    df = pd.DataFrame.from_dict(d)
    df.set_index("date", inplace=True)

    df = df.reset_index().melt(id_vars=['date'])
    # UTC to gmt?
    df["date"] = pd.to_datetime(df["date"]) + pd.DateOffset(hours=1)

    return df
