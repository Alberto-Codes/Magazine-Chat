import os
import streamlit as st
import requests
import base64
import streamlit.components.v1 as components

# Get API_SERVICE_URL from environment variables
api_service_url = os.getenv("API_SERVICE_URL")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
AI_CHAT_AGENT_ID = os.getenv("AI_CHAT_AGENT_ID")

col1, col2 = st.columns(2)
with col1:
    # User inputs
    argument = st.text_input("Enter food ingredient")

    # Button to start the process
    if st.button("Start"):
        # Call WebPdfSearch endpoint
        response1 = requests.post(f'{api_service_url}/api/v1/web_pdf_search', json={"argument": argument})
        if response1.status_code == 200:
            st.write("WebPdfSearch completed successfully")

            # Call ImportDocuments endpoint
            response2 = requests.post(f'{api_service_url}/api/v1/import_documents', json={"location": "global"})
            if response2.status_code == 200:
                st.write("ImportDocuments completed successfully")

                # Call PdfGenerator endpoint
                response3 = requests.post(f'{api_service_url}/api/v1/pdf_generator', json={"argument": argument})
                if response3.status_code == 200:
                    st.write("PdfGenerator completed successfully")

                    # Convert the PDF content to a base64 string
                    pdf_base64 = base64.b64encode(response3.content).decode()

                    # Display the PDF file
                    st.markdown("Here is the generated PDF file:")
                    st.markdown(
                        f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="700" height="700" type="application/pdf"></iframe>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.error("PdfGenerator failed")
            else:
                st.error("ImportDocuments failed")
        else:
            st.error("WebPdfSearch failed")
with col2:
    st.title("Chat with the AI Agent")
    components.html(
        f"""
        <link rel="stylesheet" href="https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/themes/df-messenger-default.css">
        <script src="https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/df-messenger.js"></script>
        <df-messenger
        project-id="{GOOGLE_CLOUD_PROJECT}"
        agent-id="{AI_CHAT_AGENT_ID}"
        language-code="en"
        max-query-length="-1">
        <df-messenger-chat-bubble
        chat-title="Magazine Chat Conversation AI">
        </df-messenger-chat-bubble>
        </df-messenger>
        <style>
        df-messenger {{
            z-index: 999;
            position: fixed;
            bottom: 16px;
            right: 16px;
        }}
        </style>
            """,
        height=600,
    )