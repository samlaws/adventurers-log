import streamlit as st
import pandas as pd
import numpy as np
import traceback
import matplotlib.pyplot as plt
import random
import json

from utils.api import ApiMethods
from utils.config import format_sel
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
            st.sidebar.write("Player found")

            # load in supporting data - messages.json with custom messages
            # for the log and the level up table
            with open('data/messages.json') as json_file:
                messages = json.load(json_file)
            level_table = pd.read_csv("data/level_table.csv")

            player_data = api.get_player_snapshots(id=msg, period="month")
            boss_df = snapshot_to_df(player_data, type="boss").replace(-1, 0)
            skill_df = snapshot_to_df(
                player_data, type="skills").replace(-1, 0)

            skill_l = skill_df[skill_df["date"]
                               == skill_df["date"].max()]

            skill_r_df = snapshot_to_df(
                player_data, type="skills", subtype="Rank").replace(-1, 0)

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

            # summary_data
            total_level = skill_l[skill_l["variable"]
                                  == "overall"]["level"].values[0]
            total_xp = skill_l[skill_l["variable"]
                               == "overall"]["value"].values[0]
            overall_rank = skill_l[skill_l["variable"]
                                   == "overall"]["rank"].values[0]

            cols_head = st.beta_columns(3)
            cols_head[0].markdown(
                f"### Total Level:\n {int(total_level):,}")
            cols_head[1].markdown(f"### Total XP:\n {int(total_xp):,}")
            cols_head[2].markdown(f"### Overall Rank:\n {int(overall_rank):,}")

            st.markdown("## Skills")
            cols_skills = st.beta_columns(6)
            left, right = 0, 1
            for index, row in skill_l.iterrows():
                if index != 0:
                    if left == 6:
                        left, right = 0, 1
                    print(left)
                    skill, level = format_sel(
                        row["variable"]) + ":", str(int(row["level"]))
                    cols_skills[left].write(skill)
                    cols_skills[right].write(level)
                    left += 2
                    right += 2

            cols = st.beta_columns(2)

            timeline_data = timeline_data_merge(
                boss_df, skill_df, level_table, virtual).head(15)

            cols[0].markdown("## Recent Events")

            for index, row in timeline_data.iterrows():

                var_type = row["var_type"]
                var = row["variable"]
                date = row["date"].strftime('%d %B %Y')
                if var_type == "boss":
                    diffs = int(row["diffs"])
                    val = int(row["value"])
                    short_m = "%s %s" % (
                        int(diffs), format_sel(var))
                else:
                    diffs = int(row["l_diffs"])
                    val = int(row["level"])
                    short_m = "%s levels gained in %s" % (
                        int(diffs), format_sel(var))
                try:
                    long_m = random.choice(messages[var_type][var])
                    long_m = long_m.replace("XXX", str(
                        diffs)).replace("YYY", str(val))
                except KeyError:
                    # No message for skill or boss, reverting to default
                    if var_type == "boss":
                        long_m = "I killed %s %s. (%s)" % (
                            diffs, format_sel(var), date)
                    else:
                        if diffs > 1:
                            long_m = "I gained a level in %s, I am now level %s (%s)" % (
                                format_sel(var), val, date)
                        else:
                            long_m = "I gained %s levels in %s, I am now level %s  (%s)" % (
                                diffs, format_sel(var), val, date)

                with cols[0].beta_expander(short_m):
                    st.write(long_m)
                    if (var_type == "skill") & (val == 99):
                        st.balloons()
