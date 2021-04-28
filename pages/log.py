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

            player_data = api.get_player_snapshots(id=msg, period="year")
            boss_df = snapshot_to_df(player_data, type="boss").replace(-1, 0)
            skill_df = snapshot_to_df(
                player_data, type="skills").replace(-1, 0)

            st.dataframe(skill_df)

            timeline_data = timeline_data_merge(
                boss_df, skill_df, level_table).tail(30)

            messages = []
            for index, row in timeline_data.iterrows():
                if row["var_type"] == "boss":
                    messages.append("%s %s kills" % (
                        int(row["diffs"]), format_sel(row["variable"])))
                else:
                    messages.append("%s levels gained in %s" % (
                        int(row["l_diffs"]), format_sel(row["variable"])))

            timeline_data["message"] = messages

            if st.button("Generate timeline plot"):
                st.pyplot(timeline_plot(timeline_data))
