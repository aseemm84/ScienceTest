"""
Enhanced Main Interface for ScienceGPT
Handles chat interface, dynamic question suggestions, and video display.
"""

import streamlit as st
from typing import List, Dict, Optional

def draw_main_interface():
    """Draw the enhanced main interface with dynamic content and video display."""
    st.title("🤖 Ask Your Science Questions")

    # Get current settings from session state
    grade = st.session_state.get('grade', 3)
    language = st.session_state.get('language', 'English')
    subject = st.session_state.get('subject', 'General Science')
    topic = st.session_state.get('topic', 'All Topics')

    # Initialize LLM handler if not already done
    if 'llm_handler' not in st.session_state:
        from backend_code.llm_handler import LLMHandler
        st.session_state.llm_handler = LLMHandler()

    llm_handler = st.session_state.llm_handler

    # Generate dynamic suggestions based on current settings
    with st.spinner("Generating personalized questions..."):
        suggestions = llm_handler.generate_suggestions(grade, subject, language, topic)

    # Display suggested questions
    st.markdown("### 💭 Suggested Questions")
    st.markdown(f"*Based on Grade {grade} {subject} in {language}*")

    # Create columns for better layout
    col1, col2 = st.columns(2)

    for i, suggestion in enumerate(suggestions):
        with col1 if i % 2 == 0 else col2:
            if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                # Add suggestion to chat and get response
                handle_question(suggestion, grade, subject, language, topic)

    # Chat interface
    st.markdown("---")
    st.markdown("### 💬 Chat with ScienceGPT")

    # Display chat messages
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Chat container
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                # If the message is from the assistant and has a video, display it
                if message["role"] == "assistant" and "video_url" in message and message["video_url"]:
                    st.markdown("---")
                    st.markdown("##### 📺 Recommended Video")
                    st.video(message["video_url"])


    # Chat input
    if prompt := st.chat_input(f"Ask your {subject} question in {language}..."):
        handle_question(prompt, grade, subject, language, topic)

def handle_question(question: str, grade: int, subject: str, language: str, topic: str):
    """Handle a user question, generate response, and find a relevant video."""
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": question})

    # Rerun to display the user's message immediately
    st.rerun()

def handle_response_generation():
    """Generate and display the assistant's response. This is separated to run after the user message is shown."""
    # Get the last user question
    last_message = st.session_state.messages[-1]
    if last_message["role"] != "user":
        return # Should not happen if called correctly

    question = last_message["content"]
    grade = st.session_state.get('grade', 3)
    subject = st.session_state.get('subject', 'General Science')
    language = st.session_state.get('language', 'English')
    topic = st.session_state.get('topic', 'All Topics')

    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking and finding a relevant video..."):
            if 'llm_handler' in st.session_state:
                response_data = st.session_state.llm_handler.generate_response(
                    question, grade, subject, language, topic
                )
                response_text = response_data.get("text")
                video_url = response_data.get("video_url")
            else:
                response_text = "I'm sorry, I'm having trouble connecting right now. Please try again."
                video_url = None

        st.markdown(response_text)
        if video_url:
            st.markdown("---")
            st.markdown("##### 📺 Recommended Video")
            st.video(video_url)

    # Add assistant response to chat history
    assistant_message = {"role": "assistant", "content": response_text, "video_url": video_url}
    st.session_state.messages.append(assistant_message)

    # Update gamification
    if 'gamification' in st.session_state:
        st.session_state.gamification.add_points(10)  # 10 points per question
        st.session_state.gamification.check_achievements()
        # Update points in session state
        st.session_state.points = st.session_state.gamification.get_total_points()
    
    # We need to rerun one last time to persist the assistant message
    st.rerun()

# This logic ensures the response is generated only after the user's message is displayed
if 'messages' in st.session_state and len(st.session_state.messages) > 0:
    if st.session_state.messages[-1]["role"] == "user":
        handle_response_generation()
