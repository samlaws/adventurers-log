import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import random
import os

from pages.log import log
from pages.skill_dash import skill_dash
from pages.boss_dash import boss_dash
from utils.config import format_sel, local_css


def main():

    st.set_page_config(page_title="Adventurer's Log",
                       page_icon="static/img/73.png")

    pd.options.mode.chained_assignment = None
    local_css("style.css")

    # Register your pages
    pages = {
        "Adventurer's Log": log,
        "Skilling Dashboard": skill_dash,
        "Bossing Dashboard": boss_dash,
    }

    st.sidebar.title("Adventurer's Log 📔")
    # Widget to select your page, you can choose between radio buttons or a selectbox
    page = st.sidebar.radio("Select your page", tuple(pages.keys()))
    virtual = st.sidebar.checkbox("Enable virtual levels")
    #page = st.sidebar.radio("Select your page", tuple(pages.keys()))

    # username = st.sidebar.text_input(
    # "Enter a username", value='', max_chars=12).replace("-", " ")

    username = st.sidebar.selectbox(
        "Enter a username", ["K1LLERS0FA", "Dr VinDiesel"])

    if page in ["Skilling Dashboard",  "Bossing Dashboard"]:
        period = st.sidebar.selectbox('Tracking period:',
                                      ('day', 'week', 'month', 'year'),
                                      index=1, format_func=format_sel)

        # Display the selected page with the session state
        pages[page](username, period)
    else:

        group = st.sidebar.selectbox('Group by:',
                                     ('session', 'day'),
                                     index=1, format_func=format_sel)
        pages[page](username, virtual, group)

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
