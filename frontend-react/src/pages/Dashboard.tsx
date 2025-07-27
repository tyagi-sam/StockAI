import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import StockAnalysis from '../components/dashboard/StockAnalysis';
import Button from '../components/common/Button';
import Alert from '../components/common/Alert';
import type { User, Message } from '../types';

export default function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [showWelcomeBanner, setShowWelcomeBanner] = useState(false);
  const [message, setMessage] = useState<Message | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (!token) {
      navigate('/login');
      return;
    }

    if (userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        
        // Show welcome banner if user just verified email
        const justVerified = sessionStorage.getItem('justVerified');
        if (justVerified === 'true') {
          setShowWelcomeBanner(true);
          sessionStorage.removeItem('justVerified');
          
          // Auto-hide banner after 5 seconds
          setTimeout(() => {
            setShowWelcomeBanner(false);
          }, 5000);
        }
      } catch (error) {
        console.error('Failed to parse user data:', error);
        localStorage.removeItem('user');
        navigate('/login');
      }
    }

    setLoading(false);
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (loading) {
    return (
      <div id="dashboard-loading" className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="spinner mx-auto mb-4" style={{ width: '2rem', height: '2rem' }}></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div id="dashboard-container" className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <nav id="dashboard-nav" className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Brand */}
            <div id="nav-brand" className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
                  <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>
              <div className="ml-3">
                <h1 id="nav-title" className="text-xl font-bold text-gray-900">StockAI</h1>
                <p id="nav-subtitle" className="text-sm text-gray-500">AI-Powered Stock Analysis</p>
              </div>
            </div>

            {/* User Menu */}
            <div id="nav-user-menu" className="flex items-center space-x-4">
              <div id="user-info" className="hidden md:flex items-center space-x-3">
                <div className="text-right">
                  <p id="user-name" className="text-sm font-medium text-gray-900">
                    {user?.name || 'User'}
                  </p>
                  <p id="user-email" className="text-xs text-gray-500">
                    {user?.email}
                  </p>
                </div>
                <div id="user-avatar" className="h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-primary-600">
                    {(user?.name || 'U').charAt(0).toUpperCase()}
                  </span>
                </div>
              </div>

              <div id="nav-actions" className="flex items-center space-x-2">
                <Button
                  id="logout-button"
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                >
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Welcome Banner */}
      {showWelcomeBanner && (
        <div id="welcome-banner" className="bg-success-50 border-b border-success-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-success-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-sm font-medium text-success-800">
                  Welcome to StockAI, {user?.name}! 🎉 Your account is ready for analysis.
                </p>
              </div>
              <button
                id="close-welcome-banner"
                onClick={() => setShowWelcomeBanner(false)}
                className="text-success-600 hover:text-success-800"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main id="dashboard-main" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div id="page-header" className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 id="page-title" className="text-3xl font-bold text-gray-900">
                Dashboard
              </h1>
              <p id="page-subtitle" className="mt-2 text-gray-600">
                Analyze stocks with AI-powered insights and technical indicators
              </p>
            </div>
            
            <div id="quick-stats" className="hidden lg:flex items-center space-x-6">
              <div id="stats-item-1" className="text-center">
                <p className="text-2xl font-bold text-primary-600">10</p>
                <p className="text-xs text-gray-500">Daily Searches</p>
              </div>
              <div id="stats-item-2" className="text-center">
                <p className="text-2xl font-bold text-success-600">∞</p>
                <p className="text-xs text-gray-500">AI Analysis</p>
              </div>
              <div id="stats-item-3" className="text-center">
                <p className="text-2xl font-bold text-warning-600">24/7</p>
                <p className="text-xs text-gray-500">Available</p>
              </div>
            </div>
          </div>
        </div>

        {/* Stock Analysis Component */}
        <StockAnalysis />
      </main>

      {/* Footer */}
      <footer id="dashboard-footer" className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p id="footer-text" className="text-sm text-gray-500">
              © 2025 StockAI. Powered by AI and technical analysis.
            </p>
            
            {/* Message Display in Footer */}
            {message && (
              <div className="mt-4 mb-4">
                <Alert 
                  id="footer-message"
                  message={message} 
                  onClose={() => setMessage(null)}
                />
              </div>
            )}
            
            <div id="footer-links" className="mt-4 flex justify-center space-x-8">
              <button
                id="privacy-button"
                onClick={() => setMessage({ 
                  type: 'info', 
                  text: 'Privacy: We do not store your passwords or OTPs in plain text. All sensitive data is securely hashed. We do not collect any personal information from your Google account beyond what is necessary for authentication.' 
                })}
                className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
              >
                Privacy
              </button>
              <button
                id="terms-button"
                onClick={() => setMessage({ 
                  type: 'info', 
                  text: 'Terms: By using StockAI, you agree to use this service responsibly. We provide stock analysis for educational purposes only and do not guarantee investment outcomes.' 
                })}
                className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
              >
                Terms
              </button>
              <button
                id="support-button"
                onClick={() => setMessage({ 
                  type: 'info', 
                  text: 'Support: For any queries or issues, please email us at support@stockai.com. We typically respond within 24 hours.' 
                })}
                className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
              >
                Support
              </button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
} 