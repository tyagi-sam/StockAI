import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth } from '../../services/api';
import Button from '../common/Button';
import Input from '../common/Input';
import Alert from '../common/Alert';
import Card, { CardHeader, CardBody } from '../common/Card';
import type { Message } from '../../types';

interface EmailVerificationProps {
  email: string;
  name?: string;
  onVerificationSuccess: () => void;
  onCancel: () => void;
}

export default function EmailVerification({ email, name, onVerificationSuccess, onCancel }: EmailVerificationProps) {
  const navigate = useNavigate();
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [resendDisabled, setResendDisabled] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [message, setMessage] = useState<Message | null>(null);
  const [verificationSuccess, setVerificationSuccess] = useState(false);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!otp.trim()) {
      setMessage({ type: 'error', text: 'Please enter the verification code' });
      return;
    }

    setLoading(true);
    
    try {
      const response = await auth.verifyEmail(email, otp);
      
      // Store the token for automatic login
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      
      setVerificationSuccess(true);
      setMessage({ type: 'success', text: 'Verification successful! Redirecting to your dashboard...' });
      
      // Set flag for welcome banner
      sessionStorage.setItem('justVerified', 'true');
      
      // Redirect to dashboard after a short delay
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
      
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to verify email';
      setMessage({ type: 'error', text: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    setResendLoading(true);
    setMessage(null);
    
    try {
      const response = await auth.resendOtp(email);
      setMessage({ type: 'success', text: response.data.message || 'New verification code sent!' });
      
      // Start countdown
      setResendDisabled(true);
      setCountdown(60);
      
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            setResendDisabled(false);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to resend verification code';
      setMessage({ type: 'error', text: errorMessage });
    } finally {
      setResendLoading(false);
    }
  };

  if (verificationSuccess) {
    return (
      <div id="verification-success-container" className="min-h-screen flex items-center justify-center bg-gradient-to-br from-success-50 to-green-50 py-12 px-4 sm:px-6 lg:px-8">
        <div id="verification-success-card" className="max-w-md w-full">
          <Card className="animate-fade-in">
            <CardHeader className="text-center">
              <div id="success-icon" className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 id="success-title" className="text-xl font-bold text-gray-900">Email Verified!</h2>
              <p id="success-message" className="text-gray-600 mt-2">
                Welcome to StockAI! Redirecting you to your dashboard...
              </p>
            </CardHeader>
            
            <CardBody className="text-center">
              <div id="loading-indicator" className="flex items-center justify-center mb-4">
                <div className="spinner mr-2" style={{ width: '1rem', height: '1rem' }}></div>
                <span className="text-sm text-gray-600">Setting up your account...</span>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div id="email-verification-container" className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-blue-50 py-12 px-4 sm:px-6 lg:px-8">
      <div id="email-verification-card" className="max-w-md w-full">
        <Card className="animate-fade-in">
          <CardHeader className="text-center">
            <div id="verification-icon" className="mx-auto h-12 w-12 bg-primary-600 rounded-lg flex items-center justify-center">
              <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h2 id="verification-title" className="mt-6 text-2xl font-bold text-gray-900">
              Verify Your Email
            </h2>
            <p id="verification-subtitle" className="mt-2 text-sm text-gray-600">
              We've sent a verification code to <strong>{email}</strong>
            </p>
          </CardHeader>
          
          <CardBody>
            {message && (
              <Alert 
                id="verification-message"
                message={message} 
                onClose={() => setMessage(null)}
                className="mb-6"
              />
            )}
            
            <form id="verification-form" onSubmit={handleVerify} className="space-y-4">
              <div id="otp-field">
                <label htmlFor="otp-input" className="block text-sm font-medium text-gray-700 mb-2">
                  Verification Code
                </label>
                <Input
                  id="otp-input"
                  type="text"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  placeholder="Enter 6-digit code"
                  maxLength={6}
                  autoComplete="one-time-code"
                  className="text-center text-lg tracking-widest"
                />
              </div>

              <Button
                id="verify-button"
                type="submit"
                loading={loading}
                disabled={loading || !otp.trim()}
                className="w-full"
              >
                Verify Email
              </Button>
            </form>

            <div id="resend-section" className="mt-6 text-center">
              <p id="resend-text" className="text-sm text-gray-600 mb-3">
                Didn't receive the code?
              </p>
              
              <Button
                id="resend-button"
                variant="ghost"
                onClick={handleResendOtp}
                disabled={resendLoading || resendDisabled}
                className="text-sm"
              >
                {resendLoading ? (
                  <>
                    <div className="spinner mr-2" style={{ width: '0.875rem', height: '0.875rem' }}></div>
                    Sending...
                  </>
                ) : resendDisabled ? (
                  `Resend in ${countdown}s`
                ) : (
                  'Resend Code'
                )}
              </Button>
            </div>

            <div id="cancel-section" className="mt-6 pt-4 border-t border-gray-200">
              <Button
                id="cancel-button"
                variant="secondary"
                onClick={onCancel}
                className="w-full text-sm"
              >
                Back to Login
              </Button>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
} 