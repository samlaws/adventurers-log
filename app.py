import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from pages.skill_dash import skill_dash
from pages.boss_dash import boss_dash


def main():
    # Register your pages
    pages = {
        "Skilling Dashboard": skill_dash,
        "Bossing Dashboard": boss_dash,
    }

    st.sidebar.title("Adventurer's Log 📔")

    # Widget to select your page, you can choose between radio buttons or a selectbox
    page = st.sidebar.selectbox("Select your page", tuple(pages.keys()))
    #page = st.sidebar.radio("Select your page", tuple(pages.keys()))

    username = st.sidebar.text_input(
        "Enter a username", value='', max_chars=12).replace("-", " ")
    period = st.sidebar.selectbox('Tracking period:',
                                  ('6h', 'day', 'week', 'month', 'year'), index=2)

    # Display the selected page with the session state

    pages[page](username, period)

    st.sidebar.title("About")
    st.sidebar.info(
        """
        The source code for this web app is available on [github]
        (https://github.com/samlaws/adventurers-log), please feel free to 
        comment or make a pull request.
        """
    )


if __name__ == "__main__":
    main()
