# Document Processing Pipeline

A scalable document processing pipeline that uses OCR and Gemini AI to extract structured data from various document types.

## Features

- **Modular Architecture**: Separate modules for OCR, AI extraction, and document-specific processing
- **Multi-format Support**: Handles JPG, JPEG, and PNG image formats
- **Robust OCR**: Uses EasyOCR with Tesseract fallback for reliable text extraction
- **AI-powered Field Extraction**: Leverages Google's Gemini AI for intelligent field extraction
- **Batch Processing**: Process multiple documents efficiently
- **Error Handling**: Comprehensive error logging and retry mechanisms
- **Validation**: Structured output validation for data quality

## Project Structure

```
doc_pipeline/
├── main.py                 # Main CLI entry point
├── config.py              # Configuration settings
├── .env                   # Environment variables (API keys)
├── ocr/
│   ├── __init__.py
│   └── ocr_engine.py      # OCR text extraction
├── llm/
│   ├── __init__.py
│   └── gemini_client.py   # Gemini AI integration
├── extractors/
│   ├── __init__.py
│   └── license.py         # Driving license field extraction
├── prompts/
│   └── license_extraction.txt  # AI prompt templates
├── utils/
│   ├── __init__.py
│   └── validators.py      # Output validation
├── data/
│   └── driving_license/   # Input images
└── outputs/
    └── driving_license/   # Processed results
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd doc_pipeline
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install OCR dependencies**:
   ```bash
   # For macOS
   brew install tesseract
   
   # For Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # For Windows
   # Download from: https://github.com/UB-Mannheim/tesseract/wiki
   ```

5. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

## Configuration

### Environment Variables (.env)

```bash
# Google Cloud API Configuration
GOOGLE_API_KEY=your_actual_gemini_api_key_here

# Gemini Model Configuration
GEMINI_MODEL=gemini-1.5-pro

# Pipeline Configuration
LOG_LEVEL=INFO
OUTPUT_DIR=./output
DATA_DIR=./data
```

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new project or select existing one
3. Generate an API key
4. Add the key to your `.env` file

## Usage

### Command Line Interface

Process a directory of images:
```bash
python main.py --input data/driving_license --output outputs/driving_license --type license
```

Process with verbose logging:
```bash
python main.py --input data/driving_license --output outputs/driving_license --type license --verbose
```

### Single File Processing

Use the test script for single file processing:
```bash
python test_single.py data/driving_license/generated_license_0.png outputs/test_output.json
```

## Supported Document Types

### Driving License
- **Fields**: Name, DateOfBirth, LicenseNumber, IssuingState, ExpiryDate
- **Input**: Images of driving licenses
- **Output**: JSON with extracted fields

## API Rate Limits

The free tier of Gemini API has the following limits:
- **Requests per minute**: 15
- **Requests per day**: 1500
- **Input tokens per minute**: 32,000

For production use, consider:
- Upgrading to a paid plan
- Implementing request queuing
- Adding delays between requests

## Output Format

### Successful Processing
```json
{
  "Name": "John Doe",
  "DateOfBirth": "1990-01-01",
  "LicenseNumber": "DL123456789",
  "IssuingState": "CA",
  "ExpiryDate": "2025-12-31"
}
```

### Error Logging
Errors are logged to `outputs/<doc_type>/errors.log` with detailed information about failures.

## Architecture

### OCR Engine (`ocr/ocr_engine.py`)
- **Primary**: EasyOCR for high accuracy
- **Fallback**: Tesseract for reliability
- **Supported formats**: JPG, JPEG, PNG

### AI Client (`llm/gemini_client.py`)
- **Model**: Gemini 1.5 Pro
- **Retry logic**: 3 attempts with exponential backoff
- **JSON parsing**: Handles markdown-formatted responses

### Field Extraction (`extractors/license.py`)
- **Document-specific logic**: Tailored for driving licenses
- **Validation**: Ensures required fields are present
- **Error handling**: Graceful degradation on extraction failures

### Validation (`utils/validators.py`)
- **Schema validation**: Ensures output structure
- **Type checking**: Validates field data types
- **Required fields**: Enforces mandatory field presence

## Development

### Adding New Document Types

1. **Create extractor** (`extractors/new_doc_type.py`):
   ```python
   def parse_new_doc_type(text: str) -> Dict[str, Any]:
       return extract_fields_from_text(text, "new_doc_type")
   ```

2. **Add prompt template** (`prompts/new_doc_type_extraction.txt`):
   ```
   Extract the following fields from this document:
   - Field1: Description
   - Field2: Description
   
   OCR Text: <INSERT_OCR_TEXT_HERE>
   
   Return as JSON only.
   ```

3. **Update validators** (`utils/validators.py`):
   ```python
   EXPECTED_FIELDS["new_doc_type"] = {
       "Field1": str,
       "Field2": str
   }
   ```

4. **Update main CLI** to support the new type.

### Testing

```bash
# Test OCR only
python -c "from ocr.ocr_engine import extract_text_from_file; print(extract_text_from_file('test.png'))"

# Test AI extraction only
python -c "from llm.gemini_client import extract_fields_from_text; print(extract_fields_from_text('test text', 'license'))"
```

## Troubleshooting

### Common Issues

1. **OCR not working**:
   - Ensure Tesseract is installed
   - Check image format (JPG, JPEG, PNG only)

2. **Gemini API errors**:
   - Verify API key in `.env` file
   - Check rate limits (free tier has restrictions)
   - Ensure internet connectivity

3. **Import errors**:
   - Activate virtual environment
   - Install all dependencies
   - Check Python path

### Rate Limiting

If you hit rate limits:
- Wait for the quota to reset (usually 1 minute)
- Process files in smaller batches
- Consider upgrading to paid plan

## Performance

- **OCR Speed**: ~2-3 seconds per image
- **AI Extraction**: ~1-2 seconds per image (when not rate limited)
- **Batch Processing**: Processes multiple files sequentially

## Security

- **API Keys**: Never commit `.env` files to version control
- **Input Validation**: All inputs are validated before processing
- **Error Handling**: Sensitive information is not logged

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review error logs in `outputs/<doc_type>/errors.log`
3. Open an issue on GitHub 