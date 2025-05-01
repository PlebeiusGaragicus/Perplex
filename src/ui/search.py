import streamlit as st
from src.agents.search_agent import perform_search
from src.utils.history import add_to_history, get_conversation_history

def render_search_interface():
    """
    Renders the main search interface for Perplexica
    """
    st.title("Perplexica Search")
    
    # Focus mode indicator
    focus_mode_labels = {
        "all": "All Web Search",
        "writing": "Writing Assistant",
        "academic": "Academic Search",
        "youtube": "YouTube Search",
        "wolfram": "Wolfram Alpha",
        "reddit": "Reddit Search"
    }
    
    # Display current mode
    mode_text = f"Mode: {focus_mode_labels[st.session_state.focus_mode]}"
    if st.session_state.copilot_mode:
        mode_text += " (Copilot Enabled)"
    st.markdown(f"**{mode_text}**")
    
    # Search input
    with st.form(key="search_form", clear_on_submit=True):
        query = st.text_input("Ask anything...", key="search_query")
        col1, col2 = st.columns([6, 1])
        with col1:
            submit_button = st.form_submit_button("Search", use_container_width=True)
        with col2:
            clear_button = st.form_submit_button("Clear", use_container_width=True)
    
    # Handle clear button
    if clear_button:
        st.session_state.conversation_history = []
        st.rerun()
    
    # Process search query
    if submit_button and query:
        with st.spinner("Searching..."):
            # Perform search based on focus mode and copilot mode
            response, sources = perform_search(
                query=query,
                focus_mode=st.session_state.focus_mode,
                copilot_mode=st.session_state.copilot_mode
            )
            
            # Add to conversation history
            add_to_history(query, response, sources)
            
            # The form's clear_on_submit=True will handle clearing the input
    
    # Display conversation history
    display_conversation_history()

def display_conversation_history():
    """
    Displays the conversation history with expandable source citations
    """
    history = get_conversation_history()
    
    if not history:
        st.info("Ask a question to get started!")
        return
    
    for i, (query, response, sources) in enumerate(reversed(history)):
        # User query
        with st.chat_message("user"):
            st.markdown(query)
        
        # Assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
            
            # Display sources if available
            if sources:
                with st.expander("Sources"):
                    for j, source in enumerate(sources):
                        st.markdown(f"**[{j+1}] {source['title']}**")
                        st.markdown(f"[{source['url']}]({source['url']})")
                        if 'content' in source:
                            st.markdown(f"_{source['content']}_")
                        st.markdown("---")
