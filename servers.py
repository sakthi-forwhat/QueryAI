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
agent = create_sql_agent(llm, db=db, verbose=True, handle_parsing_errors=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_query = request.json.get("query")
    
    try:
        return jsonify({"answer":"success"})
        result = agent.invoke({"input": user_query})
        return jsonify({"answer": result["output"]})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)