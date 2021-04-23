import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import string

from utils.api import ApiMethods
from utils.snapshot_wrangling import snapshot_to_df
from utils.config import skill_layout, format_sel


def boss_dash(username, period):

    if username:
        api = ApiMethods(username=username)
        status, msg = api.check_player_exists()
        try:
            if status:
                st.sidebar.write("Player found")

                player_data = api.get_player_snapshots(id=msg, period=period)

                boss_df = snapshot_to_df(player_data, type="boss")

                boss_df = boss_df[boss_df["variable"] != "overall"]
                boss_list = list(boss_df["variable"].unique())
                boss_list.insert(0, "")

                boss_dict = {k: string.capwords(k.replace("_", " "))
                             for k in boss_list}

                filter_boss = []

                boss1 = st.empty()
                boss2 = st.empty()
                boss3 = st.empty()

                choice1 = boss1.selectbox(
                    "Choose a boss", boss_list, format_func=format_sel)
                choice2 = None

                filter_boss.append(choice1)

                if choice1:
                    choice2 = boss2.selectbox(
                        "Add another?", boss_list, format_func=format_sel)
                    filter_boss.append(choice2)
                if choice2:
                    choice3 = boss3.selectbox(
                        "One more?", boss_list, format_func=format_sel)
                    filter_boss.append(choice3)

                chart_data = boss_df[boss_df["variable"].isin(
                    filter_boss)]

                if not chart_data.empty:

                    # Create a selection that chooses the nearest point & selects based on x-value
                    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                                            fields=['date'], empty='none')

                    # The basic line
                    # define y-axis label format depending on time period selection

                    # maybe this would be more appropriate to be scaled from the current range
                    # i.e if period = year but slider selects a smaller range
                    if period in ["day", "6h"]:
                        time_format = "%H:%M"
                    elif period == "week":
                        time_format = "%d-%m"
                    elif period == "month":
                        time_format = "%d-%m"
                    else:
                        time_format = "%b %Y"

                    line = alt.Chart(chart_data).mark_line(interpolate="linear").encode(
                        x=alt.X('date:T', axis=alt.Axis(
                            title="Time", titleFontWeight="normal", format=time_format)),
                        y=alt.Y('value:Q', scale=alt.Scale(
                            zero=False), axis=alt.Axis(title="Kills", titleFontWeight="normal")),
                        color='variable:N'
                    )
                    # Transparent selectors across the chart. This is what tells us
                    # the x-value of the cursor
                    selectors = alt.Chart(chart_data).mark_point().encode(
                        x='date:T',
                        opacity=alt.value(0),
                    ).add_selection(
                        nearest
                    )
                    # Draw points on the line, and highlight based on selection
                    points = line.mark_point().encode(
                        opacity=alt.condition(
                            nearest, alt.value(1), alt.value(0))
                    )
                    # Draw text labels near the points, and highlight based on selection
                    text = line.mark_text(align='left', dx=10, dy=10).encode(
                        text=alt.condition(nearest, alt.Text(
                            'value:Q', format=","), alt.value(' '))
                    )
                    # Draw a rule at the location of the selection
                    rules = alt.Chart(chart_data).mark_rule(color='gray').encode(
                        x='date:T',
                    ).transform_filter(
                        nearest
                    )
                    # Put the five layers into a chart and bind the data
                    st.altair_chart(alt.layer(
                        line, selectors, points, rules, text
                    ), use_container_width=True)

            else:
                st.sidebar.write("Player not found")
                st.sidebar.write(
                    "Either they do not exist, or are not 1337 enough to be tracked on Wiseoldman.net")

        except IndexError:
            st.write("No information from that time period")
    else:
        st.write("Enter a username in the side bar to get started...")
