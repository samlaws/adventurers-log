import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import string

from utils.api import ApiMethods
from utils.snapshot_wrangling import snapshot_to_df
from utils.config import format_sel_boss, list_formatter


def boss_dash(username, period):

    if username:
        api = ApiMethods(username=username)
        status, msg = api.check_player_exists()
        try:
            if status:
                t = "<div><span class='green'>Player Found</span></div>"
                st.sidebar.markdown(t, unsafe_allow_html=True)

                player_data = api.get_player_snapshots(
                    id=msg[0], period=period)

                cols = st.beta_columns((4, 1))
                subtype = cols[1].radio(" ", ["Kills", "Rank"])
                scale_dict = {"Rank": True, "Kills": False}

                boss_df = snapshot_to_df(
                    player_data, type="boss", subtype=subtype)
                boss_list = list_formatter(boss_df["variable"].unique())

                filter_boss = cols[0].multiselect(
                    'Enter the bosses to track/compare',
                    options=boss_list, format_func=format_sel_boss)

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
                            zero=False, reverse=scale_dict[subtype]), axis=alt.Axis(title=subtype, titleFontWeight="normal")),
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
                    st.write("Select some bosses to filter by...")

            else:
                t = "<div><span class='red'>Player not found</span></div>"
                st.sidebar.markdown(t, unsafe_allow_html=True)
                t = "<div><span class='red'>Either player doesn't exist, or are not tracked on Wiseoldman.net</span></div>"
                st.sidebar.markdown(t, unsafe_allow_html=True)

        except IndexError:
            st.write("")
            t = "<span class='red'>No information from that time period</span>"
            st.sidebar.markdown(t, unsafe_allow_html=True)
    else:
        st.write("Enter a username in the side bar to get started...")
