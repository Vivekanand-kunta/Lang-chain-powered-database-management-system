import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import backend
import plotting
import styles
import os
from dotenv import load_dotenv

# Load environment variables from .env file (optional for local testing)
load_dotenv()

# File locations (relative paths)
schema_file_loc = "sql_query/sql_query_schema.txt"
request_loc = "sql_query/sql_query_request.txt"

# Set page config
st.set_page_config(layout="wide")
st.markdown(styles.get_sidebar_css(), unsafe_allow_html=True)

# Custom CSS for sidebar contact button and details with dark theme
st.markdown(
    """
    <style>
    .contact-button {
        width: 100%;
        padding: 5px 15px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        margin-bottom: 10px;
    }
    .contact-button:hover {
        background-color: #45a049;
    }
    .contact-details {
        background-color: #1a1a1a; /* Dark theme background */
        color: #ffffff; /* White text for contrast */
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.5);
        display: none;
        margin-top: 5px;
    }
    .contact-details.visible {
        display: block;
    }
    a {
        color: #1e90ff; /* Light blue for links in dark theme */
    }
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    # One-time message for database details
    if 'show_db_message' not in st.session_state:
        st.warning("**Please add your database details in the 'Database Connection' section below.**")
        st.session_state['show_db_message'] = True

    st.title("Data Visualization Dashboard")

    # Sidebar controls
    st.sidebar.title("Controls")

    # Contact button and details at top of sidebar
    if st.sidebar.button("Contact", key="contact_button", help="Click to view contact details", type="primary"):
        st.session_state['show_contact'] = not st.session_state.get('show_contact', False)

    if st.session_state.get('show_contact', False):
        st.sidebar.markdown(
            """
            <div class="contact-details visible">
                <strong>Vivekanandreddy</strong><br>
                <a href="mailto:vivekanandreddy05@gmail.com" style="color: #1e90ff;">vivekanandreddy05@gmail.com</a>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Database connection inputs
    st.sidebar.subheader("Database Connection")
    database_name = st.sidebar.text_input("Database Name", value="Vivekanand_bikes-Database")
    user_name = st.sidebar.text_input("Username", value="vivek")
    password_ = st.sidebar.text_input("Password", type="password", value="1234567890")
    host_name = st.sidebar.text_input("Host", value="localhost")
    port_number = st.sidebar.text_input("Port", value="5432")

    # API Key input
    st.sidebar.subheader("API Configuration")
    api_key = st.sidebar.text_input("Google Gemini API Key", type="password", value="")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key

    # Database controls
    st.sidebar.subheader("Data")
    if st.sidebar.button("Show/Hide Schema", type="primary"):
        st.session_state['show_schema'] = not st.session_state.get('show_schema', False)

    # Query controls
    st.sidebar.subheader("Queries")
    if st.sidebar.button("Enter SQL Query", type="primary"):
        st.session_state['show_input'] = not st.session_state.get('show_input', False)
    if st.session_state.get('show_input', False):
        sql_query = st.sidebar.text_area("Enter SQL Query", height=200)
        if st.sidebar.button("Run Query", type="primary"):
            with st.spinner("Executing query..."):
                dataframe = backend.run_query(database_name, user_name, password_, host_name, port_number, sql_query, request_loc)
                if dataframe is not None:
                    st.session_state['dataframe'] = dataframe
                    st.success("Query executed successfully!")

    # QueryCraft section (renamed to Enter Prompt)
    if st.sidebar.button("Enter Prompt", type="primary"):
        st.session_state['show_querycraft'] = not st.session_state.get('show_querycraft', False)
    if st.session_state.get('show_querycraft', False):
        text_instruction = st.sidebar.text_area("Enter your query requirement", height=100)
        if st.sidebar.button("Run Generated Query", type="primary"):
            if not api_key:
                st.sidebar.error("Please enter a Google Gemini API Key to use this feature.")
            elif 'schema_text' in st.session_state and text_instruction:
                with st.spinner("Generating and executing query..."):
                    try:
                        dataframe, sql_query = backend.run_generated_query(database_name, user_name, password_, host_name, port_number, st.session_state['schema_text'], text_instruction, request_loc)
                        st.session_state['generated_sql'] = sql_query
                        if dataframe is not None:
                            st.session_state['dataframe'] = dataframe
                            st.success("Query executed successfully!")
                            st.session_state['query_error'] = False
                        else:
                            st.error("Failed to execute the generated query.")
                            st.session_state['query_error'] = True
                    except Exception as e:
                        st.error(f"Error generating or executing SQL: {e}")
                        st.session_state['query_error'] = True
                        st.session_state['generated_sql'] = sql_query if 'sql_query' in locals() else ""
            else:
                st.sidebar.error("Please display the schema first and enter a query requirement.")

        if 'generated_sql' in st.session_state:
            if st.sidebar.button("Show/Hide Generated SQL", type="secondary"):
                st.session_state['show_generated_sql'] = not st.session_state.get('show_generated_sql', False)
            
            if st.session_state.get('show_generated_sql', False):
                st.sidebar.text_area("Generated SQL Query", 
                                   value=st.session_state['generated_sql'], 
                                   height=150, 
                                   disabled=True)

        if st.session_state.get('query_error', False) and 'generated_sql' in st.session_state:
            st.sidebar.subheader("Generated SQL (Error Occurred)")
            edited_sql = st.sidebar.text_area("Edit SQL Query", value=st.session_state['generated_sql'], height=200)
            if st.sidebar.button("Rerun Edited Query", type="primary"):
                with st.spinner("Executing edited query..."):
                    dataframe = backend.run_query(database_name, user_name, password_, host_name, port_number, edited_sql, request_loc)
                    if dataframe is not None:
                        st.session_state['dataframe'] = dataframe
                        st.session_state['query_error'] = False
                        st.success("Edited query executed successfully!")
                    else:
                        st.error("Failed to execute the edited query")

    # Visualization controls
    st.sidebar.subheader("Visualizations")
    graph_types = {
        "Line Plot": "lineplot",
        "Distribution Plot": "displot",
        "Bar Plot": "barplot",
        "Scatter Plot": "scatterplot",
        "Heatmap": "heatmap",
        "Violin Plot": "violinplot",
        "Strip Plot": "striplot",
        "Box Plot": "boxplot",
        "Pie Chart": "pie"
    }
    selected_graph = st.sidebar.selectbox("Map Options", list(graph_types.keys()))
    plot_title = st.sidebar.text_input("Plot Title", "My Visualization")
    
    if 'dataframe' in st.session_state:
        column_names = st.session_state['dataframe'].columns
        x_axis = st.sidebar.selectbox("Select X-Axis", column_names)
        y_axis = st.sidebar.selectbox("Select Y-Axis", column_names)

    if st.sidebar.button("Run", type="primary") and 'dataframe' in st.session_state:
        dataframe = st.session_state['dataframe']
        with st.spinner("Generating plot..."):
            if x_axis not in dataframe.columns or y_axis not in dataframe.columns:
                st.error("Invalid axis selection")
            else:
                fig = plotting.plotting_function(dataframe, graph_types[selected_graph], y_axis, x_axis, title=plot_title)
            if fig is not None:
                st.session_state['plot'] = fig

    # Reset button below graph options in sidebar
    if st.sidebar.button("Reset", type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.sidebar.success("Session reset successfully!")

    # Main content area
    if st.session_state.get('show_schema', False):
        with st.spinner("Loading schema..."):
            dataframe = backend.server_connection(database_name, user_name, password_, host_name, port_number, schema_file_loc)
            if dataframe is not None:
                tables_dfs = backend.get_table_schema(dataframe)
                st.subheader("Schema")
                
                num_tables = len(tables_dfs)
                cols = st.columns(3)
                
                st.markdown(styles.get_schema_css(), unsafe_allow_html=True)
                
                schema_text = ""
                for table_name, columns in tables_dfs.items():
                    schema_text += f"Table: {table_name}\n"
                    schema_text += "Columns:\n"
                    for col in columns:
                        schema_text += f"- {col[0]} ({col[1]})\n"
                    schema_text += "\n"
                st.session_state['schema_text'] = schema_text
                
                for idx, (table_name, columns) in enumerate(tables_dfs.items()):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        st.markdown(f'<span class="table-name">Table: {table_name}</span>', unsafe_allow_html=True)
                        df = pd.DataFrame(columns, columns=['Column_Name', 'Data_Type'])
                        table_html = df.to_html(
                            classes='schema-table',
                            index=False,
                            justify='left'
                        )
                        st.markdown(table_html, unsafe_allow_html=True)

    if 'dataframe' in st.session_state:
        st.subheader("Query Results")
        st.write("Data preview:")
        st.markdown(styles.get_schema_css(), unsafe_allow_html=True)
        query_html = st.session_state['dataframe'].head().to_html(
            classes='schema-table',
            index=False,
            justify='left'
        )
        st.markdown(query_html, unsafe_allow_html=True)

    if 'plot' in st.session_state:
        st.subheader("Visualization")
        st.pyplot(st.session_state['plot'])

if __name__ == "__main__":
    main()
