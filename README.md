# DocIQ: Smart Document Parser

A comprehensive document processing pipeline that combines OCR technology with Google's Gemini AI to extract structured data from various document types including driving licenses, receipts, and resumes.

## 🚀 Features

### Core Functionality
- **Multi-Document Support**: Process driving licenses, receipts, and resumes
- **Advanced OCR**: Dual OCR engine (EasyOCR + Tesseract fallback)
- **AI-Powered Extraction**: Google Gemini AI integration for intelligent field extraction
- **Modular Architecture**: Separate pipelines for each document type
- **Fallback Mechanisms**: Regex parsing with AI fallback for missing fields
- **Real-time Processing**: Live status updates and progress tracking

### Frontend Features
- **Modern React UI**: Built with TypeScript and Tailwind CSS
- **Responsive Design**: Fixed sidebar layout with mobile-friendly interface
- **Drag & Drop Upload**: Intuitive file upload with preview
- **Real-time Status**: Live processing status and progress indicators
- **Search & Filter**: Advanced document management with search capabilities
- **Settings Management**: Comprehensive configuration options

### Backend Features
- **FastAPI Backend**: High-performance REST API
- **File Validation**: Comprehensive file type and size validation
- **Error Handling**: Robust error handling with detailed logging
- **Mock Mode**: Development mode with simulated AI responses
- **Production Ready**: Scalable architecture with proper logging

## 📁 Project Structure

```
assignment/
├── doc_pipeline/                 # Core document processing engine
│   ├── extractors/              # Document-specific extractors
│   │   ├── license.py          # Driving license extraction
│   │   ├── receipt.py          # Receipt extraction
│   │   └── resume.py           # Resume extraction
│   ├── llm/                    # AI integration
│   │   └── gemini_client.py    # Google Gemini API client
│   ├── ocr/                    # OCR engines
│   │   └── ocr_engine.py       # Dual OCR implementation
│   ├── parsers/                # Regex-based parsers
│   │   ├── driving_license_parser.py
│   │   ├── receipt_parser.py
│   │   └── resume_parser.py
│   ├── pipeline/               # Processing pipelines
│   │   ├── license_pipeline.py
│   │   ├── receipt_pipeline.py
│   │   └── resume_pipeline.py
│   ├── prompts/                # AI prompt templates
│   │   ├── license_extraction.txt
│   │   └── receipt_extraction.txt
│   ├── utils/                  # Utility functions
│   │   └── validators.py       # Field validation
│   ├── cli.py                  # Command-line interface
│   ├── config.py               # Configuration settings
│   ├── main.py                 # Main processing logic
│   └── requirements.txt        # Python dependencies
│
├── dociq-ui/                   # React frontend application
│   ├── backend/                # FastAPI backend
│   │   ├── main.py            # API server
│   │   └── requirements.txt   # Backend dependencies
│   ├── src/                   # React source code
│   │   ├── components/        # UI components
│   │   │   ├── layout/        # Layout components
│   │   │   ├── pages/         # Page components
│   │   │   └── ui/            # Reusable UI components
│   │   ├── services/          # API services
│   │   └── lib/               # Utility libraries
│   ├── public/                # Static assets
│   ├── package.json           # Frontend dependencies
│   └── start.sh               # Development startup script
│
└── README.md                  # This file
```

## 🛠️ Technology Stack

### Backend
- **Python 3.8+**: Core programming language
- **FastAPI**: High-performance web framework
- **EasyOCR**: Primary OCR engine
- **Tesseract**: Fallback OCR engine
- **Google Gemini AI**: AI-powered text extraction
- **PyMuPDF**: PDF processing
- **pdfplumber**: PDF text extraction
- **Typer**: CLI framework

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Modern UI components
- **Lucide React**: Icon library
- **Axios**: HTTP client

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- Google Gemini API key

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd assignment

