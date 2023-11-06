import streamlit as st
import sys
import os
sys.path.append('../main/')
from TQLRunner import TQLRunner

sys.path.append('../utils/')
from utils import *
import requests
import json
import pandas as pd

def style():
    st.markdown(
        """
        <style>
        .st-eb {
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0px 0px 8px rgba(0, 0, 0, 0.2);
        }
        .st-cu {
            background-color: #f0f0f0;
            padding: 0.5rem;
            border-radius: 0.25rem;
        }
        .st-dp {
            padding: 1rem;
        }
        .st-eb, .st-cu {
            margin: 1rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )



def main():
    st.set_page_config(
        page_title="TQL – Text to SQL",
        page_icon="🛢️",
        layout="wide",
    )
    style()

    st.title("TQL – Text to SQL")
    
    if "old_queries" not in st.session_state:
        st.session_state['old_queries'] = []
    # Layout the sidebar for older queries
    with st.sidebar:
        st.markdown("# Older Queries")
        for i in st.session_state['old_queries']:
            for j in i:
                st.markdown(j)
            st.text('----')

    # Layout the main content area
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("New Query")

        # Select a test schema from a dropdown
        schema = st.selectbox("Select a test schema from dropdown", ["college_2", "yelp", "student_assessment"])
        q, s = get_spider_schema_table_files()
        s = s[s['schema_id'] == schema][['table_name', 'primary_key', 'column_list', 'foreign_keys']].reset_index(drop = True)
        s = s.rename(columns = {
            'table_name' : 'Name of Table', 
            'primary_key' : 'Primary Key', 
            'column_list': 'List of Columns', 
            'foreign_keys' : 'Foreign Keys'
        })
        st.dataframe(s)

        # Enter query
        query = st.text_area("Enter query:", height=200)
    
        if st.button("Run Query"):
            if query.strip() == "":
                st.error("Please enter a query.")
            else:
                # Call your function to convert TQL to SQL
                processed_text = ''
                url_api = 'https://1d73-34-69-119-5.ngrok-free.app/api/data'
                response = requests.post(url_api, json = {"schema" : schema, "query" : query})
                print(response.content)
                st.success("Generated SQL Query:")
                st.code(json.loads(response.content)['final_SQL_query'], language="sql")
                st.session_state['old_queries'].append([
                    ':gray[**Question:**] ' + query, 
                     ':gray[**SQL:**] ' + json.loads(response.content)['final_SQL_query']
                ])
                    

if __name__ == '__main__':
    main()
