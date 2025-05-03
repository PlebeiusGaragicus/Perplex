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
    
    # Check if we have a URL query parameter that needs processing
    if hasattr(st.session_state, 'url_search_query') and st.session_state.url_search_query:
        # Use the query from the URL
        query = st.session_state.url_search_query
        
        # Clear the URL query to prevent reprocessing
        st.session_state.url_search_query = None
        
        # Display the query that was processed from the URL
        st.info(f"Processing search query from URL: {query}")
    
    # Check if we have a search query from the discover tab or elsewhere in the session state
    elif "search_query" in st.session_state and st.session_state.search_query:
        # Use the query from session state
        query = st.session_state.search_query
        
        # Clear the session state query to prevent reprocessing
        temp_query = st.session_state.search_query
        st.session_state.search_query = None
        
        # Display the query that was processed
        st.info(f"Processing search query: {temp_query}")
    
    # Immediately display the query when submitted via chat_input
    elif query:
        # Display the query that was just submitted
        with st.chat_message("user"):
            st.markdown(query)
    
    # Process search query when submitted via chat_input or from URL
    if query:
        # Create a placeholder for the assistant's response
        assistant_placeholder = st.empty()
        
        with st.spinner("Searching..."):
            # Perform search with streaming enabled
            result = perform_search(
                query=query,
                focus_mode=st.session_state.focus_mode,
                copilot_mode=st.session_state.copilot_mode,
                conversation_id=st.session_state.active_conversation_id,
                stream=True
            )
            
            # Check if we got a streaming response (4 items in tuple) or regular response (3 items)
            if len(result) == 4:
                # Unpack streaming response
                answer_generator, sources, conversation_id, message_id = result
                
                # Update the active conversation ID
                st.session_state.active_conversation_id = conversation_id
                
                # Create a container for the assistant's response
                with assistant_placeholder.container():
                    with st.chat_message("assistant"):
                        # First, display the sources if available
                        if sources:
                            for j, source in enumerate(sources):
                                st.markdown(f"**[{j+1}]** {source['title']} - <a href='{source['url']}' target='_blank'>{source['url']}</a>", unsafe_allow_html=True)
                        
                        # Create a placeholder for the streaming text
                        message_placeholder = st.empty()
                        full_response = ""
                        
                        st.divider()
                        # Stream the response
                        for chunk, full_answer in answer_generator():
                            if chunk:  # Only update if there's new content
                                full_response = full_answer
                                message_placeholder.markdown(full_response)
                        
                        # Update the message in the database only once after streaming is complete
                        # Use the existing conversation_manager instance
                        conversation_manager.update_message_content(message_id, full_response)
                
                # Don't rerun the page - we've already shown the response
                st.session_state.clear_query = True
                
            else:
                # Regular non-streaming response
                response, sources, conversation_id = result
                
                # Update the active conversation ID
                st.session_state.active_conversation_id = conversation_id
                
                # Refresh the page to show results
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
    # if st.session_state.active_conversation_id is None:
    #     st.info("Ask a question to get started!")
    #     return
    
    # Get messages for the active conversation
    messages = conversation_manager.get_conversation_messages(st.session_state.active_conversation_id)
    
    # if not messages:
    #     st.info("Ask a question to get started!")
    #     return
    
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
                    st.divider()
                    # with st.expander(f"Sources ({len(sources)})"):
                    for j, source in enumerate(sources):
                        st.markdown(f"**[{j+1}]** {source['title']} - <a href='{source['url']}' target='_blank'>{source['url']}</a>", unsafe_allow_html=True)
            i += 1
