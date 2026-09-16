import streamlit as st
import requests


UPLOAD_PDF_URL = "http://localhost:8000/upload-pdf"


st.set_page_config(
    page_title="Knowledge Base Upload",
    page_icon="📄"
)

st.title("📄 Upload PDF to Knowledge Base")

uploaded_pdf = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    accept_multiple_files=False
)

if uploaded_pdf:
    st.write(f"Selected: **{uploaded_pdf.name}**")

    if st.button("Upload"):

        with st.spinner("Uploading and processing..."):

            files = {
                "pdf": (
                    uploaded_pdf.name,
                    uploaded_pdf.getvalue(),
                    "application/pdf"
                )
            }

            response = requests.post(UPLOAD_PDF_URL, files=files)

        if response.status_code == 200:
            st.success(response.json())
        else:
            st.error(f"Error {response.status_code}: {response.text}")