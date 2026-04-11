import streamlit as st


def render_registration() -> None:
    st.title("Registration")
    with st.form("registration_form"):
        st.text_input("User name")
        st.text_input("Email ID")
        st.text_input("Password", type="password")
        submitted = st.form_submit_button("Submit")

    if submitted:
        st.success("Registration submitted.")
