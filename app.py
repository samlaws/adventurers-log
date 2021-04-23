import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from utils.api import ApiMethods
from utils.snapshot_wrangling import snapshot_to_skills
from utils.config import skill_layout
from pages.skill_dash import skill_dash


def main():
    # Register your pages
    pages = {
        "Skilling Dashboard": skill_dash,
        "Bossing Dashboard": page_second,
    }

    st.sidebar.title("Adventurer's Log")

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
        comment and pull request.
        """
    )


def page_first(username, period):
    pass


def page_second(username, period):
    # ...
    pass


if __name__ == "__main__":
    main()
