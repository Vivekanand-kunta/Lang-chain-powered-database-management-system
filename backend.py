import pandas as pd
import psycopg2
import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def query_generator(loc):
    """Generate SQL query from a file."""
    sql_query = ""
    with open(loc, "r") as file:
        sql_query = file.read()
    return sql_query

def server_connection(database_name, user_name, password_, host_name, port_number, file_loc):
    """Connect to the database and execute a query."""
    try:
        conn = psycopg2.connect(
            dbname=database_name,
            user=user_name,
            password=password_,
            host=host_name,
            port=port_number
        )
        cursor = conn.cursor()
        cursor.execute(query_generator(file_loc))
        data = cursor.fetchall()
        col_name = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()
        df = pd.DataFrame(data, columns=col_name)
        df.reset_index(drop=True, inplace=True)
        return df
    except psycopg2.Error as e:
        st.error(f"Database error: {e}")
        return None

def get_table_schema(dataframe):
    """Extract table schema from a dataframe."""
    required_columns = {'table_name', 'column_name', 'data_type'}
    if not required_columns.issubset(dataframe.columns):
        missing = required_columns - set(dataframe.columns)
        raise ValueError(f"Missing required columns: {missing}")
    
    schema = {}
    for _, row in dataframe.iterrows():
        table = row['table_name']
        schema.setdefault(table, []).append((row['column_name'], row['data_type']))
    return schema

def generate_sql_query(schema_text, instruction):
    """Generate an SQL query using the Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Please provide it in the sidebar.")
    
    genai.configure(api_key=api_key)
    model_name = 'gemini-1.5-pro'  # Update based on available models
    try:
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        st.error(f"Model {model_name} not available: {e}. Check API key permissions or available models.")
        raise
    
    prompt = f"""
    Given the following database schema:
    {schema_text}
    
    Generate an SQL query based on this instruction:
    {instruction}
    
    Return the SQL query inside ```sql ... ``` markers.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating SQL with model {model_name}: {e}")
        raise

def extract_sql_content(query_text):
    """Extract SQL content between ```sql ...``` markers if present."""
    import re
    pattern = r'```sql\s*(.*?)\s*```'
    match = re.search(pattern, query_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return query_text

def run_query(database_name, user_name, password_, host_name, port_number, sql_query, request_loc):
    """Run a user-provided SQL query."""
    with open(request_loc, "w") as file:
        file.write(sql_query)
    return server_connection(database_name, user_name, password_, host_name, port_number, request_loc)

def run_generated_query(database_name, user_name, password_, host_name, port_number, schema_text, instruction, request_loc):
    """Run a generated SQL query."""
    sql_query = generate_sql_query(schema_text, instruction)
    executable_sql = extract_sql_content(sql_query)
    with open(request_loc, "w") as file:
        file.write(executable_sql)
    return server_connection(database_name, user_name, password_, host_name, port_number, request_loc), sql_query
