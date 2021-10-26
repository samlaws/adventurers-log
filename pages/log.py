import streamlit as st
import pandas as pd
import numpy as np
import json

from utils.api import ApiMethods
from utils.config import format_sel, boss_dict
from utils.log_writer import log_writer
from utils.snapshot_wrangling import snapshot_to_df, timeline_data_merge

pd.options.mode.chained_assignment = None


def log(username, virtual, group):

    if username:
        api = ApiMethods(username=username)
        status, msg = api.check_player_exists()
        print(msg)
        if status:
            t = "<div><span class='green'>Player Found</span></div>"
            st.sidebar.markdown(t, unsafe_allow_html=True)

            # update player
            api.update_player()

            # load in supporting data - messages.json with custom messages
            # for the log and the level up table
            with open('data/messages.json') as json_file:
                messages = json.load(json_file)
            level_table = pd.read_csv("data/level_table.csv")

            # load the player data from wiseoldman
            player_data = api.get_player_snapshots(id=msg[0], period="month")
            if len(player_data) < 25:
                player_data = api.get_player_snapshots(
                    id=msg[0], period="year")
            boss_df = snapshot_to_df(player_data, type="boss").replace(-1, 0)
            skill_df = snapshot_to_df(
                player_data, type="skills").replace(-1, 0)
            clues_df = snapshot_to_df(
                player_data, type="clues").replace(-1, 0)

            skill_r_df = snapshot_to_df(
                player_data, type="skills", subtype="Rank").replace(-1, 0)

            skill_l = skill_df[skill_df["date"]
                               == skill_df["date"].max()]
            boss_l = boss_df[boss_df["date"]
                             == boss_df["date"].max()]
            clues_l = clues_df[clues_df["date"]
                               == clues_df["date"].max()]
            skill_rl = skill_r_df[skill_r_df["date"]
                                  == skill_r_df["date"].max()]

            skill_l["rank"] = skill_rl["value"].to_list()
            bins = level_table["exp"].to_list()
            skill_l["level"] = pd.cut(
                skill_l.value, bins, labels=False)
            skill_l["level"] = skill_l["level"] + 1
            if not virtual:
                skill_l["level"] = np.clip(
                    skill_l['level'], a_max=99, a_min=None)
            skill_l.iloc[0, 4] = 0
            skill_l.iloc[0, 4] = skill_l["level"].sum()

            st.title(username)
            # summary data
            total_level = skill_l[skill_l["variable"]
                                  == "overall"]["level"].values[0]
            total_xp = skill_l[skill_l["variable"]
                               == "overall"]["value"].values[0]
            overall_rank = skill_l[skill_l["variable"]
                                   == "overall"]["rank"].values[0]
            total_clues = clues_l[clues_l["variable"]
                                  == "clue_scrolls_all"]["value"].values[0]
            total_bosses = boss_l["value"].sum()

            cols_head1 = st.beta_columns(3)
            cols_head1[0].markdown(
                f"### Total Level:\n {int(total_level):,}")
            cols_head1[1].markdown(f"### Total XP:\n {int(total_xp):,}")
            cols_head1[2].markdown(
                f"### Overall Rank:\n {int(overall_rank):,}")

            cols_head2 = st.beta_columns(3)
            cols_head2[0].markdown(
                f"### Total Clues:\n {int(total_clues):,}")
            cols_head2[1].markdown(
                f"### Total Bosses:\n {int(total_bosses):,}")
            cols_head2[2].markdown(
                f"### Player Type:\n {format_sel(msg[1])}")

            st.markdown("## Recent Events")
            # have to define here so that skills and bosses that are mentioned
            # can be highlighted
            timeline_data = timeline_data_merge(
                boss_df, skill_df, clues_df, level_table, virtual, group)
            print(timeline_data)
            log_writer(timeline_data.head(25), messages=messages)

            # Hi-scores section
            st.markdown("## Hi-scores")

            with st.beta_expander("Clues"):
                cols_clues = st.beta_columns((2, 1, 2, 1))
                left, right = 0, 1
                for index, row in clues_l.iterrows():
                    # ignore overall
                    if (index != 1):
                        if left == 4:  # once the last column has been reached, reset
                            left, right = 0, 1
                        if ("clue" in row["variable"]) and ("all" not in row["variable"]):
                            clue_level = "%s:" % (format_sel(row["variable"]))
                            clue_level = clue_level.split(" ")[2]
                            count = str(int(row["value"]))
                            if row["variable"] in timeline_data["variable"].to_list():
                                clue_level = "<span class='green'>%s</span>" % clue_level
                                count = "<span class='green'>%s</span>" % count
                            cols_clues[left].markdown(
                                clue_level, unsafe_allow_html=True)
                            cols_clues[right].markdown(
                                count, unsafe_allow_html=True)
                            left += 2
                            right += 2

            with st.beta_expander("Skills"):
                cols_skills = st.beta_columns((2, 1, 2, 1, 2, 1, 2, 1))
                left, right = 0, 1
                for index, row in skill_l.iterrows():
                    if index != 0:  # ignore overall
                        if left == 8:  # once the last column has been reached, reset
                            left, right = 0, 1
                        skill = "%s:" % (format_sel(row["variable"]))
                        try:
                            level = str(int(row["level"]))
                        except ValueError:
                            # Unranked skills
                            level = "--"
                        if row["variable"] in timeline_data["variable"].to_list():
                            skill = "<span class='green'>%s</span>" % skill
                            level = "<span class='green'>%s</span>" % level
                        cols_skills[left].markdown(
                            skill, unsafe_allow_html=True)
                        cols_skills[right].markdown(
                            level, unsafe_allow_html=True)
                        left += 2
                        right += 2

            with st.beta_expander("Bosses"):
                cols_bosses = st.beta_columns((2, 1, 2, 1, 2, 1))
                left, right = 0, 1
                for index, row in boss_l.iterrows():
                    if left == 6:  # once the last column has been reached, reset
                        left, right = 0, 1

                    try:
                        boss = boss_dict[row["variable"]]
                    except KeyError:
                        boss = "%s:" % (format_sel(row["variable"]))
                    boss += ":"

                    val = str(int(row["value"]))
                    if val == "0":
                        val = "--"
                    else:
                        val = f"{int(val):,}"

                    if row["variable"] in timeline_data["variable"].to_list():
                        boss = "<span class='green'>%s</span>" % boss
                        val = "<span class='green'>%s</span>" % val
                    cols_bosses[left].markdown(
                        boss, unsafe_allow_html=True)
                    cols_bosses[right].markdown(
                        val, unsafe_allow_html=True)
                    left += 2
                    right += 2

        else:
            t = "<div><span class='red'>Player not found</span></div>"
            st.sidebar.markdown(t, unsafe_allow_html=True)
            t = "<div><span class='red'>Either player doesn't exist, or are not tracked on Wiseoldman.net</span></div>"
            st.sidebar.markdown(t, unsafe_allow_html=True)
