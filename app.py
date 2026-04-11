import streamlit as st

from pages.chat import render_chat
from pages.login import render_login
from pages.registration import render_registration


st.set_page_config(page_title="MineGuard")

st.markdown(
	"""
	<style>
	.stApp {
		background-color: #000000;
		color: #ffffff;
	}
	[data-testid="stSidebar"] {
		display: none;
	}
	.stTextInput input {
		background-color: #111111;
		color: #ffffff;
		border: 1px solid #333333;
	}
	.stTextInput label {
		color: #ffffff;
	}
	.stButton button {
		background-color: #222222;
		color: #ffffff;
		border: 1px solid #444444;
	}
	.chat-bubble {
		padding: 12px 14px;
		border-radius: 12px;
		margin: 8px 0;
		max-width: 720px;
		font-size: 15px;
		line-height: 1.4;
	}
	.chat-user {
		background-color: #1b1b1b;
		border: 1px solid #2f2f2f;
		margin-left: auto;
	}
	.chat-assistant {
		background-color: #0f0f0f;
		border: 1px solid #2a2a2a;
		margin-right: auto;
	}
	a { color: #ffffff; }
	</style>
	""",
	unsafe_allow_html=True,
)

params = st.query_params
page = params.get("page", "home")


def render_home() -> None:
	st.title("MineGuard")
	st.write("Welcome to MineGuard.")
	st.markdown("[Go to Registration](/?page=reg)")
	st.markdown("[Go to Login](/?page=login)")
	st.markdown("[Go to Chat](/?page=chat)")
	st.markdown("[Go to Incident Report](/?page=incident)")


if page == "reg":
	render_registration()
elif page == "login":
	render_login()
elif page == "chat":
	render_chat()
elif page == "incident":
	from pages.incident_report import render_incident_report
	render_incident_report()
else:
	render_home()
