import streamlit as st
import sys

# Add the path to your TQLRunner
sys.path.append('../main/')
# from TQLRunner import TQLRunner

# Function to style Streamlit elements
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
        schema = st.selectbox("Select a test schema from dropdown", ["Schema 1", "Schema 2", "Schema 3"])

        # Enter query
        query = st.text_area("Enter query:", height=200)

        if st.button("Run Query"):
            if query.strip() == "":
                st.error("Please enter a query.")
            else:
                try:
                    tqlRunner = TQLRunner(schema)
                    processed_text = tqlRunner.get_SQL_query(query)
                    st.success("SQL Query:")
                    st.code(processed_text, language="sql")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

if __name__ == '__main__':
    main()
