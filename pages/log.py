import streamlit as st
import pandas as pd
import numpy as np
import traceback
import matplotlib.pyplot as plt
import random
import json

from utils.api import ApiMethods
from utils.config import format_sel, boss_dict
from utils.snapshot_wrangling import snapshot_to_df, timeline_data_merge


def timeline_plot(timeline_data):
    # Choose some nice levels
    levels = np.tile([-3, 3, -2, 2, -1, 1],
                     int(np.ceil(len(timeline_data["date"])/6)))[:len(timeline_data["date"])]

    # Create figure and plot a stem plot with the date
    fig, ax = plt.subplots(figsize=(6, 20))

    # The vertical stems.
    ax.hlines(timeline_data["date"], 0, levels, color="tab:red")
    ax.plot(np.zeros_like(timeline_data["date"]), timeline_data["date"], "-o",
            color="k", markerfacecolor="w")  # Baseline and markers on it.

    # annotate lines
    for d, l, r in zip(timeline_data["date"], levels, timeline_data["message"]):
        ax.annotate(r, xy=(l, d),
                    xytext=(np.sign(l)*3, -3), textcoords="offset points",
                    horizontalalignment="right",
                    verticalalignment="bottom" if l > 0 else "top")

    # remove y axis and spines
    ax.xaxis.set_visible(False)
    ax.spines[["right", "top", "bottom"]].set_visible(False)

    ax.margins(y=0.1)
    plt.axis("off")
    return fig


def log(username, virtual):

    if username:
        api = ApiMethods(username=username)
        status, msg = api.check_player_exists()
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
            player_data = api.get_player_snapshots(id=msg, period="month")
            if len(player_data) < 50:
                player_data = api.get_player_snapshots(id=msg, period="year")
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
            print(clues_l.head())
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

            st.markdown("## Recent Events")
            # have to define here so that skills and bosses that are mentioned
            # can be highlighted
            timeline_data = timeline_data_merge(
                boss_df, skill_df, clues_df, level_table, virtual).head(15)

            # This could be a util function that takes the timeline data as an argument
            for index, row in timeline_data.iterrows():

                var_type = row["var_type"]
                var = row["variable"]
                date = row["date"].strftime('%d %B %Y')

                if var_type == "boss":
                    diffs = int(row["diffs"])
                    val = int(row["value"])
                    if row["diffs"] == row["value"]:
                        # if these are equal then value gone from 0 to current, meaning freshly ranked
                        # wrong to write "killed 10 jad" when mostly likely only killed 1 and got over
                        # the treshold
                        short_m = "Now ranked for %s" % (format_sel(var))
                    else:
                        short_m = "%s %s" % (
                            int(diffs), format_sel(var))
                elif var_type == "clue":
                    diffs = int(row["diffs"])
                    val = int(row["value"])
                    short_m = "%s %s clue scroll" % (int(diffs), format_sel(
                        var).split(" ")[2])
                    if diffs > 1:
                        short_m += "s"
                else:
                    diffs = int(row["l_diffs"])
                    val = int(row["level"])
                    short_m = "%s level gained in %s" % (
                        int(diffs), format_sel(var))
                    if diffs > 1:
                        short_m = short_m.replace("level", "levels")
                try:
                    long_m = random.choice(messages[var_type][var])
                    long_m = long_m.replace("XXX", str(
                        diffs)).replace("YYY", str(val))
                    long_m += " (%s)" % date
                except KeyError:
                    # No message for skill or boss or clue, reverting to default
                    if var_type == "boss":
                        if row["diffs"] == row["value"]:
                            long_m = "I have now killed %s %s in total. (%s)" % (
                                val, format_sel(var), date)
                        else:
                            long_m = "I killed %s %s. (%s)" % (
                                diffs, format_sel(var), date)
                    elif var_type == "clue":
                        shorter_m = " ".join(short_m.split(" ")[1:])
                        if row["diffs"] == row["value"]:
                            long_m = "I completed my first %s. I have now completed %s %s (%s)" % (
                                shorter_m, val, shorter_m, date)
                        else:
                            long_m = "I completed %s. I have now completed %s %s (%s)" % (
                                short_m, val, shorter_m, date)
                    else:
                        diffs = int(row["l_diffs"])
                        if diffs > 1:
                            long_m = "I gained %s levels in %s, I am now level %s (%s)" % (
                                diffs, format_sel(var), val, date)
                        else:
                            long_m = "I gained a level in %s, I am now level %s (%s)" % (
                                format_sel(var), val, date)

                with st.beta_expander(short_m):
                    st.write(long_m)
                    if (var_type == "skill") & (val == 99):
                        st.balloons()

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
                    if index != 0:  # ignore overall
                        if left == 6:  # once the last column has been reached, reset
                            left, right = 0, 1

                        try:
                            boss = boss_dict[row["variable"]]
                        except KeyError:
                            boss = "%s:" % (format_sel(row["variable"]))
                        level = str(int(row["value"]))
                        if level == "0":
                            level = "--"
                        if row["variable"] in timeline_data["variable"].to_list():
                            boss = "<span class='green'>%s</span>" % boss
                            level = "<span class='green'>%s</span>" % level
                        cols_bosses[left].markdown(
                            boss, unsafe_allow_html=True)
                        cols_bosses[right].markdown(
                            level, unsafe_allow_html=True)
                        left += 2
                        right += 2

        else:
            t = "<div><span class='red'>Player not found</span></div>"
            st.sidebar.markdown(t, unsafe_allow_html=True)
            t = "<div><span class='red'>Either player doesn't exist, or are not tracked on Wiseoldman.net</span></div>"
            st.sidebar.markdown(t, unsafe_allow_html=True)
