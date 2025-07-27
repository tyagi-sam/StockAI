import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth } from '../../services/api';
import Button from '../common/Button';
import Input from '../common/Input';
import Alert from '../common/Alert';
import Card, { CardHeader, CardBody } from '../common/Card';
import EmailVerification from './EmailVerification';
import type { Message } from '../../types';

export default function LoginForm() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showEmailVerification, setShowEmailVerification] = useState(false);
  const [registeredEmail, setRegisteredEmail] = useState('');
  const [message, setMessage] = useState<Message | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      if (isLogin) {
        const response = await auth.login(email, password);
        const { access_token, user } = response.data;
        
        localStorage.setItem('token', access_token);
        localStorage.setItem('user', JSON.stringify(user));
        
        setMessage({ type: 'success', text: 'Login successful! Redirecting to dashboard...' });
        
        setTimeout(() => {
          navigate('/dashboard');
        }, 1500);
      } else {
        await auth.register(email, password, name);
        
        setRegisteredEmail(email);
        setShowEmailVerification(true);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'An error occurred';
      setMessage({ type: 'error', text: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      setMessage(null);
      const response = await auth.getGoogleLoginUrl();
      window.location.href = response.data.login_url;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to initiate Google login';
      setMessage({ type: 'error', text: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  const handleVerificationCancel = () => {
    setShowEmailVerification(false);
    setIsLogin(true);
  };

  if (showEmailVerification) {
    return (
      <EmailVerification
        email={registeredEmail}
        onCancel={handleVerificationCancel}
      />
    );
  }

  return (
    <div id="login-container" className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-blue-50 py-12 px-4 sm:px-6 lg:px-8">
      <div id="login-card" className="max-w-md w-full space-y-8">
        <Card className="animate-fade-in">
          <CardHeader className="text-center">
            <div id="login-logo" className="mx-auto h-12 w-12 bg-primary-600 rounded-lg flex items-center justify-center">
              <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h2 id="login-title" className="mt-6 text-3xl font-bold text-gray-900">
              {isLogin ? 'Sign in to StockAI' : 'Create your account'}
            </h2>
            <p id="login-subtitle" className="mt-2 text-sm text-gray-600">
              {isLogin ? 'Welcome back! Please sign in to your account.' : 'Start your stock analysis journey today.'}
            </p>
          </CardHeader>

          <CardBody>
            {message && (
              <Alert 
                id="login-message"
                message={message} 
                onClose={() => setMessage(null)}
                className="mb-6"
              />
            )}

            <form id="login-form" onSubmit={handleSubmit} className="space-y-6">
              {!isLogin && (
                <div id="name-field">
                  <label htmlFor="name-input" className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name
                  </label>
                  <Input
                    id="name-input"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter your full name"
                    required={!isLogin}
                    autoComplete="name"
                  />
                </div>
              )}

              <div id="email-field">
                <label htmlFor="email-input" className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <Input
                  id="email-input"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  required
                  autoComplete="email"
                />
              </div>

              <div id="password-field">
                <label htmlFor="password-input" className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <Input
                    id="password-input"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    required
                    autoComplete={isLogin ? 'current-password' : 'new-password'}
                  />
                  <button
                    id="password-toggle"
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? (
                      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                      </svg>
                    ) : (
                      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              <Button
                id="submit-button"
                type="submit"
                loading={loading}
                disabled={loading || !email.trim() || !password.trim() || (!isLogin && !name.trim())}
                className="w-full"
              >
                {isLogin ? 'Sign In' : 'Create Account'}
              </Button>
            </form>

            <div id="divider" className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Or continue with</span>
              </div>
            </div>

            <Button
              id="google-login-button"
              variant="secondary"
              onClick={handleGoogleLogin}
              disabled={loading}
              className="w-full"
            >
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Continue with Google
            </Button>

            <div id="toggle-mode" className="text-center mt-6">
              <p className="text-sm text-gray-600">
                {isLogin ? "Don't have an account?" : "Already have an account?"}
                <button
                  id="toggle-button"
                  type="button"
                  onClick={() => {
                    setIsLogin(!isLogin);
                    setMessage(null);
                  }}
                  className="ml-1 font-medium text-primary-600 hover:text-primary-500"
                >
                  {isLogin ? 'Sign up' : 'Sign in'}
                </button>
              </p>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
} 