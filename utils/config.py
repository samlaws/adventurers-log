import string
import streamlit as st


def format_sel(label):
    return string.capwords(label.replace("_", " ")).replace("Rank", "rank")


def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()),
                    unsafe_allow_html=True)
