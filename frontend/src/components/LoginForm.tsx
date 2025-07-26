'use client';

import { useState } from 'react';
import { auth } from '../services/api';
import toast from 'react-hot-toast';
import EmailVerification from './EmailVerification';

export default function LoginForm() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showEmailVerification, setShowEmailVerification] = useState(false);
  const [registeredEmail, setRegisteredEmail] = useState('');
  const [registeredName, setRegisteredName] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        const response = await auth.login(email, password);
        const { access_token, user } = response.data;
        
        localStorage.setItem('token', access_token);
        toast.success('Login successful!');
        
        // Redirect to dashboard
        window.location.href = '/dashboard';
      } else {
        const response = await auth.register(email, password, name);
        toast.success(response.data.message || 'Registration successful!');
        
        // Show email verification
        setRegisteredEmail(email);
        setRegisteredName(name);
        setShowEmailVerification(true);
      }
    } catch (error: any) {
      const message = error.response?.data?.detail || 'An error occurred';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      const response = await auth.getGoogleLoginUrl();
      window.location.href = response.data.login_url;
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to initiate Google login';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerificationSuccess = () => {
    setShowEmailVerification(false);
    setIsLogin(true);
    setEmail(registeredEmail);
    toast.success('Email verified! You can now log in.');
  };

  const handleVerificationCancel = () => {
    setShowEmailVerification(false);
    setIsLogin(true);
  };

  // Show email verification component
  if (showEmailVerification) {
    return (
      <EmailVerification
        email={registeredEmail}
        name={registeredName}
        onVerificationSuccess={handleVerificationSuccess}
        onCancel={handleVerificationCancel}
      />
    );
  }

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="space-y-3">
        {!isLogin && (
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              Full Name
            </label>
            <div className="relative">
              <input
                id="name"
                type="text"
                required={!isLogin}
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="input"
                placeholder="Enter your full name"
              />
            </div>
          </div>
        )}

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            Email Address
          </label>
          <div className="relative">
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input"
              placeholder="Enter your email"
            />
          </div>
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
            Password
          </label>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input pr-10"
              placeholder={isLogin ? "Enter your password" : "Create a password"}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-2 top-3 text-gray-400 hover:text-gray-600 transition-colors text-sm"
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn btn-primary w-full"
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <div className="spinner mr-2"></div>
              {isLogin ? "Signing in..." : "Creating account..."}
            </div>
          ) : (
            isLogin ? "Sign In" : "Create Account"
          )}
        </button>
      </form>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-300" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-white text-gray-500">Or continue with</span>
        </div>
      </div>

      <button
        onClick={handleGoogleLogin}
        disabled={loading}
        className="w-full flex items-center justify-center px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
      >
        Continue with Google
      </button>

      <div className="text-center">
        <button
          type="button"
          onClick={() => {
            setIsLogin(!isLogin);
            setEmail('');
            setPassword('');
            setName('');
          }}
          className="text-sm text-blue-600 hover:text-blue-500 font-medium"
        >
          {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
        </button>
      </div>
    </div>
  );
}
