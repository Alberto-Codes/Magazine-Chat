import os
import streamlit as st
import requests
import base64

# Get API_SERVICE_URL from environment variables
api_service_url = os.getenv("API_SERVICE_URL")

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

                # Save the PDF file to a location that's accessible via a URL
                with open('output.pdf', 'wb') as f:
                    f.write(response3.content)

                # Display the PDF file
                st.markdown("Here is the generated PDF file:")
                st.markdown(
                    f'<iframe src="data:application/pdf;base64,{base64.b64encode(response3.content).decode()}" width="700" height="700" type="application/pdf"></iframe>',
                    unsafe_allow_html=True,
                )
            else:
                st.error("PdfGenerator failed")
        else:
            st.error("ImportDocuments failed")
    else:
        st.error("WebPdfSearch failed")