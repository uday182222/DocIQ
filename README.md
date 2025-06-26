# DOC-IQ: Intelligent Document Processing Pipeline

DOC-IQ is a comprehensive document processing system that uses OCR and AI to extract structured data from various document types including resumes, driver's licenses, and receipts. Built with a modular, config-driven architecture for easy extensibility.

## 🚀 Features

### Document Types Supported
- **Resumes**: Extract FullName, Email, PhoneNumber, Skills, WorkExperience, Education
- **Driver's Licenses**: Extract Name, DateOfBirth, LicenseNumber, IssuingState, ExpiryDate
- **Receipts**: Extract StoreName, LineItems, TotalAmount, PaymentMethod, and more with discrepancy detection

### Key Capabilities
- **OCR Processing**: Uses EasyOCR for robust text extraction
- **AI-Powered Parsing**: OpenAI GPT-4o-mini for intelligent field extraction
- **Config-Driven Architecture**: Easy to add new document types
- **Validation Logic**: Built-in validation with discrepancy detection
- **Batch Processing**: Process multiple documents efficiently
- **CLI Interface**: Easy-to-use command-line tools
- **API Ready**: FastAPI backend for web integration
- **Comprehensive Testing**: Automated testing for all document types

## 📁 Project Structure

```
DOC-IQ/
├── doc_pipeline/
│   ├── pipeline/
│   │   └── generic_pipeline.py    # Main processing pipeline (config-driven)
│   ├── config/
│   │   ├── __init__.py            # Configuration package
│   │   └── doc_config.py          # Document type configurations
│   ├── llm/
│   │   └── llm_client.py          # OpenAI integration
│   ├── prompts/                   # AI prompts for each document type
│   │   ├── resume_extraction.txt
│   │   ├── license_extraction.txt
│   │   └── receipt_extraction.txt
│   ├── ocr/
│   │   └── ocr_engine.py          # OCR processing engine
│   ├── utils/
│   │   ├── validators.py          # Data validation logic
│   │   └── file_utils.py          # File handling utilities
│   ├── cli.py                     # Command-line interface
│   └── main.py                    # FastAPI server
├── test/                          # Test scripts and outputs
│   ├── output/                    # Processed results
│   ├── resumes/                   # Resume test data
│   ├── driving_license/           # License test data
│   └── shop_receipts/             # Receipt test data
├── test_*.py                      # Individual test scripts
├── test_parser.py                 # Comprehensive config test
├── test_doc_config.py             # Configuration module test
└── requirements.txt               # Python dependencies
```

## 🛠 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DOC-IQ
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up OpenAI API key**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

## 📖 Usage

### Command Line Interface

**Process a single document:**
```bash
python doc_pipeline/cli.py --mode resume --input path/to/resume.jpg --output test/output/resume
```

**Process a directory of documents:**
```bash
python doc_pipeline/cli.py --mode receipt --input doc_pipeline/data/shop_receipts --output test/output/shop_receipts
```

### Supported Modes
- `resume` - Extract resume information
- `license` - Extract driver's license information  
- `receipt` - Extract receipt information with discrepancy detection

### API Usage

**Start the FastAPI server:**
```bash
cd doc_pipeline
uvicorn main:app --reload
```

**Upload and process a document:**
```bash
curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@path/to/document.jpg" \
     -F "doc_type=resume"
```

## 🧪 Testing

### Comprehensive Configuration Test
Test all document types with mock data:
```bash
python test_parser.py
```

### Individual Document Type Tests
```bash
# Test resume parser
python test_resume_parser.py

# Test license parser  
python test_license_parser.py

# Test receipt parser
python test_receipt_parser.py

# Test configuration module
python test_doc_config.py
```

### Test Results
- **Configuration Test**: 100% success rate (3/3 document types)
- **Resume Processing**: 100% success rate (31/31 files)
- **License Processing**: 82% success rate (9/11 files)
- **Receipt Processing**: 100% success rate (22/22 files)

## 📊 Results

### Resume Processing
- **Success Rate**: 100% (31/31 files processed)
- **Fields Extracted**: FullName, Email, PhoneNumber, Skills, WorkExperience, Education
- **Output Format**: Structured JSON with validation

### Driver's License Processing
- **Success Rate**: 82% (9/11 files processed)
- **Fields Extracted**: Name, DateOfBirth, LicenseNumber, IssuingState, ExpiryDate
- **Special Features**: Strict name extraction from numbered fields
- **Output Format**: Validated JSON with required field enforcement

### Receipt Processing
- **Success Rate**: 100% (22/22 files processed)
- **Fields Extracted**: StoreName, LineItems, TotalAmount, PaymentMethod, CardLast4Digits
- **Special Features**: Discrepancy detection with 2% tolerance
- **Output Format**: Unified JSON format with comprehensive validation

