import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import streamlit as st
import tempfile
import csv_agent, plotter  # Make sure these are local modules

# Load API key and env variables
load_dotenv()


# Streamlit page config
st.set_page_config(page_title="🤖📊 CSV Agent Chatbot")

st.header("🤖📊 CSV Agent", divider="rainbow")

# Chat history state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for chats in st.session_state.chat_history:
    with st.chat_message(chats["role"]):
        st.markdown(chats["content"])
        if chats["role"] == "Assistant" and chats.get("html_content"):
            with st.expander("📈📝 See explanation"):
                st.components.v1.html(chats["html_content"], height=600, scrolling=True)

# CSV File Upload
st.sidebar.header("📁 Upload a CSV File")
uploaded_file = st.sidebar.file_uploader("", type=["csv"])
temp_file_path = ""

if uploaded_file is not None:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_file_path = tmp_file.name

        st.sidebar.success("✅ File uploaded successfully!")
    except Exception as e:
        st.sidebar.error(f"❌ File upload failed: {e}")

# Chat Input
if user_input := st.chat_input("Ask a question about your CSV..."):
    # Display user message
    with st.chat_message("User"):
        st.markdown(user_input)

    st.session_state.chat_history.append({
        "role": "User",
        "content": user_input
    })

    # If no file uploaded
    if not temp_file_path:
        assistant_reply = "⚠️ Please upload a CSV file before asking questions."
        with st.chat_message("Assistant"):
            st.markdown(assistant_reply)
        st.session_state.chat_history.append({
            "role": "Assistant",
            "content": assistant_reply,
            "html_content": ""
        })
    else:
        # Run CSV agent and formatter
        try:
            csv_agent_response = csv_agent.csv_agent_invoker(temp_file_path, user_input)
            html_content, response = plotter.output_formatter(user_input, csv_agent_response)

            # Display assistant reply
            with st.chat_message("Assistant"):
                st.markdown(response)
                if html_content:
                    with st.expander("📈📝 See explanation"):
                        st.components.v1.html(html_content, height=600, scrolling=True)

            st.session_state.chat_history.append({
                "role": "Assistant",
                "content": response,
                "html_content": html_content
            })
        except Exception as e:
            with st.chat_message("Assistant"):
                st.error(f"❌ Error processing your request: {e}")
            st.session_state.chat_history.append({
                "role": "Assistant",
                "content": f"Error: {e}",
                "html_content": ""
            })
