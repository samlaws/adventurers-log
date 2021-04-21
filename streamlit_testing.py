import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from vega_datasets import data

from api_testing import ApiMethods
from snapshots_to_pandas import snapshot_to_skills
from utils import load_skill_icons

username = st.sidebar.text_input("Enter a username", value='', max_chars=12)
# username = "pompelmo"
if username:
    api = ApiMethods(username=username)

    status, msg = api.check_player_exists()
    if status:
        st.sidebar.write("Player found")

        period = st.selectbox('Tracking period:',
                              ('6h', 'day', 'week', 'month', 'year'), index=2)

        skill_layout = load_skill_icons()

        player_data = api.get_player_snapshots(id=msg, period=period)

        try:
            skill_df = snapshot_to_skills(player_data)

            melt = skill_df.reset_index().melt(id_vars=['date'])
            melt["date"] = pd.to_datetime(melt["date"])
            overall = melt[melt["variable"] == "overall"]
            melt = melt[melt["variable"] != "overall"]

            cols = st.beta_columns((1, 1, 1, 7))

            # create tilegrid with select boxes for each skill
            # can then filter 'melt' by those skills in the chart
            filter_skills = []
            for row in skill_layout:
                for i in range(len(row)):
                    # st.image(row[i][1]))
                    check = cols[i].checkbox(row[i][0])
                    if check:
                        filter_skills.append(row[i][0])

            print(filter_skills)

            if filter_skills:
                chart_data = melt[melt["variable"].isin(filter_skills)]
            else:
                chart_data = overall

            c = alt.Chart(chart_data).mark_line(point=True).encode(
                x='date',
                y='value',
                color='variable'
            )

            cols[3].altair_chart(c, use_container_width=True)

        except IndexError:
            st.write("No data available from that period")

    else:
        st.sidebar.write("Player not found")
