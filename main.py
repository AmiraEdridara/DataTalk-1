import streamlit as st
import pandas as pd
from query_engine import process_query
from viz import process_visualization
from sqlalchemy import create_engine, inspect
import os
import csv
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import json

# App Title
st.title('DataTalk: Natural Language to Data Query')

# Initialize conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Initialize visualization history
if 'visualization_history' not in st.session_state:
    st.session_state.visualization_history = []

# Function to initialize chat log file
def initialize_chat_log():
    if not os.path.exists('chat_log.csv'):
        with open('chat_log.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['User Query', 'Chatbot Response', 'Timestamp'])

# Initialize chat log file
initialize_chat_log()

# Tabs for Data Query, Conversation History, and Visualization History
tab1, tab2, tab3 = st.tabs(["Data Query", "Conversation History", "Visualization History"])

with tab1:
    # File Upload
    uploaded_file = st.file_uploader("Upload your Excel/CSV/SQL file", type=['csv', 'xlsx', 'sql'])

    if uploaded_file:
        file_type = uploaded_file.name.split('.')[-1]

        # Handling Excel and CSV Files
        if file_type in ['csv', 'xlsx']:
            if file_type == 'csv':
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.write("Data Preview:", df.head())

        # Handling SQL Files
        elif file_type == 'sql':
            # Ensure the 'data' directory exists
            if not os.path.exists('data'):
                os.makedirs('data')

            # Save file to local storage
            file_path = os.path.join('data', uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                engine = create_engine(f'sqlite:///{file_path}')
                inspector = inspect(engine)
                table_names = inspector.get_table_names()
                st.write("Available Tables:", table_names)

                # Selecting Table
                selected_table = st.selectbox("Select Table", table_names)
                query = f"SELECT * FROM {selected_table} LIMIT 5"
                df = pd.read_sql_query(query, engine)
                st.write("Data Preview:", df.head())
            except Exception as e:
                st.error(f"Error reading SQL file: {e}")

        # Natural Language Query Input
        user_query = st.text_input("Ask your question in natural language")

        if user_query:
            result_df = process_query(user_query, df)
            st.write("Query Result:", result_df)

            # Append to conversation history
            st.session_state.conversation_history.append(("You", user_query))
            
            # Convert result to string based on its type
            if isinstance(result_df, pd.DataFrame):
                result_str = result_df.to_string()
            elif isinstance(result_df, (int, float)):
                result_str = str(result_df)
            elif isinstance(result_df, pd.Series):
                result_str = result_df.to_string()
            elif isinstance(result_df, dict):
                result_str = json.dumps(result_df, indent=4)
            elif isinstance(result_df, tuple):
                result_str = str(result_df)
            elif isinstance(result_df, list):
                result_str = ", ".join(map(str, result_df))
            else:
                result_str = "⚠️ No valid result found."

            st.session_state.conversation_history.append(("Chatbot", result_str))

            # Save to chat log
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open('chat_log.csv', 'a', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([user_query, result_str, timestamp])
        
        # Visualization Query Input
        viz_query = st.text_input("Enter your visualization query")
        if viz_query:
            code = process_visualization(viz_query, df)
            st.write("Generated Code:", code)

            # Append to conversation history
            st.session_state.conversation_history.append(("You", viz_query))
            st.session_state.conversation_history.append(("Chatbot", code))

            # Save to chat log
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open('chat_log.csv', 'a', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([viz_query, code, timestamp])

            # Execute the generated code
            safe_globals = {"df": df, "pd": pd, "plt": plt, "sns": sns}
            try:
                exec(code, safe_globals)
                if 'fig' in safe_globals:
                    st.pyplot(safe_globals['fig'])
                    # Append to visualization history
                    st.session_state.visualization_history.append((viz_query, safe_globals['fig']))
                elif 'result' in safe_globals:
                    st.write(safe_globals['result'])
                else:
                    st.write("⚠️ No valid result found.")
            except Exception as e:
                st.error(f"Error executing the generated code: {e}")

with tab2:
    st.header("Conversation History:")
    
    # Display conversation history from session state
    for speaker, text in st.session_state.conversation_history:
        st.markdown(f"**{speaker}:** {text}")

    # Display conversation history from chat log file
    if os.path.exists('chat_log.csv'):
        with open('chat_log.csv', 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader, None)  # Skip header
            for row in csv_reader:
                st.text(f"User: {row[0]}")
                st.text(f"Chatbot: {row[1]}")
                st.text(f"Timestamp: {row[2]}")
                st.markdown("----")

with tab3:
    st.header("Visualization History:")
    
    # Display visualization history from session state
    for query, fig in st.session_state.visualization_history:
        st.markdown(f"**Query:** {query}")
        st.pyplot(fig)
        st.markdown("----")
