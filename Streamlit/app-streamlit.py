import streamlit as st
from TQLRunner import TQLRunner  # Import your TQLRunner class from '../main/'

def main():
    st.title("TQL – Text to SQL")

    # Select a test schema from a dropdown
    schema = st.selectbox("Select a test schema from dropdown", ["Schema 1", "Schema 2", "Schema 3"])
    
    # Enter query
    query = st.text_input("Enter query:")

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

    # Display older queries (you can replace this with actual queries if needed)
    st.markdown("## Older Queries")
    st.text("Query 1: SELECT * FROM table1 WHERE column1 = 'value1'")
    st.text("Query 2: SELECT column1, column2 FROM table2 WHERE column3 = 'value2'")
    st.text("Query 3: ...")

if __name__ == '__main__':
    main()
