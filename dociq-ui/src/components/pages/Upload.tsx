import React, { useState, useCallback, useEffect } from 'react';
import { 
  Upload as UploadIcon, 
  FileText, 
  File, 
  X,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { Button } from '../ui/button';
import { apiService, UploadRequest, ProcessingStatus } from '../../services/api';

interface FileWithPreview {
  file: File; // Keep the original File object intact
  id: string;
  preview?: string;
  status: 'pending' | 'uploading' | 'success' | 'error';
  documentType: 'license' | 'receipt' | 'resume';
  processingMode: 'license' | 'receipt' | 'resume';
  fileId?: string; // Backend file ID
  progress: number;
  message?: string;
}

const Upload: React.FC = () => {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [apiConnected, setApiConnected] = useState(false);

  // Check API connection on component mount
  useEffect(() => {
    checkApiConnection();
  }, []);

  const checkApiConnection = async () => {
    try {
      await apiService.healthCheck();
      setApiConnected(true);
    } catch (error) {
      console.warn('API not connected, using mock mode:', error);
      setApiConnected(false);
    }
  };

  // Drag and drop handlers
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  }, []);

  // File input handler
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    addFiles(selectedFiles);
  };

  const addFiles = (newFiles: File[]) => {
    const filesWithPreview: FileWithPreview[] = newFiles.map(file => ({
      file: file, // Keep the original File object intact
      id: Math.random().toString(36).substr(2, 9),
      status: 'pending' as const,
      documentType: 'license' as const,
      processingMode: 'license' as const,
      progress: 0,
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
    }));

    setFiles(prev => [...prev, ...filesWithPreview]);
  };

  // Remove file
  const removeFile = (id: string) => {
    setFiles(prev => {
      const fileToRemove = prev.find(f => f.id === id);
      if (fileToRemove?.preview) {
        URL.revokeObjectURL(fileToRemove.preview);
      }
      return prev.filter(f => f.id !== id);
    });
  };

  // Update file settings
  const updateFileSettings = (id: string, field: 'documentType' | 'processingMode', value: string) => {
    setFiles(prev => prev.map(file => 
      file.id === id 
        ? { ...file, [field]: value as 'license' | 'receipt' | 'resume' }
        : file
    ));
  };

  // Poll processing status
  const pollProcessingStatus = async (fileId: string, backendFileId: string) => {
    try {
      const status: ProcessingStatus = await apiService.getProcessingStatus(backendFileId);
      
      setFiles(prev => prev.map(file => {
        if (file.fileId === backendFileId) {
          return {
            ...file,
            status: status.status === 'completed' ? 'success' : 
                   status.status === 'failed' ? 'error' : 'uploading',
            progress: status.progress,
            message: status.message
          };
        }
        return file;
      }));

      // Continue polling if still processing
      if (status.status === 'pending' || status.status === 'processing') {
        setTimeout(() => pollProcessingStatus(fileId, backendFileId), 2000);
      }
    } catch (error) {
      console.error('Error polling status:', error);
      setFiles(prev => prev.map(file => 
        file.fileId === backendFileId 
          ? { ...file, status: 'error', message: 'Status check failed' }
          : file
      ));
    }
  };

  // Real upload function
  const handleUpload = async () => {
    setUploading(true);
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      try {
        // Update status to uploading
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'uploading', progress: 10 } : f
        ));

        if (apiConnected) {
          // Real API upload
          const uploadRequest: UploadRequest = {
            file: file.file,
            documentType: file.documentType,
            processingMode: file.processingMode
          };

          console.log('[DEBUG] Upload request:', {
            fileName: file.file.name,
            fileSize: file.file.size,
            documentType: file.documentType,
            processingMode: file.processingMode
          });

          const response = await apiService.uploadFile(uploadRequest);
          
          if (response.success && response.fileId) {
            // Update file with backend ID and start polling
            setFiles(prev => prev.map(f => 
              f.id === file.id 
                ? { ...f, fileId: response.fileId, progress: 20 }
                : f
            ));

            // Start polling for status
            pollProcessingStatus(file.id, response.fileId);
          } else {
            throw new Error(response.message || 'Upload failed');
          }
        } else {
          // Mock upload for development
          setFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, status: 'uploading', progress: 30 } : f
          ));

          await new Promise(resolve => setTimeout(resolve, 1000));
          
          setFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, progress: 60 } : f
          ));

          await new Promise(resolve => setTimeout(resolve, 1000));
          
          const success = Math.random() > 0.2; // 80% success rate
          setFiles(prev => prev.map(f => 
            f.id === file.id 
              ? { 
                  ...f, 
                  status: success ? 'success' : 'error',
                  progress: 100,
                  message: success ? 'Processing completed' : 'Processing failed'
                }
              : f
          ));
        }
      } catch (error) {
        console.error('Upload error:', error);
        setFiles(prev => prev.map(f => 
          f.id === file.id 
            ? { 
                ...f, 
                status: 'error', 
                progress: 0,
                message: error instanceof Error ? error.message : 'Upload failed'
              }
            : f
        ));
      }
    }
    
    setUploading(false);
  };

  const getStatusIcon = (status: FileWithPreview['status']) => {
    switch (status) {
      case 'uploading':
        return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusText = (status: FileWithPreview['status']) => {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'uploading':
        return 'Uploading...';
      case 'success':
        return 'Success';
      case 'error':
        return 'Error';
      default:
        return '';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Upload Documents</h2>
        <p className="text-gray-600">Upload and process your documents with AI</p>
        {!apiConnected && (
          <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800">
            ⚠️ API not connected - running in mock mode
          </div>
        )}
      </div>

      {/* Drag and Drop Zone */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragOver 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <UploadIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <div className="space-y-2">
          <p className="text-lg font-medium text-gray-900">
            Drop files here or click to browse
          </p>
          <p className="text-sm text-gray-500">
            Supports JPG, PNG, and PDF files
          </p>
          <Button
            variant="outline"
            onClick={() => document.getElementById('file-input')?.click()}
            className="mt-4"
          >
            Choose Files
          </Button>
        </div>
        <input
          id="file-input"
          type="file"
          multiple
          accept=".jpg,.jpeg,.png,.pdf"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* File Preview List */}
      {files.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Files to Upload ({files.length})
            </h3>
          </div>
          <div className="p-6 space-y-4">
            {files.map((file) => (
              <div key={file.id} className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg">
                {/* File Preview */}
                <div className="flex-shrink-0">
                  {file.preview ? (
                    <img 
                      src={file.preview} 
                      alt={file.file.name}
                      className="w-12 h-12 object-cover rounded"
                    />
                  ) : (
                    <div className="w-12 h-12 bg-gray-100 rounded flex items-center justify-center">
                      <FileText className="w-6 h-6 text-gray-400" />
                    </div>
                  )}
                </div>

                {/* File Info */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {file.file.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {file.file.size && file.file.size > 0 ? (file.file.size / 1024 / 1024).toFixed(2) : '0.00'} MB
                  </p>
                  {file.message && (
                    <p className="text-xs text-red-600 mt-1">{file.message}</p>
                  )}
                </div>

                {/* Document Type Selection */}
                <div className="flex items-center space-x-4">
                  <div>
                    <label className="text-xs font-medium text-gray-700 mb-1 block">
                      Document Type
                    </label>
                    <div className="flex space-x-2">
                      {(['license', 'receipt', 'resume'] as const).map((type) => (
                        <label key={type} className="flex items-center space-x-1">
                          <input
                            type="radio"
                            name={`doc-type-${file.id}`}
                            value={type}
                            checked={file.documentType === type}
                            onChange={(e) => updateFileSettings(file.id, 'documentType', e.target.value)}
                            className="w-3 h-3 text-blue-600"
                            disabled={file.status === 'uploading'}
                          />
                          <span className="text-xs capitalize">{type}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Processing Mode */}
                  <div>
                    <label className="text-xs font-medium text-gray-700 mb-1 block">
                      Processing Mode
                    </label>
                    <select
                      value={file.processingMode}
                      onChange={(e) => updateFileSettings(file.id, 'processingMode', e.target.value)}
                      className="text-xs border border-gray-300 rounded px-2 py-1"
                      disabled={file.status === 'uploading'}
                    >
                      <option value="license">License</option>
                      <option value="receipt">Receipt</option>
                      <option value="resume">Resume</option>
                    </select>
                  </div>

                  {/* Status */}
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(file.status)}
                    <span className={`text-xs ${
                      file.status === 'success' ? 'text-green-600' :
                      file.status === 'error' ? 'text-red-600' :
                      file.status === 'uploading' ? 'text-blue-600' :
                      'text-gray-500'
                    }`}>
                      {getStatusText(file.status)}
                    </span>
                  </div>

                  {/* Remove Button */}
                  <button
                    onClick={() => removeFile(file.id)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                    disabled={file.status === 'uploading'}
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Upload Button */}
          <div className="p-6 border-t border-gray-200">
            <Button
              onClick={handleUpload}
              disabled={uploading || files.length === 0}
              className="w-full"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <UploadIcon className="w-4 h-4 mr-2" />
                  Upload and Process ({files.length} files)
                </>
              )}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Upload; 