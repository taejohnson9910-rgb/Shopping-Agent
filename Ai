from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool

# 1. Define the 'Shopping Tool' 
def search_products(query: str):
    # In a real app, this calls the Google Shopping or UCP API
    return [
        {"name": "TrailMaster X", "price": 129, "specs": "Waterproof, Wide-fit"},
        {"name": "PeakHiker Pro", "price": 145, "specs": "Waterproof, Narrow-fit"}
    ]

# 2. Setup the Agent Brain
llm = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=0) # Or DeepSeek-V3.2
tools = [
    Tool(
        name="ProductSearch",
        func=search_products,
        description="Useful for finding real-time product prices and specs."
    )
]

# 3. Initialize the Agent
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
agent.run("Find me waterproof boots for wide feet under $150.")

from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END

# 1. Define the Shared State (What the agents "remember")
class AgentState(TypedDict):
    query: str
    products: List[dict]
    critique: str
    final_decision: str

# 2. Define the Specialized Agent Nodes
def search_agent(state: AgentState):
    print("---SEARCHING PRODUCTS---")
    # Logic to call your Visual Search or UCP API
    return {"products": [{"id": 1, "name": "UltraComfort Runner", "price": 120}]}

def critic_agent(state: AgentState):
    print("---CRITIQUING PRODUCTS---")
    # Logic to analyze reviews for the found products
    return {"critique": "High comfort ratings, but 20% of users report soul wear after 3 months."}

# 3. Build the Orchestration Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("searcher", search_agent)
workflow.add_node("critic", critic_agent)

# Define Edges (The "Flow")
workflow.set_entry_point("searcher")
workflow.add_edge("searcher", "critic")
workflow.add_edge("critic", END)

# Compile the Graph
shopping_team = workflow.compile()

# 4. Run the Orchestration
inputs = {"query": "Best running shoes for marathons"}
for output in shopping_team.stream(inputs):
    print(output)
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

# 1. Define a node that requires human eyes
def human_approval_node(state):
    print("---AGENT IS PAUSING FOR YOUR REVIEW---")
    
    # The 'interrupt' function saves the state and stops execution
    # It returns whatever the human sends back via the 'Command' later
    user_decision = interrupt({
        "question": "I found these shoes for $145. Should I proceed to checkout?",
        "item_details": state["products"][0]
    })
    
    return {"final_decision": user_decision}

# 2. Compile the graph with a Checkpointer (Required for HITL)
memory = InMemorySaver()
builder = StateGraph(AgentState)
# ... add your search/critic nodes ...
builder.add_node("ask_human", human_approval_node)

# Connect the nodes
builder.add_edge("critic", "ask_human")
builder.add_edge("ask_human", END)

graph = builder.compile(checkpointer=memory)
# To resume the agent after the human says "Yes"
thread_config = {"configurable": {"thread_id": "user_123"}}

# This 'resume' value becomes the return value of the 'interrupt()' call inside the node
graph.invoke(Command(resume="Approved! Buy them."), config=thread_config)
import streamlit as st
from langgraph.types import Command

# Assume 'graph' is your compiled LangGraph shopping assistant
thread_config = {"configurable": {"thread_id": "user_unique_session_1"}}

def run_ui():
    st.title("🤖 Autonomous Shopping Agent")

    # 1. Fetch the current state of the graph
    current_state = graph.get_state(thread_config)

    # 2. Check if the agent is interrupted (waiting for human)
    if current_state.next:
        st.warning("⚠️ The Agent is waiting for your approval to proceed.")
        
        # Display what the agent found
        last_message = current_state.values.get("products", [])
        st.write("### Proposed Purchase:")
        st.json(last_message)

        # 3. The HITL Buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Approve & Buy"):
                # Resume the graph with an 'Approved' command
                graph.invoke(Command(resume="Approved"), config=thread_config)
                st.rerun()
        with col2:
            if st.button("❌ Reject / Edit"):
                user_feedback = st.text_input("What should the agent change?")
                if user_feedback:
                    graph.invoke(Command(resume=f"Rejected: {user_feedback}"), config=thread_config)
                    st.rerun()
    else:
        # Normal chat input if not interrupted
        user_input = st.chat_input("What are you looking for today?")
        if user_input:
            graph.invoke({"query": user_input}, config=thread_config)
            st.rerun()
