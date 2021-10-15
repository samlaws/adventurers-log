import streamlit as st
import pandas as pd
import numpy as np
import traceback
import random
import json

from utils.config import format_sel, boss_dict


def log_writer(timeline_data, messages):
    # main fn for writing the expander containers in the log page
    # takes the timeline data as input and calls other functions
    # depending on the type of event

    for index, row in timeline_data.iterrows():

        var_type = row["var_type"]
        var = row["variable"]
        date = row["date"].strftime('%d %B %Y')

        if var_type == "boss":
            short_m, long_m = boss_event_writer(
                row, var, var_type, date, messages)
        elif var_type == "clue":
            short_m, long_m = clue_event_writer(
                row, var, var_type, date, messages)
        elif var_type == "skill":
            short_m, long_m, val = skill_event_writer(
                row, var, var_type, date, messages)

        with st.beta_expander(short_m):
            st.write(long_m)
            # special case for 99s
            if var_type == "skill":
                if val == 99:
                    st.balloons()


def boss_event_writer(row, var, var_type, date, messages):

    diffs = int(row["diffs"])
    val = int(row["value"])
    if row["diffs"] == row["value"]:
        # if these are equal then value gone from 0 to current, meaning freshly ranked
        # wrong to write "killed 10 jad" when mostly likely only killed 1 and got over
        # the threshold
        short_m = "Now ranked for %s" % (format_sel(var))
    else:
        short_m = "%s %s" % (
            int(diffs), format_sel(var))
    try:
        long_m = random.choice(messages[var_type][var])
        long_m = long_m.replace("XXX", str(
            diffs)).replace("YYY", str(val))
        long_m += " (%s)" % date
    except KeyError:
        if row["diffs"] == row["value"]:
            long_m = "I have now killed %s %s in total. (%s)" % (
                val, format_sel(var), date)
        else:
            long_m = "I killed %s %s. (%s)" % (
                diffs, format_sel(var), date)

    return short_m, long_m


def clue_event_writer(row, var, var_type, date, messages):

    diffs = int(row["diffs"])
    val = int(row["value"])
    short_m = "%s %s clue scroll" % (int(diffs), format_sel(
        var).split(" ")[2])
    if diffs > 1:
        short_m += "s"
    try:
        long_m = random.choice(messages[var_type][var])
        long_m = long_m.replace("XXX", str(
            diffs)).replace("YYY", str(val))
        long_m += " (%s)" % date
    except KeyError:
        shorter_m = " ".join(short_m.split(" ")[1:])
        if row["diffs"] == row["value"]:
            long_m = "I completed my first %s. I have now completed %s %s. (%s)" % (
                shorter_m, val, shorter_m, date)
        else:
            if val > 1:
                long_m = "I completed %s. I have now completed %s %s. (%s)" % (
                    short_m, val, shorter_m+"s", date)
            else:
                long_m = "I completed %s. I have now completed %s %s. (%s)" % (
                    short_m, val, shorter_m, date)

    return short_m, long_m


def skill_event_writer(row, var, var_type, date, messages):

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
        diffs = int(row["l_diffs"])
        if diffs > 1:
            long_m = "I gained %s levels in %s, I am now level %s. (%s)" % (
                diffs, format_sel(var), val, date)
        else:
            long_m = "I gained a level in %s, I am now level %s. (%s)" % (
                format_sel(var), val, date)

    return short_m, long_m, val
