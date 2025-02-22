import streamlit as st
import pandas as pd
import json
import datetime
from viz import process_visualization
import os
import csv

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

# File Upload
uploaded_file = st.file_uploader("Upload your Excel/CSV file", type=['csv', 'xlsx'])

if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1]

    # Handling Excel and CSV Files
    if file_type in ['csv', 'xlsx']:
        if file_type == 'csv':
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.write("Data Preview:", df.head())

# Interactive Data Exploration
st.header("Interactive Data Exploration")
columns = df.columns.tolist()
selected_columns = st.multiselect("Select columns to display", columns, default=columns)

if selected_columns:
    df_display = df[selected_columns]
    st.write("Filtered Data Preview:", df_display.head())

# Natural Language Query Input
st.header("Natural Language Query")
user_query = st.text_input("Ask your question in natural language")

def process_query(user_query, df):
    """
    This function processes a user's natural language query with simple logic
    to simulate how the query might be processed and return results.
    """
    try:
        if "sum" in user_query.lower():
            column_name = user_query.split("sum of")[-1].strip()
            if column_name in df.columns:
                return df[column_name].sum()
            else:
                return f"Column '{column_name}' not found in data."
        elif "average" in user_query.lower():
            column_name = user_query.split("average of")[-1].strip()
            if column_name in df.columns:
                return df[column_name].mean()
            else:
                return f"Column '{column_name}' not found in data."
        else:
            return "Query not recognized."
    except Exception as e:
        return f"Error processing query: {str(e)}"

if user_query:
    result = process_query(user_query, df)
    st.write("Query Result:", result)

    # Append to conversation history
    st.session_state.conversation_history.append(("You", user_query))
    st.session_state.conversation_history.append(("Chatbot", result))

    # Save to chat log
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('chat_log.csv', 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([user_query, result, timestamp])

# Visualization Query Input
st.header("Visualization Query")
viz_query = st.text_input("Enter your visualization query")

if viz_query:
    fig = process_visualization(viz_query, df)
    st.write("Generated Visualization:", fig)

    # Append to conversation history
    st.session_state.conversation_history.append(("You", viz_query))
    st.session_state.visualization_history.append(("Chatbot", fig))

    # Save to chat log
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('chat_log.csv', 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([viz_query, str(fig), timestamp])

    # Display the Plotly chart
    st.plotly_chart(fig)
