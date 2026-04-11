import streamlit as st


def render_chat() -> None:
    st.title("MineGuard Chat")
    st.caption("Ask questions about laws, policies, or incidents.")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            role = message["role"]
            content = message["content"]
            bubble_class = "chat-user" if role == "user" else "chat-assistant"
            st.markdown(
                f"<div class='chat-bubble {bubble_class}'>{content}</div>",
                unsafe_allow_html=True,
            )

    with st.form("chat_form", clear_on_submit=True):
        input_col, button_col = st.columns([6, 1])
        with input_col:
            prompt = st.text_input(
                "Message",
                placeholder="Type your message...",
                label_visibility="collapsed",
            )
        with button_col:
            submitted = st.form_submit_button("Send")

    if submitted and prompt.strip():
        st.session_state.chat_messages.append(
            {"role": "user", "content": prompt.strip()}
        )
        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": "Thanks. I will respond once the backend is connected.",
            }
        )
        st.rerun()
