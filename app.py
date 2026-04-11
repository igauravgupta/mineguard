import streamlit as st


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


def render_registration() -> None:
	st.title("Registration")
	with st.form("registration_form"):
		st.text_input("User name")
		st.text_input("Email ID")
		st.text_input("Password", type="password")
		submitted = st.form_submit_button("Submit")

	if submitted:
		st.success("Registration submitted.")


def render_login() -> None:
	st.title("Login")
	with st.form("login_form"):
		st.text_input("Email ID")
		st.text_input("Password", type="password")
		submitted = st.form_submit_button("Login")

	if submitted:
		st.success("Login submitted.")


if page == "reg":
	render_registration()
elif page == "login":
	render_login()
else:
	render_home()
