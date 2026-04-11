import streamlit as st


def render_incident_report() -> None:
    st.title("Incident Report")
    st.caption("Describe the incident and upload up to 5 images.")

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
            st.success("Incident report submitted.")
