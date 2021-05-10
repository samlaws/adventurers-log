import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import traceback

from utils.api import ApiMethods
from utils.snapshot_wrangling import snapshot_to_df
from utils.config import format_sel


def skill_dash(username, period):

    if username:
        api = ApiMethods(username=username)
        status, msg = api.check_player_exists()
        try:
            if status:
                t = "<div><span class='green'>Player Found</span></div>"
                st.sidebar.markdown(t, unsafe_allow_html=True)

                player_data = api.get_player_snapshots(id=msg, period=period)

                cols = st.beta_columns((4, 1))
                subtype = cols[1].radio(" ", ["XP", "Rank"])
                scale_dict = {"Rank": True, "XP": False}

                skill_df = snapshot_to_df(
                    player_data, type="skills", subtype=subtype)

                skill_list = list(skill_df["variable"].unique())
                filter_skills = cols[0].multiselect(
                    'Enter the skills to track/compare',
                    options=skill_list, format_func=format_sel)

                chart_data = skill_df[skill_df["variable"].isin(
                    filter_skills)]

                if not chart_data.empty:

                    graph_placeholder = st.empty()
                    slider = True

                    # The basic line
                    # define y-axis label format depending on time period selection
                    if period in ["day", "6h"]:
                        time_format = "%H:%M"
                        slider = False
                    elif period == "week":
                        time_format = "%d-%m"
                    elif period == "month":
                        time_format = "%d-%m"
                    else:
                        time_format = "%b %Y"

                    if slider:
                        start_date = chart_data["date"].min().to_pydatetime()
                        end_date = chart_data["date"].max().to_pydatetime()

                        x = st.slider("Date range", start_date, end_date,
                                      (start_date, end_date))

                        new_start = pd.Timestamp(x[0])
                        new_end = pd.Timestamp(x[1])
                        mask = (chart_data['date'] > new_start) & (
                            chart_data['date'] <= new_end)
                        chart_data = chart_data.loc[mask]

                    # Create a selection that chooses the nearest point & selects based on x-value
                    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                                            fields=['date'], empty='none')

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
                    graph_placeholder.altair_chart(alt.layer(
                        line, selectors, points, rules, text
                    ), use_container_width=True)
                else:
                    st.write("Select some skills to view the graph...")

            else:
                t = "<div><span class='red'>Player not found</span></div>"
                st.sidebar.markdown(t, unsafe_allow_html=True)
                t = "<div><span class='red'>Either player doesn't exist, or are not tracked on Wiseoldman.net</span></div>"
                st.sidebar.markdown(t, unsafe_allow_html=True)

        except IndexError:
            st.write("No information from that time period")
            traceback.print_exc()

    else:
        st.write("Enter a username in the side bar to get started...")
