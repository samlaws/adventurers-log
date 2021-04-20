import streamlit as st
from api_testing import ApiMethods
from snapshots_to_pandas import snapshot_to_skills

username = st.sidebar.text_input("Enter a username", value='', max_chars=12)
if username:
    api = ApiMethods(username=username)

    status, msg = api.check_player_exists()
    if status:
        st.sidebar.write("Player found")

        period = st.selectbox('Tracking period:',
                              ('6h', 'day', 'week', 'month', 'year'), index=0)
        player_data = api.get_player_snapshots(id=msg, period=period)

        try:
            skill_df = snapshot_to_skills(player_data)
            skill = st.selectbox('Skill:',
                                 (skill_df.columns), index=0)
            slice_df = skill_df[skill]
            st.line_chart(slice_df)

        except IndexError:
            st.write("No data available from that period")

    else:
        st.sidebar.write("Player not found")
