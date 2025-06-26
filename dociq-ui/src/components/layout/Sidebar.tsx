import React from 'react';
import { 
  LayoutDashboard, 
  Upload, 
  FileText, 
  Settings,
  FileImage,
  CreditCard,
  User
} from 'lucide-react';
import { cn } from '../../lib/utils';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload', icon: Upload },
    { id: 'results', label: 'Results', icon: FileText },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const documentTypes = [
    { id: 'license', label: 'Driving License', icon: CreditCard },
    { id: 'receipt', label: 'Receipts', icon: FileImage },
    { id: 'resume', label: 'Resumes', icon: User },
  ];

  return (
    <div className="w-64 bg-white border-r border-gray-200 h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-900">DocIQ</h1>
        <p className="text-sm text-gray-500">Smart Document Parser</p>
      </div>

      {/* Navigation Tabs */}
      <nav className="flex-1 p-4">
        <div className="space-y-2">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Navigation
          </h3>
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={cn(
                  "w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors",
                  activeTab === tab.id
                    ? "bg-blue-50 text-blue-700 border border-blue-200"
                    : "text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                )}
              >
                <Icon className="w-5 h-5 mr-3" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Document Types */}
        <div className="mt-8 space-y-2">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Document Types
          </h3>
          {documentTypes.map((type) => {
            const Icon = type.icon;
            return (
              <div
                key={type.id}
                className="flex items-center px-3 py-2 text-sm text-gray-600"
              >
                <Icon className="w-4 h-4 mr-3" />
                {type.label}
              </div>
            );
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500">
          <p>Version 1.0.0</p>
          <p>Powered by AI</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar; 