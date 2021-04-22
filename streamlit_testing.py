import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from vega_datasets import data

from api_testing import ApiMethods
from snapshots_to_pandas import snapshot_to_skills
from utils import skill_layout


username = st.sidebar.text_input("Enter a username", value='', max_chars=12)
#username = "pompelmo"
if username:
    api = ApiMethods(username=username)

    status, msg = api.check_player_exists()
    if status:
        st.sidebar.write("Player found")

        period = st.selectbox('Tracking period:',
                              ('6h', 'day', 'week', 'month', 'year'), index=2)

        player_data = api.get_player_snapshots(id=msg, period=period)

        skill_df = snapshot_to_skills(player_data)

        melt = skill_df.reset_index().melt(id_vars=['date'])
        melt["date"] = pd.to_datetime(melt["date"])

        melt.drop_duplicates(subset=["variable", "value"])

        overall = melt[melt["variable"] == "overall"]
        melt = melt[melt["variable"] != "overall"]

        filter_skills = []

        skill_array = np.array(skill_layout, dtype="object")
        n_rows, n_cols = len(skill_array[0]), len(skill_array)
        cols = st.beta_columns(n_cols-1)
        for c in range(n_cols-1):
            for r in range(n_rows):
                check = cols[c].checkbox(skill_array[c][r][1].lower())
                if check:
                    filter_skills.append(skill_array[c][r][0])

        if filter_skills:
            print(filter_skills)
            chart_data = melt[melt["variable"].isin(filter_skills)]
            print(chart_data)
        else:
            chart_data = overall
            print(chart_data)

        # Create a selection that chooses the nearest point & selects based on x-value
        nearest = alt.selection(type='single', nearest=True, on='mouseover',
                                fields=['date'], empty='none')

        # The basic line
        line = alt.Chart(chart_data).mark_line(interpolate="linear").encode(
            x='date:T',
            y='value:Q',
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
        text = line.mark_text(align='left', dx=5, dy=-5).encode(
            text=alt.condition(nearest, 'value:Q', alt.value(' '))
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

else:
    st.write("Enter a username in the side bar to get started...")
