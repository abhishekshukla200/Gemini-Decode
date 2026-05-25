# GeminiDecode

GeminiDecode is a Flask web app that analyzes document images and PDFs with the Gemini API. Upload a JPG, PNG, or PDF, ask a question about the document, and get an AI-generated answer.

## Features

- Analyze document images in JPG and PNG format
- Analyze PDF documents
- Ask custom questions about uploaded documents
- Uses Gemini Flash by default
- Deployable on Vercel as a Python Flask app

## Tech Stack

- Python
- Flask
- Google Generative AI SDK
- Vercel

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

`GEMINI_MODEL` is optional. If it is not set, the app uses `gemini-2.5-flash`.

## Run Locally

```powershell
flask --app app run --debug
```

Open the local URL shown in your terminal, usually:

```text
http://127.0.0.1:5000
```

## Vercel Deployment

Add this environment variable in your Vercel project settings:

```text
GEMINI_API_KEY
```

Then redeploy the project. Vercel only applies new environment variables to new deployments.

## Upload Limits

This project is configured for Vercel-friendly uploads up to 4 MB. Larger PDFs need a storage-based upload flow or a different hosting platform.

## Notes

If Google reports that your API key was leaked, create a new key in Google AI Studio, update `GEMINI_API_KEY` in Vercel, remove the old key, and redeploy.
