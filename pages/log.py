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


def log(username):

    if username:
        api = ApiMethods(username=username)
        status, msg = api.check_player_exists()
        if status:
            st.sidebar.write("Player found")

            with open('data/messages.json') as json_file:
                messages = json.load(json_file)
            level_table = pd.read_csv("data/level_table.csv")

            player_data = api.get_player_snapshots(id=msg, period="month")
            boss_df = snapshot_to_df(player_data, type="boss").replace(-1, 0)
            skill_df = snapshot_to_df(
                player_data, type="skills").replace(-1, 0)

            timeline_data = timeline_data_merge(
                boss_df, skill_df, level_table).head(15)

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

                with st.beta_expander(short_m):
                    st.write(long_m)
                    if (var_type == "skill") & (val == 99):
                        st.balloons()

            print(messages)
