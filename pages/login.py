import streamlit as st


def render_login() -> None:
    st.title("Login")
    with st.form("login_form"):
        st.text_input("Email ID")
        st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        st.success("Login submitted.")
