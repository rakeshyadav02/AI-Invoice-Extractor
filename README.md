# AI-Powered Invoice Data Extraction System

**An AI-powered invoice processing application built with Python, Google Gemini AI, and Streamlit.**

A Python application that extracts structured information from invoice images and PDF documents using Google Gemini AI, validates financial calculations, and generates downloadable JSON output.

## Overview

This project automates invoice data extraction using multimodal AI. It identifies invoice details, supplier information, line items, and financial summaries, then validates the extracted information using structured data models and independent calculation logic.

## Key Features

- Upload invoice images (PNG, JPG, JPEG) and PDF documents.
- Enforce a 10 MB upload limit and reject oversized image dimensions.
- Extract invoice information using Google Gemini AI.
- Identify invoice number, date, and supplier name.
- Extract item descriptions, quantities, unit prices, and total amounts.
- Extract subtotal, VAT, and grand total.
- Generate structured JSON output.
- Validate item calculations and financial totals using Python `Decimal`.
- Detect missing information and calculation inconsistencies.
- Display extraction results through an interactive Streamlit dashboard.
- Download extracted information as a JSON file.
- Handle invalid files and extraction errors.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| Google Gemini AI | AI-powered invoice extraction |
| Google Gen AI SDK | Gemini API integration |
| Streamlit | User interface |
| Pydantic | Data structure validation |
| Pillow | Image processing |
| PyMuPDF | PDF processing |
| Decimal | Financial calculations |
| Pandas | Tabular data presentation |
| python-dotenv | Environment configuration |

## Project Structure

```text
AI-Invoice-Extractor/
│
├── src/
│   ├── __init__.py
│   ├── gemini_client.py
│   ├── extractor.py
│   ├── schemas.py
│   ├── validator.py
│   └── file_handler.py
│
├── samples/
├── app.py
├── test_gemini.py
├── test_extraction.py
├── test_validation.py
├── test_full_pipeline.py
├── .env.example
├── .env                      # Local only; never commit
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation and Setup

**Prerequisites:** Python 3.10 or newer, Git, and a Google Gemini API key.

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Invoice-Extractor.git

cd AI-Invoice-Extractor
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API

Generate an API key from [Google AI Studio](https://aistudio.google.com/).

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

You can create it from the safe template:

```powershell
Copy-Item .env.example .env
```

Then replace `your_gemini_api_key_here` in `.env` with your actual key.
The `.env` file is local-only and is excluded by `.gitignore`. Never upload
your actual API key or `.env` file to GitHub.

## Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

Open the application in your browser:

```text
http://localhost:8501
```

### How to Use

1. Upload an invoice image or PDF.
2. Click **Extract Invoice Information**.
3. Wait for Gemini AI to process the document.
4. Review the extracted invoice details and line items.
5. Check the financial validation results.
6. Preview and download the structured JSON output.

## Financial Validation

The application performs independent calculations to verify extracted financial information.

| Validation | Calculation |
|---|---|
| Item Total | Quantity × Unit Price |
| Subtotal | Sum of Item Totals |
| VAT | Subtotal × VAT Percentage / 100 |
| Grand Total | Subtotal + VAT Amount |

The application reports calculation errors and warnings for missing or inconsistent information. A small tolerance is allowed for normal rounding differences.

## Testing

The project includes offline automated tests for extraction utilities, file
processing, configuration validation, and financial calculations:

```bash
pytest
```

The test suite does not call Gemini and does not require an API key. Live
Gemini extraction requires a valid key, network access, and may consume API
quota, so it should be checked manually by running the Streamlit application.

## Security and Limitations

- API credentials are managed through environment variables.
- Sensitive files and virtual environments are excluded from Git.
- Uploaded documents are processed in memory.
- Create `.env` locally and never commit it; `.gitignore` excludes it.
- Only the first page of a PDF is currently processed.
- Extraction accuracy depends on document quality and layout.
- AI-generated results require human review before accounting or payment use.
- Confidential invoices should not be published in a public repository.

---

**Developed using Python, Google Gemini AI, and Streamlit.**