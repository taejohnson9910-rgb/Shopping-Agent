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