## 🧩 Onboarding a New Document Type in 5 Minutes

Want to add a new document type? Follow these quick steps:

- **1. Add a Prompt:**
  - Create a new prompt file in `doc_pipeline/prompts/`, e.g. `mydoc_extraction.txt`.
  - Write clear instructions and specify the fields you want to extract.

- **2. Register in Config:**
  - Open `doc_pipeline/config/doc_config.py`.
  - Add a new entry to the `DOCUMENT_CONFIGS` dictionary for your document type:
    ```python
    "mydoc": {
        "required_fields": ["Field1", "Field2"],
        "optional_fields": ["Field3"],
        "prompt_path": "doc_pipeline/prompts/mydoc_extraction.txt",
        "validator_fn": your_validator_function,  # Optional, see below
        "postprocess_fn": your_postprocess_function  # Optional, see below
    }
    ```

- **3. (Optional) Add Validator/Postprocessor:**
  - For custom validation or postprocessing, define functions in `doc_config.py` and reference them in your config entry.
  - If not needed, you can reuse existing ones or use simple pass-through functions.

- **4. Run the CLI or API:**
  - Use your new document type with the CLI or API:
    ```bash
    python doc_pipeline/cli.py --mode mydoc --input path/to/file --output path/to/output
    ```
    Or via the API: set `doc_type` to `mydoc` in your request.

That's it! Your new document type is now supported end-to-end.

## 🔧 Technical Details

### Config-Driven Architecture
- **Document Configuration**: Centralized in `doc_pipeline/config/doc_config.py`
- **Dynamic Loading**: Prompts, validators, and postprocessors loaded at runtime
- **Type Safety**: Comprehensive validation for all document types
- **Extensibility**: Easy to add new document types without code changes

### OCR Engine
- **Engine**: EasyOCR with CPU optimization
- **Languages**: English (configurable for multi-language support)
- **Preprocessing**: Automatic image enhancement and noise reduction

### AI Integration
- **Model**: OpenAI GPT-4o-mini
- **Temperature**: 0.0 (deterministic output)
- **Max Tokens**: 2048
- **Prompt Engineering**: Specialized prompts for each document type

### Validation Logic
- **Required Fields**: Enforced per document type
- **Data Types**: Automatic type conversion and validation
- **Discrepancy Detection**: Mathematical validation for receipts
- **Error Handling**: Graceful failure with detailed error messages

## 📈 Performance Metrics

| Document Type | Files Processed | Success Rate | Avg Processing Time |
|---------------|----------------|--------------|-------------------|
| Resumes       | 31             | 100%         | ~15 seconds       |
| Licenses      | 11             | 82%          | ~12 seconds       |
| Receipts      | 22             | 100%         | ~18 seconds       |

## 🚨 Discrepancy Detection

The receipt parser includes intelligent discrepancy detection:
- **Tolerance**: 2% difference threshold
- **Detection**: Automatically flags when sum of items ≠ total amount
- **Warnings**: Logged but don't fail validation
- **Use Cases**: Helps identify OCR errors or missing items

## 🔒 Security & Privacy

- **API Keys**: Environment variable based configuration
- **Data Processing**: Local OCR processing, secure API calls
- **Output**: Structured JSON without sensitive data exposure
- **Validation**: Input sanitization and type checking

## 🛠 Development

### Adding New Document Types

1. Create a new prompt file in `doc_pipeline/prompts/`
2. Add configuration entry in `doc_pipeline/config/doc_config.py`
3. (Optional) Create custom validator/postprocessor functions
4. Test with `python test_parser.py`
5. Update CLI interface if needed

### Customizing Prompts

Edit the prompt files in `doc_pipeline/prompts/` to:
- Change field extraction logic
- Add new fields
- Modify validation rules
- Improve accuracy for specific document types

### Testing New Document Types

```bash
# Test configuration loading
python test_doc_config.py

# Test end-to-end processing
python test_parser.py

# Test individual document type
python test_parser.py --doc_type your_new_type
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests using the existing test framework
5. Submit a pull request

## 📞 Support

For questions or issues:
- Create an issue in the repository
- Check the test scripts for examples
- Review the configuration guide for adding new document types

## 🎯 Roadmap

- [ ] Multi-language OCR support
- [ ] Additional document types (invoices, contracts, forms)
- [ ] Web-based UI for document upload and processing
- [ ] Real-time processing with WebSocket support
- [ ] Advanced discrepancy detection algorithms
- [ ] Machine learning model fine-tuning capabilities 