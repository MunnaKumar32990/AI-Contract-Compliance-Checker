# AI Contract Compliance Checker

An AI-powered contract review application that analyzes PDF agreements, identifies their document type, extracts contractual clauses, and compares them with reference templates to highlight potential GDPR-related compliance gaps.

> **Important:** This project provides AI-assisted review, not legal advice or a formal certification of GDPR compliance. Results should be validated by a qualified legal or privacy professional.

## Contents

- [Overview](#overview)
- [Features](#features)
- [Supported agreement types](#supported-agreement-types)
- [How it works](#how-it-works)
- [Technology stack](#technology-stack)
- [Project structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation and setup](#installation-and-setup)
- [Configuration](#configuration)
- [Run the application](#run-the-application)
- [How to use](#how-to-use)
- [Notifications and template updates](#notifications-and-template-updates)
- [Limitations and security notes](#limitations-and-security-notes)
- [Future improvements](#future-improvements)
- [License](#license)

## Overview

Reviewing contracts against privacy and data-protection requirements can be time-consuming. This application uses Google's Gemini models to help automate parts of that review process. It accepts a PDF contract, predicts which supported agreement type it represents, extracts clauses from the document, and compares those clauses with a corresponding reference dataset stored in the repository.

The app presents a structured report that includes missing or altered clauses, potential compliance risks, a risk score from 0 to 100, the model's reasoning, and recommendations for amendments.

## Features

- **PDF upload:** Upload a contract through a Streamlit web interface.
- **Agreement-type classification:** Uses Gemini to identify the document as one of the supported agreement types.
- **Clause extraction:** Extracts clause identifiers, headings, and text from PDF content using PyPDF2 and a Gemini structured-output response.
- **Reference comparison:** Compares the extracted content with local JSON reference data.
- **Risk report:** Displays a score and categorizes it as low (0–33), medium (34–66), or high (67–100) in the interface.
- **Recommendations:** Presents model-generated compliance concerns, rationale, and suggested amendments.
- **Email and Slack notifications:** The code supports sending analysis results by email and reporting errors to Slack when the relevant settings are configured.
- **Scheduled reference refresh:** Includes a daily scheduler that attempts to retrieve reference PDFs from configured URLs and regenerate the local JSON clause data.

## Supported agreement types

The main application maps the following categories to local JSON reference files:

| Agreement type | Reference file |
|---|---|
| Data Processing Agreement (DPA) | `json_files/dpa.json` |
| Joint Controller Agreement (JCA) | `json_files/jca.json` |
| Controller-to-Controller Agreement (C2C) | `json_files/c2c.json` |
| Processor-to-Subprocessor Agreement | `json_files/subprocessor.json` |
| Standard Contractual Clauses (SCC) | `json_files/scc.json` |

Documents that cannot be classified into one of these categories are not processed through the standard comparison flow.

## How it works

1. **Upload a PDF.** The user submits a contractual agreement using Streamlit's file uploader.
2. **Extract document text.** PyPDF2 reads the available text from the PDF pages.
3. **Classify the document.** Gemini returns a supported agreement type.
4. **Extract clauses.** Gemini generates structured clause data from the uploaded contract.
5. **Load the matching reference.** The application reads the relevant JSON file under `json_files/`.
6. **Compare and assess risk.** Gemini compares the uploaded clauses against the reference and generates the report.
7. **Display and notify.** Streamlit displays the results in separate tabs, and the notification module attempts to send the configured result notification.

The high-level flow is:

```text
PDF Upload
    |
    v
PDF Text Extraction (PyPDF2)
    |
    v
Agreement Classification (Gemini)
    |
    v
Clause Extraction (Gemini)
    |
    v
Load Matching JSON Reference
    |
    v
Clause Comparison and Risk Assessment (Gemini)
    |
    v
Streamlit Compliance Report
    |
    v
Email Result Notification
```

## Technology stack

| Technology | Role |
|---|---|
| Python | Application logic |
| Streamlit | Web user interface |
| Google Gen AI SDK | Gemini model integration |
| Gemini 2.5 Flash | Agreement classification, clause extraction, and comparison |
| PyPDF2 | Reading text from PDF documents |
| Pydantic | Structured output schema for model responses |
| python-dotenv | Loading environment variables from a local `.env` file |
| Requests | Downloading reference documents and sending Slack webhook requests |
| schedule and threading | Running the scheduled reference refresh task |
| JSON | Storing reference clause data |

The code also lists `numpy` and `groq` in `requirements.txt`; the current main workflow primarily uses the Google Gen AI SDK.

## Project structure

```text
AI-Contract-Compliance-Checker/
├── main.py                    # Streamlit application and end-to-end workflow
├── agreement_comparision.py   # Agreement classification and comparison prompts
├── data_extraction.py         # PDF text extraction and AI clause extraction
├── notifications.py           # Email and Slack notification utilities
├── scrapping.py               # Downloads reference PDFs and refreshes clause data
├── requirements.txt           # Python package dependencies
├── json_files/
│   ├── dpa.json               # DPA reference clauses
│   ├── jca.json               # Joint controller reference clauses
│   ├── c2c.json               # Controller-to-controller reference clauses
│   ├── subprocessor.json      # Subprocessor reference clauses
│   └── scc.json               # SCC reference clauses
├── templates/                 # Reference agreement PDFs
├── UnseenData/                # Additional sample/reference PDFs
├── temp_uploaded.pdf          # Temporary uploaded document (created at runtime)
├── temp_agreement.pdf         # Temporary downloaded reference PDF
└── LICENSE
```

## Prerequisites

- Python 3.10 or a compatible newer Python version.
- A Google Gemini API key with access to the configured Gemini model.
- Internet access for model calls and, if enabled, reference downloads and Slack notifications.
- Optional: a Slack incoming webhook if Slack error notifications are needed.
- Optional: SMTP credentials if email notifications are enabled.

## Installation and setup

### 1. Clone the repository

```bash
git clone https://github.com/MunnaKumar32990/AI-Contract-Compliance-Checker.git
cd AI-Contract-Compliance-Checker
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the repository root. The code references different Gemini key names in different modules:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
GEMINI_API_KEY1=your_gemini_api_key
GEMINI_API_KEY2=your_gemini_api_key
SLACK_WEBHOOK_URL=your_slack_incoming_webhook_url
```

The three Gemini variables are used separately by the current source code: classification reads `GEMINI_API_KEY`, comparison reads `GEMINI_API_KEY1`, and full clause extraction reads `GEMINI_API_KEY2`. They can point to the same key if that key has the required access. Do not commit your real `.env` file or API keys to GitHub.

## Run the application

Start the Streamlit app from the project root:

```bash
streamlit run main.py
```

Streamlit prints a local URL in the terminal (commonly `http://localhost:8501`). Open that URL in your browser.

## How to use

1. Start the app.
2. Upload a text-based PDF contract.
3. Wait for document classification, clause extraction, and template comparison to finish.
4. Review the report:
   - **Potential Compliance Risks**
   - **Recommendations**
   - **Missing Clauses**
   - **Reasoning**
5. Check the overall score and verify the findings against the original contract and relevant legal requirements.

Scanned/image-only PDFs may not yield usable text unless OCR is added. Model results can also omit, misinterpret, or invent details, so review the original clauses before making decisions.

## Notifications and template updates

### Email and Slack

The notification module routes result notifications to email and error notifications to Slack. The current source contains fixed sender/recipient and SMTP credential values in `notifications.py`, so **replace that implementation immediately** with environment-based configuration before using or sharing the application. If any real credential has ever been committed, revoke or rotate it. The Slack module reads `SLACK_WEBHOOK_URL` from the environment.

### Scheduled reference refresh

The application starts a background scheduler that calls the scraping module daily at midnight. That module attempts to download reference PDFs and regenerate JSON clause data.

This feature depends on the external source URLs remaining available and compatible. Review downloaded documents and generated JSON before treating them as authoritative or current. Also note that the existing paths and refresh logic may need adjustment for non-Windows environments and more robust HTTP/error handling.

## Limitations and security notes

- **Not legal advice:** The tool supports preliminary review and does not guarantee legal or GDPR compliance.
- **Model-generated output:** Risk scores, extracted clauses, and recommendations are model-generated and require human validation.
- **PDF text extraction:** PyPDF2 extracts embedded text but does not perform OCR for image-only scans.
- **Sensitive contracts:** Contracts may contain personal, commercial, or confidential information. Assess data handling, provider terms, access controls, retention, and applicable privacy requirements before sending them to an external AI service.
- **Credentials:** Never store credentials directly in source code. Replace the hard-coded SMTP details in `notifications.py`, rotate any exposed credential, and keep secrets in environment variables or a secrets manager.
- **Temporary files:** The current workflow writes uploads and downloaded reference PDFs to local files. Add appropriate cleanup, isolation, file-size limits, and access controls before production use.
- **Reference quality:** A comparison is only as useful as the selected reference. Confirm jurisdiction, version, applicability, and effective date of each source agreement.
- **Operational hardening:** Add validation for unexpected model responses, network timeouts, retry logic, and tests before relying on this tool in a production workflow.

## Future improvements

- Add a reviewable side-by-side clause diff with citations to source pages and clause identifiers.
- Support OCR for scanned PDFs and larger document handling.
- Add human approval, reviewer notes, and exportable PDF/Word reports.
- Make risk scoring explainable, configurable, and validated against a curated test set.
- Store secrets securely and configure email/Slack entirely through environment variables.
- Add automated tests, logging, dependency pinning, and CI checks.
- Version reference templates and display their source URLs and last-updated dates.
- Improve cross-platform path handling, scheduled refresh reliability, and temporary-file cleanup.

## License

This project is licensed under the [MIT License](LICENSE).
