from sqlalchemy import create_engine
import pandas as pd
import streamlit as st

@st.experimental_singleton
def _connect_db():
    db_connection_str = f"mysql+pymysql://{st.secrets['DB']['user']}:{st.secrets['DB']['pw']}@{st.secrets['DB']['host']}/{st.secrets['DB']['db_name']}"
    db_connection = create_engine(db_connection_str)
    conn = db_connection.connect()
    return db_connection

@st.experimental_memo(ttl=600)
def load_data(db_names:str|list):
    db_connection = _connect_db()
    if isinstance(db_names, str):
        return pd.read_sql_table(table_name = db_names, con = db_connection)
    else:
        df_list = []
        for db_name in db_names:
            df_list.append(pd.read_sql_table(table_name = db_name, con = db_connection))
        return df_list

@st.experimental_memo(ttl=600)   
def get_by_query(query):
    db_connection = _connect_db()
    return pd.read_sql(sql= query, con = db_connection)

@st.experimental_memo(ttl=600)
def insert_data(df, db_name):
    db_connection = _connect_db()
    df.to_sql(name= db_name, con=db_connection, if_exists='append',index=False)
