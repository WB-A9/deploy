import streamlit as st
from st_aggrid import AgGrid,GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import pandas as pd

def aggrid_interactive_table(df: pd.DataFrame):
    """Creates an st-aggrid interactive table based on a dataframe.

    Args:
        df (pd.DataFrame]): Source dataframe

    Returns:
        dict: The selected row
    """
    options = GridOptionsBuilder.from_dataframe(
        df,enableRowGroup=True,enableValue=True,enablePivot=True
    )

    options.configure_side_bar()

    options.configure_selection("None")
    
    selection = AgGrid(
        df, enable_enterprise_modules=True, gridOptions=options.build(), theme="streamlit", fit_columns_on_grid_load = True, update_mode=GridUpdateMode.MODEL_CHANGED, allow_unsafe_jscode=True)

    return selection

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')
