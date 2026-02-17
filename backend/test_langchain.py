import pandas as pd
from langchain_ollama import ChatOllama
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import os

# Create dummy data
data = {'Store': ['A', 'B', 'A'], 'Qty': [10, 20, 30]}
df = pd.DataFrame(data)

llm = ChatOllama(model="llama3.2", base_url="http://localhost:11434")

agent = create_pandas_dataframe_agent(
    llm,
    df,
    verbose=True,
    allow_dangerous_code=True,
    agent_type="openai-tools"
)

try:
    response = agent.invoke("What is the total quantity?")
    print("RESPONSE:", response["output"])
except Exception as e:
    print("ERROR:", str(e))
