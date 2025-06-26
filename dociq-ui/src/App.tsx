import React, { useState } from 'react';
import Layout from './components/layout/Layout';
import Dashboard from './components/pages/Dashboard';
import Upload from './components/pages/Upload';
import Results from './components/pages/Results';
import Settings from './components/pages/Settings';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'upload':
        return <Upload />;
      case 'results':
        return <Results />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <Layout activeTab={activeTab} onTabChange={setActiveTab}>
      {renderContent()}
    </Layout>
  );
}

export default App;
