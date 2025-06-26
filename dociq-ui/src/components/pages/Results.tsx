import React, { useState, useEffect, useCallback } from 'react';
import { 
  FileText, 
  Search, 
  Download, 
  Eye, 
  Trash2, 
  RefreshCw,
  CalendarDays,
  CheckCircle,
  AlertCircle,
  Clock,
  X
} from 'lucide-react';
import { Button } from '../ui/button';
import { apiService, ProcessedDocument } from '../../services/api';

interface DocumentDetail {
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

const Results: React.FC = () => {
  const [documents, setDocuments] = useState<ProcessedDocument[]>([]);
  const [filteredDocuments, setFilteredDocuments] = useState<ProcessedDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('uploadedAt');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedDocument, setSelectedDocument] = useState<DocumentDetail | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<string | null>(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const filterAndSortDocuments = useCallback(() => {
    let filtered = [...documents];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(doc =>
        doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
        JSON.stringify(doc.extractedFields).toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(doc => doc.status === statusFilter);
    }

    // Apply type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(doc => doc.documentType === typeFilter);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue: any = a[sortBy as keyof ProcessedDocument];
      let bValue: any = b[sortBy as keyof ProcessedDocument];

      if (sortBy === 'uploadedAt' || sortBy === 'processedAt') {
        aValue = new Date(aValue || 0).getTime();
        bValue = new Date(bValue || 0).getTime();
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredDocuments(filtered);
  }, [documents, searchTerm, statusFilter, typeFilter, sortBy, sortOrder]);

  useEffect(() => {
    filterAndSortDocuments();
  }, [filterAndSortDocuments]);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getProcessedDocuments();
      setDocuments(data);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to load documents');
      
      // Set mock data for development
      setDocuments([
        {
          id: '1',
          filename: 'license_001.jpg',
          documentType: 'license',
          status: 'completed',
          uploadedAt: new Date().toISOString(),
          processedAt: new Date().toISOString(),
          completionRate: 95.0,
          extractedFields: {
            name: 'John Doe',
            licenseNumber: 'DL123456789',
            dateOfBirth: '1990-05-15',
            expiryDate: '2025-05-15',
            address: '123 Main St, City, State'
          }
        },
        {
          id: '2',
          filename: 'receipt_001.jpg',
          documentType: 'receipt',
          status: 'completed',
          uploadedAt: new Date(Date.now() - 3600000).toISOString(),
          processedAt: new Date(Date.now() - 3500000).toISOString(),
          completionRate: 92.0,
          extractedFields: {
            merchantName: 'Walmart',
            totalAmount: '$156.78',
            dateOfPurchase: '2024-01-14',
            items: [
              { name: 'Groceries', price: '$45.23' },
              { name: 'Electronics', price: '$111.55' }
            ]
          }
        },
        {
          id: '3',
          filename: 'resume_001.pdf',
          documentType: 'resume',
          status: 'processing',
          uploadedAt: new Date(Date.now() - 1800000).toISOString(),
          completionRate: 45.0,
          extractedFields: {}
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (documentId: string) => {
    try {
      const document = await apiService.getDocumentById(documentId);
      setSelectedDocument(document);
      setShowDetailModal(true);
    } catch (err) {
      console.error('Error fetching document details:', err);
      // Fallback to local data
      const localDoc = documents.find(d => d.id === documentId);
      if (localDoc) {
        setSelectedDocument(localDoc);
        setShowDetailModal(true);
      }
    }
  };

  const handleDownload = async (documentId: string) => {
    try {
      const blob = await apiService.downloadResults(documentId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `document_${documentId}_results.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading document:', err);
      alert('Failed to download document');
    }
  };

  const handleDeleteClick = (documentId: string) => {
    setDocumentToDelete(documentId);
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    if (!documentToDelete) return;

    try {
      await apiService.deleteDocument(documentToDelete);
      setDocuments(prev => prev.filter(d => d.id !== documentToDelete));
      setShowDeleteModal(false);
      setDocumentToDelete(null);
    } catch (err) {
      console.error('Error deleting document:', err);
      alert('Failed to delete document');
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteModal(false);
    setDocumentToDelete(null);
  };

  const handleRetry = async (documentId: string) => {
    try {
      await apiService.retryDocument(documentId);
      // Refresh the document list
      fetchDocuments();
    } catch (err) {
      console.error('Error retrying document:', err);
      alert('Failed to retry document processing');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-blue-500" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'license':
        return <FileText className="w-4 h-4 text-blue-500" />;
      case 'receipt':
        return <FileText className="w-4 h-4 text-green-500" />;
      case 'resume':
        return <FileText className="w-4 h-4 text-purple-500" />;
      default:
        return <FileText className="w-4 h-4 text-gray-400" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderExtractedFields = (fields: Record<string, any>) => {
    if (!fields || Object.keys(fields).length === 0) {
      return <p className="text-gray-500">No data extracted</p>;
    }

    return (
      <div className="space-y-2">
        {Object.entries(fields).map(([key, value]) => (
          <div key={key} className="flex justify-between">
            <span className="font-medium text-gray-700 capitalize">
              {key.replace(/([A-Z])/g, ' $1').trim()}:
            </span>
            <span className="text-gray-900">
              {Array.isArray(value) 
                ? value.map((item, index) => (
                    <div key={index} className="text-right">
                      {typeof item === 'object' 
                        ? Object.entries(item).map(([k, v]) => `${k}: ${v}`).join(', ')
                        : item
                      }
                    </div>
                  ))
                : String(value)
              }
            </span>
          </div>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Results</h2>
          <p className="text-gray-600">View and manage processed documents</p>
        </div>
        <Button onClick={fetchDocuments} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          {error}
        </div>
      )}

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Status</option>
            <option value="completed">Completed</option>
            <option value="processing">Processing</option>
            <option value="failed">Failed</option>
          </select>

          {/* Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Types</option>
            <option value="license">License</option>
            <option value="receipt">Receipt</option>
            <option value="resume">Resume</option>
          </select>

          {/* Sort */}
          <select
            value={`${sortBy}-${sortOrder}`}
            onChange={(e) => {
              const [field, order] = e.target.value.split('-');
              setSortBy(field);
              setSortOrder(order as 'asc' | 'desc');
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="uploadedAt-desc">Newest First</option>
            <option value="uploadedAt-asc">Oldest First</option>
            <option value="filename-asc">Name A-Z</option>
            <option value="filename-desc">Name Z-A</option>
            <option value="completionRate-desc">Highest Completion</option>
            <option value="completionRate-asc">Lowest Completion</option>
          </select>
        </div>
      </div>

      {/* Results Count */}
      <div className="text-sm text-gray-600">
        Showing {filteredDocuments.length} of {documents.length} documents
      </div>

      {/* Documents List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {filteredDocuments.length === 0 ? (
          <div className="p-8 text-center">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No documents found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredDocuments.map((document) => (
              <div key={document.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      {getTypeIcon(document.documentType)}
                    </div>
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {document.filename}
                      </h3>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span className="capitalize">{document.documentType}</span>
                        <span>•</span>
                        <span>{formatDate(document.uploadedAt)}</span>
                        <span>•</span>
                        <span className="flex items-center space-x-1">
                          {getStatusIcon(document.status)}
                          <span className="capitalize">{document.status}</span>
                        </span>
                        <span>•</span>
                        <span>{document.completionRate}% complete</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleViewDetails(document.id)}
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      View
                    </Button>
                    
                    {document.status === 'completed' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDownload(document.id)}
                      >
                        <Download className="w-4 h-4 mr-1" />
                        Download
                      </Button>
                    )}
                    
                    {document.status === 'failed' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRetry(document.id)}
                      >
                        <RefreshCw className="w-4 h-4 mr-1" />
                        Retry
                      </Button>
                    )}
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteClick(document.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4 mr-1" />
                      Delete
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {showDetailModal && selectedDocument && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  Document Details
                </h3>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Basic Info */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Basic Information</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Filename:</span>
                    <p className="font-medium">{selectedDocument.filename}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Type:</span>
                    <p className="font-medium capitalize">{selectedDocument.documentType}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Status:</span>
                    <p className="font-medium capitalize">{selectedDocument.status}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Completion Rate:</span>
                    <p className="font-medium">{selectedDocument.completionRate}%</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Uploaded:</span>
                    <p className="font-medium">{formatDate(selectedDocument.uploadedAt)}</p>
                  </div>
                  {selectedDocument.processedAt && (
                    <div>
                      <span className="text-gray-500">Processed:</span>
                      <p className="font-medium">{formatDate(selectedDocument.processedAt)}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Extracted Fields */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Extracted Data</h4>
                <div className="bg-gray-50 p-4 rounded-lg">
                  {renderExtractedFields(selectedDocument.extractedFields)}
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
              {selectedDocument.status === 'completed' && (
                <Button onClick={() => handleDownload(selectedDocument.id)}>
                  <Download className="w-4 h-4 mr-2" />
                  Download Results
                </Button>
              )}
              <Button variant="outline" onClick={() => setShowDetailModal(false)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-md w-full mx-4 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Confirm Delete
              </h3>
              <button
                onClick={handleDeleteCancel}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete this document? This action cannot be undone.
            </p>
            
            <div className="flex justify-end space-x-3">
              <Button variant="outline" onClick={handleDeleteCancel}>
                Cancel
              </Button>
              <Button 
                onClick={handleDeleteConfirm}
                className="bg-red-600 hover:bg-red-700"
              >
                Delete
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Results; 