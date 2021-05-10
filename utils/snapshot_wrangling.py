import pandas as pd
import numpy as np
import streamlit as st
from utils.api import ApiMethods

pd.options.mode.chained_assignment = None


def snapshot_to_df(snapshots, type, subtype="skill/xp"):
    sd = []
    for snapshot in snapshots:
        data = {}
        data["date"] = snapshot["createdAt"]
        for k in snapshot.keys():

            try:
                if type == "skills":
                    val = snapshot[k]["experience"]
                elif type == "clues":
                    val = snapshot[k]["score"]
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


def timeline_data_merge(boss_df, skill_df, clue_df, level_table, virtual):
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
    if not virtual:
        skill_df["level"] = np.clip(
            skill_df['level'], a_max=99, a_min=None)

    skill_df['l_diffs'] = skill_df['level'].diff()
    mask = skill_df.variable != skill_df.variable.shift(1)
    skill_df['l_diffs'][mask] = np.nan
    skill_df.dropna(inplace=True)
    skill_df["l_diffs"] = skill_df["l_diffs"].abs()

    skill_df = skill_df[skill_df["l_diffs"] != 0]
    skill_df["var_type"] = "skill"

    clue_df = clue_df[clue_df["variable"].isin(['clue_scrolls_beginner', 'clue_scrolls_easy',
                                                'clue_scrolls_medium', 'clue_scrolls_hard', 'clue_scrolls_elite',
                                                'clue_scrolls_master'])]
    clue_df.sort_values(
        by=["variable", "date"], ascending=True, inplace=True)
    clue_df['diffs'] = clue_df['value'].diff()
    mask = clue_df.variable != clue_df.variable.shift(1)
    clue_df['diffs'][mask] = np.nan
    clue_df = clue_df.dropna()
    clue_df.loc[:, "diffs"] = clue_df["diffs"].abs()
    clue_df = clue_df[clue_df["diffs"] != 0]
    clue_df["var_type"] = "clue"

    combined = pd.concat([skill_df, boss_df, clue_df]
                         ).sort_values(by=["date"], ascending=False)

    combined["day"] = combined["date"].dt.day

    # https://stackoverflow.com/questions/12589481
    # /multiple-aggregations-of-the-same-column-using-pandas-groupby-agg
    df_test = combined.groupby([(combined.variable != combined.variable.shift(
    )).cumsum(), (combined.day != combined.day.shift(
    )).cumsum()]).agg({'date': 'first',
                      'var_type': 'first',
                       'variable': 'first',
                       'value': 'first',
                       'diffs': 'sum',
                       'level': 'first',
                       'l_diffs': 'sum'
                       }).reset_index(drop=True)

    return df_test
