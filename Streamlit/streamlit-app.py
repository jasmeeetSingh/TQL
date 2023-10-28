import streamlit as st
import sys
import os
from transformers import AutoModelForCausalLM, AutoConfig, AutoTokenizer, pipeline

import sys
sys.path.append('../main/')
from TQLRunner import TQLRunner

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

def format_example(example):
    instruction = (
        "Given the context, answer the question by writing the appropriate SQL code."
    )
    q_header = "### Question"
    a_header = "### Answer"

    q = example

    return f"{instruction}\n\n{q_header}\n{q}\n\n{a_header}\n"

def run_tql_to_sql(query):
    try:
        # Load the adapter configuration from the provided URL
        adapter_config_url = 'https://huggingface.co/naman1011/TQL/raw/main/adapter_config.json'
        adapter_config = AutoConfig.from_pretrained(adapter_config_url)
        
        # Load the model using the adapter configuration
        model = AutoModelForCausalLM.from_pretrained('naman1011/TQL', config=adapter_config)
        tokenizer = AutoTokenizer.from_pretrained('naman1011/TQL')

        # Format the user's query
        prompt = format_example(query)
        
        # Generate SQL query using the model
        pipe = pipeline(task="text-generation", model=model, tokenizer=tokenizer)
        generated_text = pipe(f"<s>[INST] {prompt} [/INST]")[0]['generated_text']
        
        return generated_text
    except Exception as e:
        return str(e)

def main():
    st.set_page_config(
        page_title="TQL – Text to SQL",
        page_icon="🛢️",
        layout="wide",
    )
    style()

    st.title("TQL – Text to SQL")

    # Layout the sidebar for older queries
    with st.sidebar:
        st.markdown("## Older Queries")
        st.text("Query 1: SELECT * FROM table1 WHERE column1 = 'value1'")
        st.text("Query 2: SELECT column1, column2 FROM table2 WHERE column3 = 'value2'")
        st.text("Query 3: ...")

    # Layout the main content area
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("New Query")

        # Select a test schema from a dropdown
        schema = st.selectbox("Select a test schema from dropdown", ["college_2", "Schema 2", "Schema 3"])

        # Enter query
        query = st.text_area("Enter query:", height=200)
    
        if st.button("Run Query"):
            if query.strip() == "":
                st.error("Please enter a query.")
            else:
                # Call your function to convert TQL to SQL
                processed_text = ''
                try: 
                    tqlRunner = TQLRunner(schema)
                    processed_text = tqlRunner.get_SQL_query(query)
                    # generated_sql = run_tql_to_sql(query)
                    st.success("Generated SQL Query:")
                    st.code(processed_text, language="sql")

if __name__ == '__main__':
    main()
