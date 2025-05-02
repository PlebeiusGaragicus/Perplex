import streamlit as st
from src.agents.search_agent import perform_search
from src.data.conversation import ConversationManager


def center_text(type, text, size=None):
    if size == None:
        st.write(f"<{type} style='text-align: center;'>{text}</{type}>", unsafe_allow_html=True)
    else:
        st.write(f"<{type} style='text-align: center; font-size: {size}px;'>{text}</{type}>", unsafe_allow_html=True)


def render_search_interface():

    """
    Renders the main search interface for Perplexica
    """
    # Initialize conversation manager
    conversation_manager = ConversationManager()
    
    # Initialize session state variables
    if "active_conversation_id" not in st.session_state:
        st.session_state.active_conversation_id = None
    if "conversations" not in st.session_state:
        st.session_state.conversations = []
    if "clear_query" not in st.session_state:
        st.session_state.clear_query = False
        
    # Handle clearing the search query if needed
    if st.session_state.clear_query:
        # This needs to happen before any widgets are rendered
        if "search_query" in st.session_state:
            del st.session_state["search_query"]
        st.session_state.clear_query = False
    
    # Conversation history is now handled in sidebar.py
    
    # Main content area
    # st.title("Perplexica Search")
    center_text(type="h1", text="Perplexity Search")
    
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
    # mode_text = f"Mode: {focus_mode_labels[st.session_state.focus_mode]}"
    # st.markdown(f"**{mode_text}**")

    # Copilot mode toggle in the main area with improved explanation
    copilot_enabled = st.toggle("Enable Copilot Mode", value=st.session_state.copilot_mode)
    if copilot_enabled != st.session_state.copilot_mode:
        st.session_state.copilot_mode = copilot_enabled
        st.rerun()

    # Update conversations in session state
    conversations = conversation_manager.get_conversations()
    if conversations:
        st.session_state.conversations = conversations
    
    # Search input - use a simpler approach without form to ensure Enter key works
    if st.session_state.active_conversation_id is not None:
        placeholder_text = "Ask a follow-up question..."
    else:
        placeholder_text = "Ask anything..."
    
    # Display current conversation status
    if st.session_state.active_conversation_id is not None:
        messages = conversation_manager.get_conversation_messages(st.session_state.active_conversation_id)
        first_user_message = next((msg['content'] for msg in messages if msg['role'] == 'user'), "Untitled")
        st.caption(f"Current conversation: '{first_user_message[:30]}...' (ID: {st.session_state.active_conversation_id})")
    
    # Display conversation history first
    display_conversation_history(conversation_manager)
    
    # Use chat_input at the bottom of the page (it will automatically appear at the bottom)
    query = st.chat_input(placeholder_text)
    
    # Process search query when submitted via chat_input
    if query:
        
        with st.spinner("Searching..."):
            # Perform search based on focus mode and copilot mode
            response, sources, conversation_id = perform_search(
                query=query,
                focus_mode=st.session_state.focus_mode,
                copilot_mode=st.session_state.copilot_mode,
                conversation_id=st.session_state.active_conversation_id
            )
            
            # Update the active conversation ID
            st.session_state.active_conversation_id = conversation_id
            
            # Refresh the page to show results
            # We'll use a flag to clear the query on the next run
            st.session_state.clear_query = True
            st.rerun()
    
    # We've already displayed the conversation history above

def display_conversation_history(conversation_manager):
    """
    Displays the conversation history with expandable source citations
    
    Args:
        conversation_manager (ConversationManager): The conversation manager instance
    """
    # If no active conversation, show a prompt to start
    if st.session_state.active_conversation_id is None:
        st.info("Ask a question to get started!")
        return
    
    # Get messages for the active conversation
    messages = conversation_manager.get_conversation_messages(st.session_state.active_conversation_id)
    
    if not messages:
        st.info("Ask a question to get started!")
        return
    
    # Group messages by user/assistant pairs
    i = 0
    while i < len(messages):
        # User message
        if i < len(messages) and messages[i]['role'] == 'user':
            with st.chat_message("user"):
                st.markdown(messages[i]['content'])
            i += 1
        
        # Assistant response
        if i < len(messages) and messages[i]['role'] == 'assistant':
            with st.chat_message("assistant"):
                st.markdown(messages[i]['content'])
                
                # Display sources if available
                if 'sources' in messages[i] and messages[i]['sources']:
                    sources = messages[i]['sources']
                    with st.expander(f"Sources ({len(sources)})"):
                        for j, source in enumerate(sources):
                            st.markdown(f"**[{j+1}] {source['title']}**")
                            if source['url']:
                                st.markdown(f"[{source['url']}]({source['url']})")
                            if source['content']:
                                st.markdown(f"_{source['content']}_")
                            st.divider()
            i += 1
