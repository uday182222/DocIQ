import React, { useState } from 'react';
import { 
  Settings as SettingsIcon,
  Save, 
  RefreshCw, 
  Zap, 
  Bell, 
  Shield, 
  Palette,
  Globe,
  Database,
  User
} from 'lucide-react';
import { Button } from '../ui/button';

interface SettingsConfig {
  processing: {
    autoProcess: boolean;
    maxFileSize: number;
    allowedFormats: string[];
    enableAI: boolean;
    confidenceThreshold: number;
  };
  notifications: {
    emailNotifications: boolean;
    processingComplete: boolean;
    processingFailed: boolean;
    weeklyReports: boolean;
  };
  security: {
    enableEncryption: boolean;
    dataRetentionDays: number;
    allowDataExport: boolean;
    requireAuthentication: boolean;
  };
  appearance: {
    theme: 'light' | 'dark' | 'auto';
    language: string;
    timezone: string;
  };
}

const Settings: React.FC = () => {
  const [settings, setSettings] = useState<SettingsConfig>({
    processing: {
      autoProcess: true,
      maxFileSize: 10,
      allowedFormats: ['.jpg', '.jpeg', '.png', '.pdf'],
      enableAI: true,
      confidenceThreshold: 80
    },
    notifications: {
      emailNotifications: true,
      processingComplete: true,
      processingFailed: true,
      weeklyReports: false
    },
    security: {
      enableEncryption: true,
      dataRetentionDays: 90,
      allowDataExport: true,
      requireAuthentication: true
    },
    appearance: {
      theme: 'light',
      language: 'en',
      timezone: 'UTC'
    }
  });

  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const updateSetting = (category: keyof SettingsConfig, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
    setHasChanges(true);
  };

  const handleSave = async () => {
    setIsSaving(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsSaving(false);
    setHasChanges(false);
  };

  const handleReset = () => {
    // Reset to default settings
    setSettings({
      processing: {
        autoProcess: true,
        maxFileSize: 10,
        allowedFormats: ['.jpg', '.jpeg', '.png', '.pdf'],
        enableAI: true,
        confidenceThreshold: 80
      },
      notifications: {
        emailNotifications: true,
        processingComplete: true,
        processingFailed: true,
        weeklyReports: false
      },
      security: {
        enableEncryption: true,
        dataRetentionDays: 90,
        allowDataExport: true,
        requireAuthentication: true
      },
      appearance: {
        theme: 'light',
        language: 'en',
        timezone: 'UTC'
      }
    });
    setHasChanges(false);
  };

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
        <p className="text-gray-600">Configure your document processing preferences</p>
      </div>

      {/* Save/Reset Buttons */}
      <div className="flex justify-between items-center">
        <div className="flex space-x-2">
          <Button
            onClick={handleSave}
            disabled={!hasChanges || isSaving}
            className="flex items-center"
          >
            {isSaving ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            {isSaving ? 'Saving...' : 'Save Changes'}
          </Button>
          <Button
            variant="outline"
            onClick={handleReset}
            disabled={isSaving}
          >
            Reset to Defaults
          </Button>
        </div>
        {hasChanges && (
          <span className="text-sm text-orange-600">You have unsaved changes</span>
        )}
      </div>

      {/* Settings Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Processing Settings */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <Zap className="w-5 h-5 text-blue-500 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Processing</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Auto-process files</label>
                <p className="text-xs text-gray-500">Automatically process files when uploaded</p>
              </div>
              <input
                type="checkbox"
                checked={settings.processing.autoProcess}
                onChange={(e) => updateSetting('processing', 'autoProcess', e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700">Max file size (MB)</label>
              <input
                type="number"
                value={settings.processing.maxFileSize}
                onChange={(e) => updateSetting('processing', 'maxFileSize', parseInt(e.target.value))}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="1"
                max="100"
              />
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700">Confidence threshold (%)</label>
              <input
                type="range"
                min="50"
                max="100"
                value={settings.processing.confidenceThreshold}
                onChange={(e) => updateSetting('processing', 'confidenceThreshold', parseInt(e.target.value))}
                className="mt-1 block w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>50%</span>
                <span>{settings.processing.confidenceThreshold}%</span>
                <span>100%</span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Enable AI processing</label>
                <p className="text-xs text-gray-500">Use advanced AI for better accuracy</p>
              </div>
              <input
                type="checkbox"
                checked={settings.processing.enableAI}
                onChange={(e) => updateSetting('processing', 'enableAI', e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Notifications Settings */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <Bell className="w-5 h-5 text-green-500 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Email notifications</label>
                <p className="text-xs text-gray-500">Receive notifications via email</p>
              </div>
              <input
                type="checkbox"
                checked={settings.notifications.emailNotifications}
                onChange={(e) => updateSetting('notifications', 'emailNotifications', e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Processing complete</label>
                <p className="text-xs text-gray-500">Notify when processing is finished</p>
              </div>
              <input
                type="checkbox"
                checked={settings.notifications.processingComplete}
                onChange={(e) => updateSetting('notifications', 'processingComplete', e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Processing failed</label>
                <p className="text-xs text-gray-500">Notify when processing fails</p>
              </div>
              <input
                type="checkbox"
                checked={settings.notifications.processingFailed}
                onChange={(e) => updateSetting('notifications', 'processingFailed', e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Weekly reports</label>
                <p className="text-xs text-gray-500">Receive weekly processing summaries</p>
              </div>
              <input
                type="checkbox"
                checked={settings.notifications.weeklyReports}
                onChange={(e) => updateSetting('notifications', 'weeklyReports', e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Security Settings */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <Shield className="w-5 h-5 text-red-500 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Security</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Enable encryption</label>
                <p className="text-xs text-gray-500">Encrypt stored documents</p>
              </div>
              <input
                type="checkbox"
                checked={settings.security.enableEncryption}
                onChange={(e) => updateSetting('security', 'enableEncryption', e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700">Data retention (days)</label>
              <input
                type="number"
                value={settings.security.dataRetentionDays}
                onChange={(e) => updateSetting('security', 'dataRetentionDays', parseInt(e.target.value))}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="1"
                max="365"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Allow data export</label>
                <p className="text-xs text-gray-500">Enable downloading processed results</p>
              </div>
              <input
                type="checkbox"
                checked={settings.security.allowDataExport}
                onChange={(e) => updateSetting('security', 'allowDataExport', e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Require authentication</label>
                <p className="text-xs text-gray-500">Force login for all operations</p>
              </div>
              <input
                type="checkbox"
                checked={settings.security.requireAuthentication}
                onChange={(e) => updateSetting('security', 'requireAuthentication', e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Appearance Settings */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <Palette className="w-5 h-5 text-purple-500 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Appearance</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Theme</label>
              <select
                value={settings.appearance.theme}
                onChange={(e) => updateSetting('appearance', 'theme', e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="auto">Auto (System)</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700">Language</label>
              <select
                value={settings.appearance.language}
                onChange={(e) => updateSetting('appearance', 'language', e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700">Timezone</label>
              <select
                value={settings.appearance.timezone}
                onChange={(e) => updateSetting('appearance', 'timezone', e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time</option>
                <option value="America/Chicago">Central Time</option>
                <option value="America/Denver">Mountain Time</option>
                <option value="America/Los_Angeles">Pacific Time</option>
                <option value="Europe/London">London</option>
                <option value="Europe/Paris">Paris</option>
                <option value="Asia/Tokyo">Tokyo</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Advanced Settings */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center mb-4">
          <SettingsIcon className="w-5 h-5 text-gray-500 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">Advanced Settings</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Button variant="outline" className="flex items-center">
            <Database className="w-4 h-4 mr-2" />
            Database Settings
          </Button>
          <Button variant="outline" className="flex items-center">
            <Globe className="w-4 h-4 mr-2" />
            API Configuration
          </Button>
          <Button variant="outline" className="flex items-center">
            <User className="w-4 h-4 mr-2" />
            User Management
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Settings; 