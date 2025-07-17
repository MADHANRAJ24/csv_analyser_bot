import os
import json
from groq import Groq
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

# Load .env file
load_dotenv(override=True)

# Load API key
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment!")

# Initialize Groq Client
Client = Groq(api_key=api_key)

# Correct class name to follow Python convention
class Product(BaseModel):
    html_content: str
    summary: str

# Fix: system_prompt must be used as a string, not the literal string "system_prompt"
system_prompt = """
You are a data summary & data visualizing expert. You will be shown the Users question & the csv agent's output, \
You should summarize the agents results and also plot the data with a suitable plot technique via HTML format doc content.
html_content --> used for either plots or tables, default value is ""
summary --> used for summarizing the result in a report fashion
Note: always respond with valid JSON objects that match this complete HTML structure while plotting
If the data is Not plottable, return default empty str as output in place of html_content.
Example:
{
  "html_content": "<!DOCTYPE html> ... </html>",
  "summary": "Category 1 accounts for 20% of the total. Category 2 dominates with 80% of the total."
}
Your response should ONLY contain the JSON object and nothing else.
"""

# Main function
def output_formatter(user_question, csv_agent, csv_agent_response):
    try:
        completion = Client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},  # FIXED: now uses variable
                {"role": "user", "content": f"User Question: {user_question}\nCSV Agent Output: {csv_agent_response}"}
            ]
        )

        # Get and parse JSON
        response_content = completion.choices[0].message.content
        json_data = json.loads(response_content)
        
        # Validate structure
        result = Product(**json_data)

        print("✅ Validation successful! Structured data:")
        print(json.dumps(json_data, indent=2))
        return result.html_content, result.summary

    except json.JSONDecodeError:
        print("❌ Error: The model did not return valid JSON.")
    except ValidationError as e:
        print(f"❌ Error: The JSON did not match the expected schema:\n{e}")