# Setup Python environment
cd doc_pipeline
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup React environment
cd ../dociq-ui
npm install
```

### 2. Configure API Keys

Create a `.env` file in the backend directory:

```bash
cd dociq-ui/backend
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
```

### 3. Start the Application

```bash
# Start both frontend and backend
cd dociq-ui
./start.sh
```

Or start them separately:

```bash
# Backend (from dociq-ui/backend)
source venv/bin/activate
python main.py

# Frontend (from dociq-ui)
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## 📖 Usage

### Web Interface

1. **Upload Documents**: Drag and drop files or click to browse
2. **Select Document Type**: Choose from License, Receipt, or Resume
3. **Processing Mode**: Select Standard or Strict processing
4. **Monitor Progress**: Real-time status updates
5. **View Results**: Search, filter, and download extracted data

### Command Line Interface

```bash
# Process a single file
python cli.py process --mode license --input path/to/file.jpg --output results/

# Process entire directory
python cli.py process --mode receipt --input path/to/directory --output results/

# Test mode (process one file)
python cli.py process --mode resume --input path/to/directory --output results/ --test
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `USE_MOCK_GEMINI` | Use mock AI responses | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Processing Modes

- **Standard**: Balanced accuracy and speed
- **Strict**: Higher accuracy with more validation

## 📊 Supported Document Types

### Driving Licenses
- **Extracted Fields**: Name, License Number, Date of Birth, Expiry Date, Address
- **Supported Formats**: JPG, PNG, PDF
- **Processing**: OCR + AI extraction with regex validation

### Receipts
- **Extracted Fields**: Merchant, Date, Total Amount, Items, Tax
- **Supported Formats**: JPG, PNG, PDF
- **Processing**: OCR + AI extraction with amount validation

### Resumes
- **Extracted Fields**: Name, Email, Phone, Skills, Experience, Education
- **Supported Formats**: JPG, PNG, PDF
- **Processing**: Text extraction + AI parsing with phone validation

## 🔍 API Endpoints

### Document Processing
- `POST /upload` - Upload and process documents
- `GET /status/{job_id}` - Get processing status
- `GET /documents` - List all processed documents
- `GET /documents/{doc_id}` - Get document details
- `DELETE /documents/{doc_id}` - Delete document

### Statistics
- `GET /statistics` - Get processing statistics
- `GET /health` - Health check endpoint

## 🧪 Testing

### Mock Mode
For development and testing without API costs:

```bash
export USE_MOCK_GEMINI=true
python main.py
```

### API Testing
```bash
# Test upload endpoint
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_document.jpg" \
  -F "documentType=receipt" \
  -F "processingMode=standard"
```

## 🚀 Production Deployment

### Backend Deployment
1. Set up a production Python environment
2. Configure environment variables
3. Use a production WSGI server (Gunicorn)
4. Set up reverse proxy (Nginx)

### Frontend Deployment
1. Build the React application: `npm run build`
2. Serve static files with a web server
3. Configure API endpoint URLs

### Docker Deployment
```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔒 Security Considerations

- API keys are stored in environment variables
- File upload validation prevents malicious files
- CORS configuration for frontend-backend communication
- Input sanitization and validation

## 📈 Performance Optimization

- Dual OCR engines for reliability
- Caching of processed results
- Async processing for large files
- Efficient image preprocessing

## 🐛 Troubleshooting

### Common Issues

1. **OCR Errors**: Ensure Tesseract is installed
2. **API Quota Exceeded**: Switch to mock mode or upgrade plan
3. **Import Errors**: Check Python path and virtual environment
4. **Frontend Not Loading**: Verify backend is running on port 8000

### Logs
- Backend logs: Check console output
- Frontend logs: Browser developer tools
- Processing logs: Stored in output directories

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for intelligent text extraction
- EasyOCR and Tesseract for OCR capabilities
- FastAPI for the high-performance backend
- React and Tailwind CSS for the modern frontend

---

**DocIQ** - Transforming document processing with AI-powered intelligence. 