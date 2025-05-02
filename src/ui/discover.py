import streamlit as st
import random
from datetime import datetime
from src.data.searxng import search_news

def render_discover_tab():
    """
    Renders the Discover tab that displays current events and trending topics
    """
    st.title("Discover")
    
    # Topic selection
    topics = ["AI", "Technology", "Science", "Business", "Health"]
    
    col1, col2 = st.columns([4, 1])
    with col1:
        selected_topic = st.selectbox("Topic", topics, index=0)
    with col2:
        if st.button("Refresh", use_container_width=True):
            # Clear cache to refresh results
            st.session_state.discover_results = None
            st.rerun()
    
    # Get or fetch discover results
    if "discover_results" not in st.session_state or st.session_state.discover_results is None:
        with st.spinner("Fetching latest news..."):
            results = fetch_discover_content(selected_topic)
            st.session_state.discover_results = results
    else:
        results = st.session_state.discover_results
    
    # Display results in a grid
    if results:
        display_discover_grid(results)
    else:
        st.error("Unable to fetch discover content. Please try again later.")

def fetch_discover_content(topic):
    """
    Fetches news and articles for the discover tab
    
    Args:
        topic (str): The topic to search for
        
    Returns:
        list: List of article dictionaries with title, content, url, and thumbnail
    """
    # Define news sources to search from
    sources = [
        "yahoo.com",
        "businessinsider.com",
        "wired.com",
        "theverge.com",
        "cnet.com",
        "techcrunch.com"
    ]
    
    # Randomly select sources to avoid overwhelming the API
    selected_sources = random.sample(sources, min(3, len(sources)))
    
    # Build search queries
    queries = [f"site:{source} {topic}" for source in selected_sources]
    
    # Fetch results
    all_results = []
    for query in queries:
        try:
            results, error_message = search_news(query)
            if error_message:
                st.warning(f"Search warning: {error_message}")
            if results:
                all_results.extend(results)
        except Exception as e:
            st.error(f"Error fetching news: {str(e)}")
    
    # Sort by date (if available) and randomize a bit for variety
    random.shuffle(all_results)
    
    return all_results

def display_discover_grid(articles):
    """
    Displays articles in a responsive grid layout
    
    Args:
        articles (list): List of article dictionaries
    """
    # Create three columns for the grid
    cols = st.columns(3)
    
    # Display articles in the grid
    for i, article in enumerate(articles):
        col_idx = i % 3
        
        with cols[col_idx]:
            # Display title as header first, then add link separately
            st.markdown(f"### {article['title']}")
            # st.markdown(f"[View full article]({article['url']})")
            st.markdown(f"📰 [Read the full article]({article['url']})")

            # Display thumbnail if available
            if 'thumbnail' in article and article['thumbnail']:
                st.image(article['thumbnail'], use_column_width=True)
            
            # Display snippet as caption
            if 'content' in article:
                st.caption(article['content'][:150] + "..." if len(article['content']) > 150 else article['content'])

            if st.button("Explore this story", key=f"search_{i}", use_container_width=True):
                # Set up a search query based on the article
                st.session_state.search_query = f"Summarize: {article['title']}"
                st.session_state.current_tab = "search"
                st.rerun()
            
            st.markdown("---")
