import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { auth } from '../services/api';
import Button from '../components/common/Button';
import Alert from '../components/common/Alert';
import type { Message } from '../types';

export default function AuthCallback() {
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<Message | null>(null);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    handleCallback();
  }, []);

  const handleCallback = async () => {
    try {
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const error = searchParams.get('error');

      if (error) {
        setMessage({ type: 'error', text: 'Authentication was cancelled or failed' });
        setLoading(false);
        return;
      }

      if (!code) {
        setMessage({ type: 'error', text: 'No authorization code found' });
        setLoading(false);
        return;
      }

      // Call the backend to exchange the code for tokens
      const response = await auth.handleGoogleCallback(code, state || '');
      
      if (response.data.access_token) {
        // Store the token
        localStorage.setItem('token', response.data.access_token);
        
        // Store user info if available
        if (response.data.user) {
          localStorage.setItem('user', JSON.stringify(response.data.user));
        }
        
        setMessage({ type: 'success', text: 'Login successful! Redirecting to dashboard...' });
        
        // Redirect to dashboard after a short delay
        setTimeout(() => {
          navigate('/dashboard');
        }, 2000);
      } else {
        setMessage({ type: 'error', text: 'Failed to authenticate' });
        setLoading(false);
      }
    } catch (error: any) {
      console.error('Callback error:', error);
      const errorMessage = error.response?.data?.detail || 'Authentication failed';
      setMessage({ type: 'error', text: errorMessage });
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div id="auth-callback-loading" className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-blue-50">
        <div id="loading-container" className="text-center">
          <div id="loading-spinner" className="spinner mx-auto mb-4" style={{ width: '3rem', height: '3rem' }}></div>
          <p id="loading-text" className="text-gray-600">Processing authentication...</p>
        </div>
      </div>
    );
  }

  if (message?.type === 'error') {
    return (
      <div id="auth-callback-error" className="min-h-screen flex items-center justify-center bg-gradient-to-br from-error-50 to-red-50">
        <div id="error-container" className="max-w-md w-full mx-auto px-4">
          <div id="error-card" className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div id="error-icon" className="text-error-600 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h2 id="error-title" className="text-2xl font-bold text-gray-900 mb-2">Authentication Failed</h2>
            <Alert 
              id="error-message"
              message={message} 
              className="mb-6"
            />
            <Button
              id="back-to-login-button"
              onClick={() => navigate('/login')}
              className="w-full"
            >
              Back to Login
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (message?.type === 'success') {
    return (
      <div id="auth-callback-success" className="min-h-screen flex items-center justify-center bg-gradient-to-br from-success-50 to-green-50">
        <div id="success-container" className="max-w-md w-full mx-auto px-4">
          <div id="success-card" className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div id="success-icon" className="text-success-600 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 id="success-title" className="text-2xl font-bold text-gray-900 mb-2">Authentication Successful</h2>
            <Alert 
              id="success-message"
              message={message} 
              className="mb-6"
            />
            <div id="redirect-indicator" className="flex items-center justify-center">
              <div className="spinner mr-2" style={{ width: '1rem', height: '1rem' }}></div>
              <span className="text-sm text-gray-600">Redirecting to dashboard...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
} 