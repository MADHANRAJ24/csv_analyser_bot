import os
from dotenv import load_dotenv
from langchain_experimental.agents import create_csv_agent
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv(override=True)

# Get API Key from environment
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment. Make sure it's set in your .env file.")

# Define available models
model1 = "llama3-70b-8192"
model2 = "gemma2-9b-it"
model3 = "llama-3.3-70b-versatile"
model4 = "deepseek-r1-distill-llama-70b"

# Instantiate Groq model
model = ChatGroq(
    model_name=model2,
    api_key=groq_api_key,
    temperature=0.5
)

# Function to run query on CSV
def csv_agent(csv_file_name, user_query):
    agent = create_csv_agent(
        llm=model,
        path=csv_file_name,
        verbose=True,
        allow_dangerous_code=True  # Fixed typo from "allow_dangeros_code"
    )
    response = agent.run(user_query)
    return response
