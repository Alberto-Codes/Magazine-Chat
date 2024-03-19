# Project Title: Magazine Chat

## Overview
This project develops a Flask-based API that interfaces with Google Cloud Platform (GCP) services to search, retrieve, store, and analyze PDF documents. The workflow automates the process of finding PDF files through programmable Google searches, uploading those files to a GCP bucket, and importing them into GCP's Search & Conversation AI for analysis. The result is a comprehensive report, generated from the AI's findings, formatted as a PDF and made available for consumption through the API or a future web frontend.

## Getting Started

### Prerequisites
- Python 3.8+
- Flask
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
1. Start the Flask application:
   ```sh
   flask run
   ```
2. Access the API endpoints as per the API documentation section below.

## API Documentation
(TBD - Define your API endpoints, request/response formats)

## Architecture
- **Flask API**: Serves as the backbone of the application, handling HTTP requests and triggering the PDF processing workflow.
- **Google Programmable Search Engine**: Powers the initial PDF file search based on user-defined criteria.
- **GCP Storage**: Hosts the retrieved PDF files.
- **GCP Search & Conversation AI**: Processes the PDF content, extracting and analyzing data.
- **PDF Report Generator**: Compiles findings into a formatted PDF report.

## Future Enhancements
- Integration with a Python web frontend (e.g., Streamlit) for an interactive user experience.
- Expanded AI analysis features for deeper insights into PDF content.
- Enhanced security measures for data protection and access control.

## Contributing
We welcome contributions! Please read our contributing guidelines (link to guidelines) before submitting pull requests.

<!-- ## License
Specify your project's license here. -->

## Contact
Your Name - Alberto-Codes
Project Link: https://github.com/Alberto-Codes/Magazine-Chat