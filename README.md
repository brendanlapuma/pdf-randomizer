# PDF Randomizer

A Modal-based API endpoint that randomizes multiple-choice questions in PDF files. Perfect for creating different versions of exams or practice tests.

## Features

- 🔀 Randomizes the order of questions
- 🎲 Randomizes answer choices within each question
- 📄 Generates a clean, properly formatted PDF output
- 🌐 Web API endpoint for easy integration
- 🚀 Deployed with Modal for serverless execution

## Setup

1. Install dependencies using Poetry:
```bash
poetry install
```

2. Set up Modal authentication:
```bash
modal setup
```

## Usage

### Deploy the API

Deploy the API endpoint to Modal:
```bash
modal deploy app.py
```

Modal will provide you with a URL for your endpoint.

### Use the Web Endpoint

Once deployed, you can randomize PDFs using the web endpoint:

```bash
curl -X POST https://your-modal-username--pdf-randomizer-randomize-pdf-endpoint.modal.run \
     -F "file=@practice.pdf" \
     --output randomized.pdf
```

Replace `your-modal-username` with your actual Modal username.

### Test Locally

You can also test the randomization locally before deploying:

```bash
modal run app.py --input-pdf practice.pdf --output-pdf randomized.pdf
```

## How It Works

1. **PDF Parsing**: Extracts questions and multiple-choice answers from the input PDF
2. **Randomization**: 
   - Shuffles the order of questions
   - Shuffles answer choices within each question
   - Reassigns answer letters (A, B, C, D, E) after shuffling
3. **PDF Generation**: Creates a new PDF with the randomized content using ReportLab

## API Endpoint Details

**Endpoint**: `/randomize_pdf_endpoint`  
**Method**: POST  
**Content-Type**: multipart/form-data  
**Form Field**: `file` (PDF file)  
**Response**: PDF file with randomized content

## Requirements

- Python 3.10+
- Modal account
- Dependencies (automatically installed):
  - pypdf
  - reportlab
  - pillow

## Example

```python
import requests

# Upload and randomize a PDF
with open('practice.pdf', 'rb') as f:
    response = requests.post(
        'https://your-modal-url/randomize_pdf_endpoint',
        files={'file': f}
    )

# Save the randomized PDF
with open('randomized.pdf', 'wb') as f:
    f.write(response.content)
```

## License

MIT