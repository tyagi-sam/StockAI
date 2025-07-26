'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { auth } from '../services/api';
import { AuthResponse } from '../types';
import toast from 'react-hot-toast';

export default function LoginForm() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = isLogin
        ? await auth.login(email, password)
        : await auth.register(email, password, name);

      const data: AuthResponse = response.data;
      if (isLogin) {
        localStorage.setItem('token', data.access_token);
        toast.success('Logged in successfully!');
        router.push('/dashboard');
      } else {
        toast.success('Account created! Please sign in.');
        setIsLogin(true);
        setEmail('');
        setPassword('');
        setName('');
      }
    } catch (error: any) {
      console.error(error);
      const msg = error.response?.data?.detail || 'Authentication failed';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setLoading(true);
    try {
      const res = await auth.getGoogleLoginUrl();
      if (res.data.login_url) window.location.href = res.data.login_url;
      else toast.error('Unable to connect Google');
    } catch (err: any) {
      console.error(err);
      toast.error('Google login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-primary-50 px-4">
      <div className="card w-full max-w-sm animate-fade-in">
        <div className="card-header text-center">
          <h2 className="text-2xl font-semibold text-gray-900">
            Stock<span className="text-primary-600">AI</span> Search
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            {isLogin ? 'Sign in to continue' : 'Create your account'}
          </p>
        </div>
        <div className="card-body space-y-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div className="flex flex-col">
                <label htmlFor="name" className="text-sm font-medium text-gray-700">
                  Full Name
                </label>
                <input
                  id="name"
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="input mt-1"
                  placeholder="Your full name"
                />
              </div>
            )}

            <div className="flex flex-col">
              <label htmlFor="email" className="text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input mt-1"
                placeholder="you@example.com"
              />
            </div>

            <div className="flex flex-col">
              <label htmlFor="password" className="text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="relative mt-1">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input"
                  placeholder={isLogin ? 'Enter password' : 'New password'}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-3 flex items-center text-sm text-gray-500"
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full"
            >
              {loading ? (isLogin ? 'Signing in...' : 'Creating...') : isLogin ? 'Sign In' : 'Sign Up'}
            </button>
          </form>

          <div className="flex items-center">
            <div className="flex-grow border-t border-gray-200"></div>
            <span className="px-3 text-sm text-gray-400">or</span>
            <div className="flex-grow border-t border-gray-200"></div>
          </div>

          <button
            onClick={handleGoogleLogin}
            disabled={loading}
            className="btn btn-secondary w-full flex items-center justify-center"
          >
            <img src="/google-icon.svg" alt="Google" className="w-5 h-5 mr-2" />
            {loading ? 'Connecting...' : 'Continue with Google'}
          </button>

          <p className="text-center text-sm text-gray-600">
            {isLogin ? (
              <>New here?{' '}
                <button onClick={() => setIsLogin(false)} className="text-primary-600 hover:underline">
                  Create account
                </button>
              </>
            ) : (
              <>Already have one?{' '}
                <button onClick={() => setIsLogin(true)} className="text-primary-600 hover:underline">
                  Sign in
                </button>
              </>
            )}
          </p>
          {isLogin && (
            <p className="text-center text-sm">
              <a href="#" className="text-gray-600 hover:text-gray-800">
                Forgot password?
              </a>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
