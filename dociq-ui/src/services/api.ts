// API service for communicating with the Python document processing pipeline

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface UploadResponse {
  success: boolean;
  message: string;
  fileId?: string;
  error?: string;
}

export interface ProcessingStatus {
  fileId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message?: string;
  result?: any;
}

export interface ProcessedDocument {
  id: string;
  filename: string;
  documentType: 'license' | 'receipt' | 'resume';
  status: 'completed' | 'processing' | 'failed';
  uploadedAt: string;
  processedAt?: string;
  completionRate: number;
  extractedFields: Record<string, any>;
  thumbnail?: string;
  originalFile?: string;
}

export interface UploadRequest {
  file: File;
  documentType: 'license' | 'receipt' | 'resume';
  processingMode: 'license' | 'receipt' | 'resume';
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Generic request helper
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const response = await fetch(url, { ...defaultOptions, ...options });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Upload file to backend
  async uploadFile(request: UploadRequest): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', request.file);
    formData.append('documentType', request.documentType);
    formData.append('processingMode', request.processingMode);

    const response = await fetch(`${this.baseUrl}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Get processing status
  async getProcessingStatus(fileId: string): Promise<ProcessingStatus> {
    return this.request<ProcessingStatus>(`/status/${fileId}`);
  }

  // Get all processed documents
  async getProcessedDocuments(): Promise<ProcessedDocument[]> {
    return this.request<ProcessedDocument[]>('/documents');
  }

  // Get document by ID
  async getDocumentById(documentId: string): Promise<ProcessedDocument> {
    return this.request<ProcessedDocument>(`/documents/${documentId}`);
  }

  // Delete document
  async deleteDocument(documentId: string): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>(`/documents/${documentId}`, {
      method: 'DELETE',
    });
  }

  // Download document results
  async downloadResults(documentId: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/documents/${documentId}/download`);
    
    if (!response.ok) {
      throw new Error(`Download failed: ${response.status} ${response.statusText}`);
    }

    return response.blob();
  }

  // Get processing statistics
  async getStatistics(): Promise<{
    totalDocuments: number;
    processedToday: number;
    pending: number;
    successRate: number;
    averageProcessingTime: number;
  }> {
    return this.request('/statistics');
  }

  // Get recent activity
  async getRecentActivity(): Promise<Array<{
    id: string;
    type: string;
    action: string;
    time: string;
    status: string;
  }>> {
    return this.request('/activity');
  }

  // Health check
  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.request('/health');
  }

  // Process document with specific mode
  async processDocument(
    fileId: string, 
    mode: 'license' | 'receipt' | 'resume'
  ): Promise<{ success: boolean; message: string }> {
    return this.request(`/process/${fileId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ mode }),
    });
  }

  // Retry failed document
  async retryDocument(fileId: string): Promise<{ success: boolean; message: string }> {
    return this.request(`/retry/${fileId}`, {
      method: 'POST',
    });
  }

  // Get supported file types
  async getSupportedFileTypes(): Promise<{
    license: string[];
    receipt: string[];
    resume: string[];
  }> {
    return this.request('/supported-types');
  }

  // Validate file before upload
  async validateFile(file: File, documentType: string): Promise<{
    valid: boolean;
    message: string;
    maxSize?: number;
  }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('documentType', documentType);

    const response = await fetch(`${this.baseUrl}/validate`, {
      method: 'POST',
      body: formData,
    });

    return response.json();
  }
}

// Create and export a singleton instance
export const apiService = new ApiService();

// Export the class for testing
export default ApiService; 