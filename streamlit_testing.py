import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from vega_datasets import data

from api_testing import ApiMethods
from snapshots_to_pandas import snapshot_to_skills

# username = st.sidebar.text_input("Enter a username", value='', max_chars=12)
username = "pompelmo"
if username:
    api = ApiMethods(username=username)

    status, msg = api.check_player_exists()
    if status:
        st.sidebar.write("Player found")

        period = st.selectbox('Tracking period:',
                              ('6h', 'day', 'week', 'month', 'year'), index=2)
        player_data = api.get_player_snapshots(id=msg, period=period)

        try:
            skill_df = snapshot_to_skills(player_data)

            # Dropping overall to fix the scaling temporarily
            skill_df.drop(columns=["overall"], inplace=True)

            melt = skill_df.reset_index().melt(id_vars=['date'])
            melt["date"] = pd.to_datetime(melt["date"])

            col1, col2 = st.beta_columns(2)

            skills = melt["variable"].unique()
            # create tilegrid with select boxes for each skill
            # can then filter 'melt' by those skills in the chart

            c = alt.Chart(melt).mark_line(point=True).encode(
                x='date',
                y='value',
                color='variable'
            )

            col2.altair_chart(c, use_container_width=True)

        except IndexError:
            st.write("No data available from that period")

    else:
        st.sidebar.write("Player not found")
