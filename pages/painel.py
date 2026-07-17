import pandas as pd
import streamlit as st


df = pd.DataFrame(st.session_state.historico)
st.table(df)
