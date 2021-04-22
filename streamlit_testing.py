import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from vega_datasets import data

from api_testing import ApiMethods
from snapshots_to_pandas import snapshot_to_skills
from utils import skill_layout


username = st.sidebar.text_input(
    "Enter a username", value='', max_chars=12).replace("-", " ")
# username = "pompelmo"
if username:
    api = ApiMethods(username=username)

    status, msg = api.check_player_exists()
    try:
        if status:
            st.sidebar.write("Player found")

            period = st.selectbox('Tracking period:',
                                  ('6h', 'day', 'week', 'month', 'year'), index=2)

            player_data = api.get_player_snapshots(id=msg, period=period)

            skill_df = snapshot_to_skills(player_data)

            overall = skill_df[skill_df["variable"] == "overall"]
            skill_df = skill_df[skill_df["variable"] != "overall"]

            filter_skills = []

            # create a grid of skills with filtering checkboxes
            # makes use of the streamlit columns
            skill_array = np.array(skill_layout, dtype="object")
            n_rows, n_cols = len(skill_array[0]), len(skill_array)
            cols = st.beta_columns(n_cols-1)
            for c in range(n_cols-1):
                for r in range(n_rows):
                    check = cols[c].checkbox(skill_array[c][r][1].lower())
                    if check:
                        filter_skills.append(skill_array[c][r][0])

            if filter_skills:
                chart_data = skill_df[skill_df["variable"].isin(filter_skills)]
            else:
                chart_data = overall

            # Create a selection that chooses the nearest point & selects based on x-value
            nearest = alt.selection(type='single', nearest=True, on='mouseover',
                                    fields=['date'], empty='none')

            # The basic line
            # define y-axis label format depending on time period selection
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
                    zero=False), axis=alt.Axis(title="XP", titleFontWeight="normal")),
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
                opacity=alt.condition(nearest, alt.value(1), alt.value(0))
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
