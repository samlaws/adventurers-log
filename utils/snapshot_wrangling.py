import pandas as pd
import numpy as np
import streamlit as st
from utils.api import ApiMethods


def snapshot_to_df(snapshots, type, subtype):
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

                rank = snapshot[k]["rank"]

                data[k] = val
                data[k+"_rank"] = rank
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

    if subtype == "Rank":
        return df[df["variable"].str.contains("_rank")]
    else:
        return df[~df["variable"].str.contains("_rank")]


def timeline_data_merge(boss_df, skill_df, level_table):
    skill_df = skill_df[skill_df["variable"] != "overall"]

    # boss killing sessions over period
    boss_df.sort_values(
        by=["variable", "date"], ascending=True, inplace=True)
    boss_df['diffs'] = boss_df['value'].diff()
    mask = boss_df.variable != boss_df.variable.shift(1)
    boss_df['diffs'][mask] = np.nan
    boss_df.dropna(inplace=True)
    boss_df["diffs"] = boss_df["diffs"].abs()
    boss_df = boss_df[boss_df["diffs"] != 0]
    boss_df["var_type"] = "boss"

    # xp gaining sessions over period
    skill_df.sort_values(
        by=["variable", "date"], ascending=True, inplace=True)
    skill_df['diffs'] = skill_df['value'].diff()
    mask = skill_df.variable != skill_df.variable.shift(1)
    skill_df['diffs'][mask] = np.nan
    skill_df.dropna(inplace=True)
    skill_df["diffs"] = skill_df["diffs"].abs()

    bins = level_table["exp"].to_list()

    skill_df["level"] = pd.cut(skill_df.value, bins, labels=False)
    skill_df["level"] = skill_df["level"] + 1

    skill_df['l_diffs'] = skill_df['level'].diff()
    mask = skill_df.variable != skill_df.variable.shift(1)
    skill_df['l_diffs'][mask] = np.nan
    skill_df.dropna(inplace=True)
    skill_df["l_diffs"] = skill_df["l_diffs"].abs()

    skill_df = skill_df[skill_df["l_diffs"] != 0]
    skill_df["var_type"] = "skill"

    return pd.concat([skill_df, boss_df]
                     ).sort_values(by=["date"])
