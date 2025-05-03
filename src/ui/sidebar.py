import streamlit as st
from src.data.conversation import ConversationManager

def render_sidebar():
    """
    Renders the sidebar navigation for Perplexica
    """
    with st.sidebar:
        # st.title("🔎 Perplexica")
        # st.markdown("---")

        # Navigation tabs
        if st.button("🔍 Search", use_container_width=True, 
                    type="primary" if st.session_state.current_tab == "search" else "secondary"):
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
        st.markdown("---")
        st.subheader("History")
        
        # Initialize conversation manager
        conversation_manager = ConversationManager()
        
        # New conversation button at the top
        if st.button("New thread", use_container_width=True, type="secondary", icon="🌱"):
            st.session_state.active_conversation_id = None
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
            
        st.markdown("---")
        
        # Focus mode selection (only visible in search tab)
        if st.session_state.current_tab == "search":
            st.subheader("Focus Mode")
            focus_modes = {
                "all": "🌐 All",
                "writing": "✍️ Writing Assistant",
                "academic": "📚 Academic",
                "youtube": "▶️ YouTube",
                "wolfram": "🧮 Wolfram Alpha",
                "reddit": "🤖 Reddit"
            }
            
            for mode_key, mode_label in focus_modes.items():
                if st.button(mode_label, use_container_width=True, 
                           type="primary" if st.session_state.focus_mode == mode_key else "secondary"):
                    st.session_state.focus_mode = mode_key
                    st.rerun()