import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from langchain_mistralai import ChatMistralAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

# --- STEP 1: LOAD MISTRAL KEY ---
current_dir = Path(__file__).parent.resolve()
load_dotenv(dotenv_path=current_dir / ".env")
api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    print("❌ ERROR: MISTRAL_API_KEY not found in .env file.")
    exit()

# --- STEP 2: DATABASE SETUP (SQLite) ---
engine = create_engine("sqlite:///my_store.db")
Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    stock = Column(Integer)

Base.metadata.create_all(engine)

# Seed dummy data
Session = sessionmaker(bind=engine)
session = Session()
if session.query(Product).count() == 0:
    session.add_all([
        Product(name="Laptop", price=1200.0, stock=10),
        Product(name="Mouse", price=25.5, stock=50),
        Product(name="Keyboard", price=75.0, stock=20)
    ])
    session.commit()
session.close()

# --- STEP 3: MISTRAL AGENT SETUP ---
db = SQLDatabase.from_uri("sqlite:///my_store.db")

# Initialize Mistral
# Use 'mistral-large-latest' for best results with SQL logic
llm = ChatMistralAI(
    model="mistral-small-latest", 
    api_key=api_key, 
    temperature=0
)

# Create the SQL Agent
agent_executor = create_sql_agent(llm, db=db, verbose=True)

# --- STEP 4: RUN QUERY ---
print("\n--- MISTRAL AI DB TOOL READY ---")
user_query = "List all products that cost more than $50."

try:
    response = agent_executor.invoke({"input": user_query})
    print("\nFinal Answer:", response["output"])
except Exception as e:
    print(f"\n❌ Error: {e}")