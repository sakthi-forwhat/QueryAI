from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

load_dotenv()
app = Flask(__name__)

# Initialize our Agent logic once
db = SQLDatabase.from_uri("sqlite:///my_store.db")
llm = ChatMistralAI(model="mistral-small-latest", temperature=0)
# Update your agent creation code
agent = create_sql_agent(
    llm, 
    db=db, 
    verbose=True, 
    # 1. This handles the specific error you saw
    handle_parsing_errors=True, 
    # 2. Helps the model focus on the final answer
    max_iterations=2 
)

@app.route('/')
def home():
    return render_template('index.html')

import re

@app.route('/ask', methods=['POST'])
def ask():
    user_query = request.json.get("query", "").strip()
    
    # Simple greeting check
    if user_query.lower() in ["hi", "hello", "hey"]:
        return jsonify({"answer": "Hello! How can I help with your data today?"})

    try:
        # Standard execution
        result = agent.invoke({"input": user_query})
        return jsonify({"answer": result["output"]})
    
    except Exception as e:
        error_msg = str(e)
        
        # Check if the error contains a partial answer
        if "Could not parse LLM output: `" in error_msg:
            # Extract content between the backticks
            # This is where the AI's actual answer is hidden
            extracted_answer = error_msg.split("Could not parse LLM output: `")[-1].rstrip("`")
            
            # Remove any trailing "Thought:" or technical snippets if they exist
            clean_answer = extracted_answer.split("Thought:")[0].strip()
            
            return jsonify({"answer": clean_answer})
        
        # If it's a different kind of error, return it normally
        return jsonify({"answer": f"System Note: {error_msg}"}), 500

if __name__ == '__main__':
    app.run(debug=True)