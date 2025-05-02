import streamlit as st

def render_sidebar():
    """
    Renders the sidebar navigation for Perplexica
    """
    with st.sidebar:
        st.title("🔎 Perplexica")
        st.markdown("---")
        
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
        
        # Copilot mode toggle (only visible in search tab)
        if st.session_state.current_tab == "search":
            st.markdown("---")
            st.subheader("Search Mode")
            copilot_enabled = st.toggle("Enable Copilot Mode", value=st.session_state.copilot_mode)
            if copilot_enabled != st.session_state.copilot_mode:
                st.session_state.copilot_mode = copilot_enabled
                st.rerun()
            
            if st.session_state.copilot_mode:
                st.info("Copilot mode performs multi-hop searches to find more relevant information.")
        
        # Footer
        # st.markdown("---")
        # st.markdown("### About")
        # st.markdown("""
        # Perplexica is an open-source AI-powered search tool that dives deep into the internet to find precise answers.
        
        # [GitHub](https://github.com/ItzCrazyKns/Perplexica)
        # """)
