'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Toaster } from 'react-hot-toast';
import LoginForm from '../components/LoginForm';
import { User } from '../types';

export default function HomePage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token and get user info
      fetchUserInfo();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserInfo = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${API_URL}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        // Redirect to dashboard
        router.push('/dashboard');
      } else {
        // Token is invalid, remove it
        localStorage.removeItem('token');
        setLoading(false);
      }
    } catch (error) {
      console.error('Error fetching user info:', error);
      localStorage.removeItem('token');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="relative z-10">
        <nav className="container py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-5 h-5 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-sm flex items-center justify-center shadow-lg">
              </div>
              <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                StockAI
              </span>
            </div>
            <div className="hidden md:flex items-center space-x-6 text-gray-600">
              <a href="#features" className="hover:text-blue-600 transition-colors font-medium text-sm">Features</a>
              <a href="#about" className="hover:text-blue-600 transition-colors font-medium text-sm">About</a>
              <a href="#contact" className="hover:text-blue-600 transition-colors font-medium text-sm">Contact</a>
            </div>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <main className="relative">
        <div className="container py-8 lg:py-16">
          <div className="grid lg:grid-cols-2 gap-8 items-center">
            {/* Left Column - Content */}
            <div className="animate-fade-in">
              <h1 className="text-3xl lg:text-5xl font-bold text-gray-900 mb-4 leading-tight">
                AI-Powered
                <span className="block bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Stock Analysis
                </span>
              </h1>
              <p className="text-lg text-gray-600 mb-6 leading-relaxed">
                Get intelligent insights, technical analysis, and trading recommendations powered by advanced AI. 
                Make informed investment decisions with real-time data and predictive analytics.
              </p>
              
              {/* Features Grid */}
              <div className="grid grid-cols-2 gap-3 mb-6">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-100 rounded-sm flex items-center justify-center">
                  </div>
                  <span className="text-xs font-medium text-gray-700">Secure & Reliable</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-blue-100 rounded-sm flex items-center justify-center">
                  </div>
                  <span className="text-xs font-medium text-gray-700">Real-time Data</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-yellow-100 rounded-sm flex items-center justify-center">
                  </div>
                  <span className="text-xs font-medium text-gray-700">Technical Analysis</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-purple-100 rounded-sm flex items-center justify-center">
                  </div>
                  <span className="text-xs font-medium text-gray-700">AI Insights</span>
                </div>
              </div>

              {/* Stats */}
              <div className="flex items-center space-x-6 text-xs text-gray-500">
                <div className="flex items-center space-x-1">
                  <span>Global Markets</span>
                </div>
                <div className="flex items-center space-x-1">
                  <span>Real-time Analysis</span>
                </div>
              </div>
            </div>

            {/* Right Column - Login Form */}
            <div className="animate-slide-in">
              <div className="card max-w-sm mx-auto">
                <div className="card-header text-center">
                  <h2 className="text-xl font-bold text-gray-900">Welcome Back</h2>
                  <p className="text-gray-600 mt-1 text-sm">Sign in to access your dashboard</p>
                </div>
                <div className="card-body">
                  <LoginForm />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Background Elements */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-24 h-24 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" style={{animationDuration: '4s'}}></div>
          <div className="absolute top-40 right-10 w-24 h-24 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" style={{animationDuration: '4s', animationDelay: '1s'}}></div>
          <div className="absolute -bottom-8 left-20 w-24 h-24 bg-pink-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" style={{animationDuration: '4s', animationDelay: '2s'}}></div>
        </div>
      </main>

      {/* Features Section */}
      <section id="features" className="py-16 bg-white">
        <div className="container">
          <div className="text-center mb-12">
            <h2 className="text-2xl lg:text-3xl font-bold text-gray-900 mb-3">
              Powerful Features for Smart Investing
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our AI-powered platform provides everything you need to make informed investment decisions
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="card p-6 text-center hover:shadow-xl transition-shadow">
              <div className="w-6 h-6 bg-blue-100 rounded-md flex items-center justify-center mx-auto mb-4">
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Technical Analysis</h3>
              <p className="text-gray-600 text-sm">
                Advanced technical indicators and chart patterns to identify market trends and entry/exit points.
              </p>
            </div>

            <div className="card p-6 text-center hover:shadow-xl transition-shadow">
              <div className="w-6 h-6 bg-green-100 rounded-md flex items-center justify-center mx-auto mb-4">
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">AI Insights</h3>
              <p className="text-gray-600 text-sm">
                Machine learning algorithms analyze market data to provide intelligent trading recommendations.
              </p>
            </div>

            <div className="card p-6 text-center hover:shadow-xl transition-shadow">
              <div className="w-6 h-6 bg-yellow-100 rounded-md flex items-center justify-center mx-auto mb-4">
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Risk Management</h3>
              <p className="text-gray-600 text-sm">
                Comprehensive risk assessment and portfolio analysis to protect your investments.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="container">
          <div className="grid md:grid-cols-4 gap-6">
            <div>
              <div className="flex items-center space-x-2 mb-3">
                <div className="w-4 h-4 bg-blue-600 rounded-sm flex items-center justify-center">
                </div>
                <span className="text-lg font-bold">StockAI</span>
              </div>
              <p className="text-gray-400 text-sm">
                AI-powered stock analysis platform for intelligent investing.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-3 text-sm">Product</h4>
              <ul className="space-y-1 text-gray-400 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-3 text-sm">Company</h4>
              <ul className="space-y-1 text-gray-400 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-3 text-sm">Support</h4>
              <ul className="space-y-1 text-gray-400 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Privacy</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-6 pt-6 text-center text-gray-400 text-sm">
            <p>&copy; 2024 StockAI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
} 