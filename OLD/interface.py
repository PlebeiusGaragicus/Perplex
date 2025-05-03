import os
import pathlib
from PIL import Image

import streamlit as st

STATIC_PATH = pathlib.Path(__file__).parent.parent / "static"



def column_fix():
    st.write("""<style>
[data-testid="column"] {
    width: calc(33.3333% - 1rem) !important;
    flex: 1 1 calc(33.3333% - 1rem) !important;
    min-width: calc(33% - 1rem) !important;
}
</style>""", unsafe_allow_html=True)
