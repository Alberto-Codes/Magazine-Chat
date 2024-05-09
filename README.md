# Project Title: Magazine Chat

## Overview
Magazine Chat is a FastAPI-based API that interfaces with Google Cloud Platform (GCP) services to search, retrieve, store, and analyze PDF documents. The workflow automates the process of finding PDF files through programmable Google searches, uploading those files to a GCP bucket, and importing them into GCP's Search & Conversation AI for analysis. The result is a comprehensive report, generated from the AI's findings, formatted as a PDF and made available for consumption through the API or a web frontend. Additionally, the project includes a Streamlit web frontend for an interactive user experience.

## Getting Started

### Prerequisites
- Python 3.8+
- FastAPI
- Streamlit
- Google Cloud Platform account
- GCP SDK installed and configured

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/Alberto-Codes/Magazine-Chat.git
   ```
2. Install the required Python packages:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up GCP credentials (refer to GCP documentation for service account setup and key management).

### Running the Application
1. Start the FastAPI application:
   ```sh
   uvicorn src.api:app --reload
   ```
2. Start the Streamlit application:
   ```sh
   streamlit run src/web/app.py
   ```
3. Access the API endpoints as per the API documentation section below.

## API Documentation
The API consists of several endpoints that trigger different parts of the PDF processing workflow. These include endpoints for initiating a web PDF search, importing documents, and generating a PDF report.

- `/greetings`: A simple greeting endpoint.
- `/upload`: Endpoint for file uploads.
- `/import_documents`: Endpoint for importing documents.
- `/ai_search`: Endpoint for performing AI search.
- `/batch_ai_search`: Endpoint for performing batch AI search.
- `/pdf_generator`: Endpoint for generating PDFs.
- `/web_pdf_search`: Endpoint for performing web PDF search.

## Architecture
- **FastAPI**: Serves as the backbone of the application, handling HTTP requests and triggering the PDF processing workflow.
- **Streamlit**: Provides an interactive web frontend for the application.
- **Google Programmable Search Engine**: Powers the initial PDF file search based on user-defined criteria.
- **GCP Storage**: Hosts the retrieved PDF files.
- **GCP Search & Conversation AI**: Processes the PDF content, extracting and analyzing data.
- **PDF Report Generator**: Compiles findings into a formatted PDF report.

## Future Enhancements
- Expanded AI analysis features for deeper insights into PDF content.
- Enhanced security measures for data protection and access control.

## Contributing
We welcome contributions! Please read our contributing guidelines (link to guidelines) before submitting pull requests.

<!-- ## License
Specify your project's license here. -->

## Contact
Your Name - Alberto-Codes
Project Link: https://github.com/Alberto-Codes/Magazine-Chat