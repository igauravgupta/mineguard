import base64

import requests
import streamlit as st


def render_incident_report() -> None:
    st.title("Incident Report")
    st.caption("Describe the incident and upload up to 5 images.")

    api_base_url = st.text_input("API Base URL", value="http://localhost:8000")

    with st.form("incident_report_form"):
        description = st.text_area("Description", height=160)
        images = st.file_uploader(
            "Upload images (up to 5)",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
        )
        submitted = st.form_submit_button("Submit")

    if submitted:
        image_count = len(images) if images else 0
        if image_count > 5:
            st.error("Please upload no more than 5 images.")
        elif not description.strip():
            st.error("Please enter a description.")
        else:
            encoded_images = []
            for image in images or []:
                encoded_images.append(
                    base64.b64encode(image.getvalue()).decode("ascii")
                )

            payload = {
                "description": description.strip(),
                "images_base64": encoded_images,
            }
            try:
                response = requests.post(
                    f"{api_base_url.rstrip('/')}/incident/classify",
                    json=payload,
                    timeout=30,
                )
                if response.status_code != 200:
                    st.error(f"API error: {response.status_code} {response.text}")
                else:
                    st.success("Incident report submitted.")
                    st.json(response.json())
            except Exception as exc:
                st.error(f"API request failed: {exc}")
