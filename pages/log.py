import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import string

from utils.api import ApiMethods
from utils.snapshot_wrangling import snapshot_to_df
from utils.config import skill_layout, format_sel


def log(username):

    if username:
        api = ApiMethods(username=username)
        status, msg = api.check_player_exists()
        try:
            if status:
                st.sidebar.write("Player found")

                player_data = api.get_player_snapshots(id=msg, period="week")
                boss_df = snapshot_to_df(player_data, type="boss").drop_duplicates(
                    subset=["variable", "value"]).replace(-1, 0)
                skill_df = snapshot_to_df(player_data, type="skills").drop_duplicates(
                    subset=["variable", "value"]).replace(-1, 0)

                skill_df = skill_df[skill_df["variable"] != "overall"]

                boss_df.sort_values(
                    by=["variable", "date"], ascending=False, inplace=True)
                boss_df['diffs'] = boss_df['value'].diff()
                mask = boss_df.variable != boss_df.variable.shift(1)
                boss_df['diffs'][mask] = np.nan
                boss_df.dropna(inplace=True)
                boss_df["diffs"] = boss_df["diffs"].abs()

                st.dataframe(boss_df)

                skill_df.sort_values(
                    by=["variable", "date"], ascending=False, inplace=True)
                skill_df['diffs'] = skill_df['value'].diff()
                mask = skill_df.variable != skill_df.variable.shift(1)
                skill_df['diffs'][mask] = np.nan
                skill_df.dropna(inplace=True)
                skill_df["diffs"] = skill_df["diffs"].abs()

                st.dataframe(skill_df)
                # xp gaining sessions over period

        except Exception as e:
            print(e)
