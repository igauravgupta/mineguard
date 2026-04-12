import base64
import time

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
                    return

                job = response.json()
                report_id = job.get("id")
                st.info(f"Processing report id: {report_id}")

                status_url = f"{api_base_url.rstrip('/')}/reports/{report_id}"
                for _ in range(10):
                    status_response = requests.get(status_url, timeout=10)
                    if status_response.status_code != 200:
                        st.error(
                            f"Status error: {status_response.status_code} {status_response.text}"
                        )
                        return
                    payload = status_response.json()
                    if payload.get("status") in {"Active", "completed"}:
                        st.success("Incident report completed.")
                        st.json(payload)
                        return
                    if payload.get("status") == "failed":
                        st.error(payload.get("error", "Incident processing failed"))
                        return
                    time.sleep(2)

                st.warning("Still processing. Please retry in a moment.")
            except Exception as exc:
                st.error(f"API request failed: {exc}")
