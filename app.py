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


if page == "reg":
	render_registration()
elif page == "login":
	render_login()
elif page == "chat":
	render_chat()
else:
	render_home()
