import streamlit as st
from src.agents.search_agent import perform_search
from src.data.conversation import ConversationManager

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
    
    # Sidebar for conversation history
    with st.sidebar:
        st.title("Conversations")
        
        # New conversation button at the top
        if st.button("+ New Conversation", use_container_width=True, type="primary"):
            st.session_state.active_conversation_id = None
            st.rerun()
        
        # Get all conversations
        conversations = conversation_manager.get_conversations()
        
        # Display conversations as buttons
        if conversations:
            st.divider()
            for conv in conversations:
                # Get the first user message to use as the button label
                messages = conversation_manager.get_conversation_messages(conv['id'])
                first_user_message = next((msg['content'] for msg in messages if msg['role'] == 'user'), "Untitled")
                
                # Truncate the message to 12 characters
                button_label = first_user_message[:12] + "..." if len(first_user_message) > 12 else first_user_message
                
                # Highlight the active conversation
                is_active = st.session_state.active_conversation_id == conv['id']
                button_type = "primary" if is_active else "secondary"
                
                # Create a container for each conversation with delete option
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    # Main conversation button
                    with col1:
                        if st.button(button_label, key=f"conv_{conv['id']}", use_container_width=True, type=button_type):
                            st.session_state.active_conversation_id = conv['id']
                            st.rerun()
                    
                    # Delete button
                    with col2:
                        if st.button("🗑️", key=f"del_{conv['id']}"):
                            conversation_manager.delete_conversation(conv['id'])
                            if st.session_state.active_conversation_id == conv['id']:
                                st.session_state.active_conversation_id = None
                            st.rerun()
        else:
            st.info("No conversations yet")
    
    # Main content area
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
                
                # Try to extract citation information
                # This is a simple heuristic - in a real app you might want to store citations separately
                response_text = messages[i]['content']
                if '[1]' in response_text:  # Check if there are citations
                    with st.expander("Sources"):
                        st.markdown("Citation information is available in the response above.")
                        st.markdown("For a more complete implementation, we would store and display the actual sources here.")
            i += 1
