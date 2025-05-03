import streamlit as st
from src.data.conversation import ConversationManager
from src.ui.common import center_text
from src.VERSION import VERSION

def render_sidebar():
    """
    Renders the sidebar navigation for Perplexed
    """
    with st.sidebar:
        st.header("🔎 :rainbow[Perplexed]", divider="rainbow")

        # Navigation tabs
        if st.button("🔍 Search", use_container_width=True, 
                    type="primary" if st.session_state.current_tab == "search" else "secondary"):
            st.session_state.active_conversation_id = None
            st.session_state.current_tab = "search"
            st.rerun()
            
        if st.button("🌐 Discover", use_container_width=True,
                    type="primary" if st.session_state.current_tab == "discover" else "secondary"):
            st.session_state.current_tab = "discover"
            st.rerun()
            
        if st.button("⚙️ Settings", use_container_width=True,
                    type="primary" if st.session_state.current_tab == "settings" else "secondary"):
            st.session_state.current_tab = "settings"
            st.rerun()
        
        # Conversation history section
        st.header("", divider="rainbow")
        st.title(":green[Conversation History]")
        # center_text(type="h2", text="Conversation history")
        
        # Initialize conversation manager
        conversation_manager = ConversationManager()
        
        # New conversation button at the top
        if st.button("New thread", use_container_width=True, type="tertiary", icon="🌱"):
            st.session_state.active_conversation_id = None
            st.session_state.current_tab = "search"
            st.rerun()
        
        # Get all conversations
        conversations = conversation_manager.get_conversations()
        
        # Display conversations as buttons
        if conversations:
            # st.divider()
            for conv in conversations:
                # Get the first user message to use as the button label
                messages = conversation_manager.get_conversation_messages(conv['id'])
                first_user_message = next((msg['content'] for msg in messages if msg['role'] == 'user'), "Untitled")
                
                # Truncate the message to 20 characters
                button_label = first_user_message[:20] + "..." if len(first_user_message) > 20 else first_user_message
                
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

        st.header("", divider="rainbow")
        st.caption(f"version: `{VERSION}`")
