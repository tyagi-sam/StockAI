'use client';

import { useState } from 'react';
import { auth } from '../services/api';

interface EmailVerificationProps {
  email: string;
  name?: string;
  onVerificationSuccess: () => void;
  onCancel: () => void;
}

export default function EmailVerification({ email, name, onVerificationSuccess, onCancel }: EmailVerificationProps) {
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [resendDisabled, setResendDisabled] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [verificationSuccess, setVerificationSuccess] = useState(false);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!otp.trim()) {
      setMessage({ type: 'error', text: 'Please enter the verification code' });
      return;
    }

    setLoading(true);
    // Don't clear message here - let the error handling set it
    
    try {
      const response = await auth.verifyEmail(email, otp);
      
      // Store the token for automatic login
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      
      setVerificationSuccess(true);
      setMessage({ type: 'success', text: 'Verification successful! Redirecting to your dashboard...' });
      
      // Redirect to dashboard after a short delay
      setTimeout(() => {
        window.location.href = '/dashboard';
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
      <div className="card max-w-md mx-auto">
        <div className="card-header text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900">Email Verified!</h2>
          <p className="text-gray-600 mt-2">
            Welcome to StockAI! Redirecting you to your dashboard...
          </p>
        </div>
        
        <div className="card-body text-center">
          <div className="flex items-center justify-center mb-4">
            <div className="spinner mr-2"></div>
            <span className="text-sm text-gray-600">Setting up your account...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card max-w-md mx-auto">
      <div className="card-header text-center">
        <h2 className="text-xl font-bold text-gray-900">Verify Your Email</h2>
        <p className="text-gray-600 mt-1 text-sm">
          We've sent a verification code to <strong>{email}</strong>
        </p>
      </div>
      
      {message && (
        <div className={`mx-4 mb-4 p-4 rounded-md text-sm border-2 ${
          message.type === 'success' 
            ? 'bg-green-50 text-green-800 border-green-300' 
            : 'bg-red-50 text-red-800 border-red-300'
        }`}>
          <div className="flex items-center">
            {message.type === 'error' && (
              <svg className="w-4 h-4 mr-2 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            )}
            {message.type === 'success' && (
              <svg className="w-4 h-4 mr-2 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            )}
            <span className="font-medium">{message.text}</span>
          </div>
        </div>
      )}
      
      <div className="card-body">
        <form onSubmit={handleVerify} className="space-y-4">
          <div>
            <label htmlFor="otp" className="block text-sm font-medium text-gray-700 mb-1">
              Verification Code
            </label>
            <input
              id="otp"
              type="text"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              className="input text-center text-lg tracking-widest"
              placeholder="Enter 6-digit code"
              maxLength={6}
              autoComplete="one-time-code"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !otp.trim()}
            className="btn btn-primary w-full"
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <div className="spinner mr-2"></div>
                Verifying...
              </div>
            ) : (
              'Verify Email'
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600 mb-3">
            Didn't receive the code?
          </p>
          
          <button
            onClick={handleResendOtp}
            disabled={resendLoading || resendDisabled}
            className="btn btn-ghost text-sm"
          >
            {resendLoading ? (
              <div className="flex items-center justify-center">
                <div className="spinner mr-2"></div>
                Sending...
              </div>
            ) : resendDisabled ? (
              `Resend in ${countdown}s`
            ) : (
              'Resend Code'
            )}
          </button>
        </div>

        <div className="mt-6 pt-4 border-t border-gray-200">
          <button
            onClick={onCancel}
            className="btn btn-secondary w-full text-sm"
          >
            Back to Login
          </button>
        </div>
      </div>
    </div>
  );
} 