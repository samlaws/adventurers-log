import streamlit as st
import pandas as pd
import numpy as np
import traceback
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

            level_table = pd.read_csv("data/level_table.csv")

            player_data = api.get_player_snapshots(id=msg, period="month")
            boss_df = snapshot_to_df(player_data, type="boss").replace(-1, 0)
            skill_df = snapshot_to_df(
                player_data, type="skills").replace(-1, 0)

            timeline_data = timeline_data_merge(
                boss_df, skill_df, level_table).head(15)

            # st.dataframe(timeline_data)

            short_m = []
            for index, row in timeline_data.iterrows():
                if row["var_type"] == "boss":
                    short_m.append("%s %s" % (
                        int(row["diffs"]), format_sel(row["variable"])))
                else:
                    short_m.append("%s levels gained in %s" % (
                        int(row["l_diffs"]), format_sel(row["variable"])))

            long_m = []
            for index, row in timeline_data.iterrows():
                if row["var_type"] == "boss":
                    long_m.append("I killed %s %s. (%s)" % (
                        int(row["diffs"]), format_sel(row["variable"]), row["date"].strftime('%d %B %Y')))
                else:
                    if int(row["l_diffs"]) > 1:
                        long_m.append("I gained a level in %s, I am now level %s (%s)" % (
                            format_sel(row["variable"]), int(row["level"]), row["date"].strftime('%d %B %Y')))
                    else:
                        long_m.append("I gained %s levels in %s, I am now level %s  (%s)" % (
                            int(row["l_diffs"]), format_sel(row["variable"]), int(row["level"]), row["date"].strftime('%d %B %Y')))

            for tup in zip(short_m, long_m):
                with st.beta_expander(tup[0]):
                    st.write(tup[1])
