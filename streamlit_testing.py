import streamlit as st
from api_testing import ApiMethods

username = st.text_input("Enter a username", value='', max_chars=12)
if username:
    api = ApiMethods(username=username)

    status, msg = api.check_player_exists()
    if status:
        st.write(msg)
        player_data = api.get_player_details(id=msg)
        rc_exp = player_data["latestSnapshot"]["runecrafting"]["experience"]
        if rc_exp > 13034000:
            st.write("CHAD ALERT 🇹🇩 - %s has 99 Runecrafting! 🙏" % username)
        else:
            st.write("Watch out this guy doesnt even have 99 Runecrafting! 🤮")

    else:
        st.write("Player not found")
