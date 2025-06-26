# DocIQ API Integration

This document describes the API integration between the React frontend and Python backend for the DocIQ document processing application.

## Architecture Overview

```
┌─────────────────┐    HTTP/JSON    ┌─────────────────┐
│   React App     │ ◄─────────────► │  FastAPI Backend│
│  (Frontend)     │                 │   (Backend)     │
└─────────────────┘                 └─────────────────┘
         │                                   │
         │                                   │
         ▼                                   ▼
┌─────────────────┐                 ┌─────────────────┐
│   API Service   │                 │ Document Pipeline│
│   (api.ts)      │                 │  (Python)       │
└─────────────────┘                 └─────────────────┘
```

## Backend API (FastAPI)

### Base URL
- Development: `http://localhost:8000`
- Production: Configurable via environment variables

### Endpoints

#### Health Check
- **GET** `/health`
- Returns API status and version information

#### File Upload
- **POST** `/upload`
- Upload and process documents
- Parameters:
  - `file`: Multipart file upload
  - `document_type`: "license", "receipt", or "resume"
  - `processing_mode`: Processing mode to use

#### Processing Status
- **GET** `/status/{file_id}`
- Get processing status for a specific file

#### Documents
- **GET** `/documents` - List all processed documents
- **GET** `/documents/{document_id}` - Get specific document details
- **DELETE** `/documents/{document_id}` - Delete a document
- **GET** `/documents/{document_id}/download` - Download results as JSON

#### Statistics
- **GET** `/statistics` - Get processing statistics
- **GET** `/activity` - Get recent activity

#### Processing
- **POST** `/process/{file_id}` - Manually trigger processing
- **POST** `/retry/{file_id}` - Retry failed document

#### Validation
- **POST** `/validate` - Validate file before upload
- **GET** `/supported-types` - Get supported file types

## Frontend API Service

### Location
`src/services/api.ts`

### Key Features
- TypeScript interfaces for all API responses
- Error handling and retry logic
- File upload with progress tracking
- Real-time status polling
- Download functionality

### Main Methods

```typescript
// Upload file
uploadFile(request: UploadRequest): Promise<UploadResponse>

// Get processing status
getProcessingStatus(fileId: string): Promise<ProcessingStatus>

// Get all documents
getProcessedDocuments(): Promise<ProcessedDocument[]>

// Get document details
getDocumentById(documentId: string): Promise<ProcessedDocument>

// Download results
downloadResults(documentId: string): Promise<Blob>

// Get statistics
getStatistics(): Promise<Statistics>

// Health check
healthCheck(): Promise<{ status: string; version: string }>
```

## Data Models

### UploadRequest
```typescript
interface UploadRequest {
  file: File;
  documentType: 'license' | 'receipt' | 'resume';
  processingMode: 'license' | 'receipt' | 'resume';
}
```

### ProcessedDocument
```typescript
interface ProcessedDocument {
  id: string;
  filename: string;
  documentType: 'license' | 'receipt' | 'resume';
  status: 'completed' | 'processing' | 'failed';
  uploadedAt: string;
  processedAt?: string;
  completionRate: number;
  extractedFields: Record<string, any>;
  thumbnail?: string;
}
```

### ProcessingStatus
```typescript
interface ProcessingStatus {
  fileId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message?: string;
  result?: any;
}
```

## Integration Features

### 1. Real-time Processing
- Frontend polls backend for processing status
- Progress indicators show real-time updates
- Automatic status updates without page refresh

### 2. Error Handling
- Graceful fallback to mock mode when backend is unavailable
- User-friendly error messages
- Retry mechanisms for failed operations

### 3. File Management
- Drag-and-drop file upload
- File validation before upload
- Support for multiple file types (JPG, PNG, PDF)
- File preview and metadata display

### 4. Document Operations
- View detailed extraction results
- Download processed data as JSON
- Delete documents
- Retry failed processing

## Development Mode

When the backend is not available, the frontend automatically switches to mock mode:

- Mock data is displayed for testing
- Upload operations are simulated
- Processing status is mocked with realistic timing
- All UI functionality remains available

## Production Deployment

### Environment Variables
```bash
# Frontend (.env)
REACT_APP_API_URL=http://your-api-domain.com

# Backend (environment variables)
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://your-frontend-domain.com
```

### Security Considerations
- CORS configuration for production domains
- File size limits (10MB default)
- Input validation and sanitization
- Rate limiting for API endpoints
- Authentication and authorization (future enhancement)

## Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
npm test
```

### API Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test file upload
curl -X POST http://localhost:8000/upload \
  -F "file=@test.jpg" \
  -F "document_type=license" \
  -F "processing_mode=license"
```

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure backend CORS configuration includes frontend domain
   - Check browser console for CORS error details

2. **File Upload Failures**
   - Verify file size is under 10MB limit
   - Check file type is supported
   - Ensure backend storage directories exist

3. **Processing Failures**
   - Check backend logs for error details
   - Verify Python pipeline dependencies are installed
   - Ensure API keys are configured (Gemini, etc.)

4. **Connection Issues**
   - Verify backend is running on correct port
   - Check firewall settings
   - Ensure network connectivity

### Debug Mode
Enable debug logging in backend:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

1. **Authentication & Authorization**
   - User login/logout
   - Role-based access control
   - API key management

2. **Real-time Updates**
   - WebSocket integration
   - Server-sent events
   - Live processing status

3. **Advanced Features**
   - Batch processing
   - Scheduled processing
   - Export to multiple formats
   - Integration with external systems

4. **Performance Optimization**
   - File compression
   - Caching strategies
   - Database optimization
   - Load balancing 