import base64
import os

import requests
import streamlit as st
import streamlit.components.v1 as components

api_service_url = os.getenv("API_SERVICE_URL")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
AI_CHAT_AGENT_ID = os.getenv("AI_CHAT_AGENT_ID")


st.set_page_config(page_title="🥑🔍 Food Ingredient Search 🤖", page_icon=":mag:")
st.title("🥑🔍 Food Ingredient Search 🤖")
st.write(
    "Discover valuable insights about food ingredients using our AI-powered search engine."
)

st.subheader("Search Parameters")
argument = st.text_input(
    "Enter food ingredient",
    key="ingredient_input",
    placeholder="e.g., pork, chicken breast, pineapple, avocado",
    help="Enter a food ingredient to search for",
)
if (
    "last_argument" not in st.session_state
    or st.session_state["last_argument"] != argument
):
    st.session_state["pdf_base64"] = None
    st.session_state["last_argument"] = argument

# Button for WebPdfSearch
if st.button(
    "Start WebPdfSearch", key="webpdfsearch_button", help="Click to initiate the WebPdfSearch process."
):
    response1 = requests.post(
        f"{api_service_url}/api/web_pdf_search/", json={"argument": argument}
    )
    if response1.status_code == 200:
        st.success("WebPdfSearch completed successfully")
    else:
        st.error("WebPdfSearch failed")

# Button for ImportDocuments
if st.button(
    "Start ImportDocuments", key="importdocuments_button", help="Click to initiate the ImportDocuments process."
):
    response2 = requests.post(
        f"{api_service_url}/api/import_documents/", json={"location": "global"}
    )
    if response2.status_code == 200:
        st.success("ImportDocuments completed successfully")
    else:
        st.error("ImportDocuments failed")

# Button for PdfGenerator
if st.button(
    "Start PdfGenerator", key="pdfgenerator_button", help="Click to initiate the PdfGenerator process."
):
    response3 = requests.post(
        f"{api_service_url}/api/pdf_generator/", json={"argument": argument}
    )
    if response3.status_code == 200:
        st.success("PdfGenerator completed successfully")
        # Update the session state with the new PDF content
        st.session_state["pdf_base64"] = base64.b64encode(
            response3.content
        ).decode()
    else:
        st.error("PdfGenerator failed")

# Display the PDF from session state if it exists
if st.session_state["pdf_base64"]:
    st.subheader("Generated PDF")
    st.markdown(
        f'<iframe src="data:application/pdf;base64,{st.session_state["pdf_base64"]}" width="100%" height="700" type="application/pdf"></iframe>',
        unsafe_allow_html=True,
    )


st.markdown(
    """
<style>
[data-testid="stSidebar"][role="complementary"] {
    width: 350px;
}
</style>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("AI Agent Chat")
    components.html(
        f"""+
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/themes/df-messenger-default.css">
        <script src="https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/df-messenger.js"></script>
        <df-messenger project-id="{GOOGLE_CLOUD_PROJECT}" agent-id="{AI_CHAT_AGENT_ID}" language-code="en" max-query-length="-1">
            <df-messenger-chat chat-title="GCP AI Pipeline Chat">
            </df-messenger-chat>
        </df-messenger>
        <style>
            df-messenger {{
                z-index: 999;
                position: fixed;
                bottom: 0;
                right: 0;
                top: 0;
                width: 100%;
                height: 100%;
            }}
        </style>
        """,
        height=600,
        width=350,
        scrolling=False,
    )
