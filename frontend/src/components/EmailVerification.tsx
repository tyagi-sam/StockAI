'use client';

import { useState } from 'react';
import { auth } from '../services/api';
import toast from 'react-hot-toast';

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

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!otp.trim()) {
      toast.error('Please enter the verification code');
      return;
    }

    setLoading(true);
    try {
      const response = await auth.verifyEmail(email, otp);
      toast.success(response.data.message || 'Email verified successfully!');
      onVerificationSuccess();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to verify email';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    setResendLoading(true);
    try {
      const response = await auth.resendOtp(email);
      toast.success(response.data.message || 'New verification code sent!');
      
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
      const message = error.response?.data?.detail || 'Failed to resend verification code';
      toast.error(message);
    } finally {
      setResendLoading(false);
    }
  };

  return (
    <div className="card max-w-md mx-auto">
      <div className="card-header text-center">
        <h2 className="text-xl font-bold text-gray-900">Verify Your Email</h2>
        <p className="text-gray-600 mt-1 text-sm">
          We've sent a verification code to <strong>{email}</strong>
        </p>
      </div>
      
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