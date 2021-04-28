import streamlit as st
import pandas as pd
import numpy as np
import traceback

from utils.api import ApiMethods
from utils.snapshot_wrangling import snapshot_to_df


def log(username):

    if username:
        api = ApiMethods(username=username)
        status, msg = api.check_player_exists()
        if status:
            st.sidebar.write("Player found")

            level_table = pd.read_csv("data/level_table.csv")

            player_data = api.get_player_snapshots(id=msg, period="month")
            boss_df = snapshot_to_df(player_data, type="boss").replace(-1, 0)
            skill_df = snapshot_to_df(
                player_data, type="skills").replace(-1, 0)

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

            st.dataframe(boss_df)

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

            st.dataframe(skill_df)
