'use client';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { stockAnalysis } from '../services/api';

interface AnalysisResult {
  symbol: string;
  technical_data?: {
    symbol: string;
    current_price: number;
    current_price_formatted: string;
    currency: string;
    is_indian_stock: boolean;
    last_updated: string;
    rsi: number;
    macd: number;
    macd_signal: number;
    sma_20: number;
    sma_20_formatted: string;
    sma_50: number;
    sma_50_formatted: string;
    volume: number;
    volume_sma_20: number;
    volume_ratio: number;
    price_change_5d: number;
    price_change_1d: number;
    support_levels: number[];
    support_levels_formatted: string[];
    resistance_levels: number[];
    resistance_levels_formatted: string[];
    pivot_points: {
      pivot: number;
      r1: number;
      r2: number;
      s1: number;
      s2: number;
    };
    pivot_points_formatted: {
      pivot: string;
      r1: string;
      r2: string;
      s1: string;
      s2: string;
    };
  };
  ai_analysis?: {
    ai_analysis: string;
  };
  rule_analysis?: {
    summary: string;
    recommendation: string;
    confidence: string;
    key_points: string[];
  };
  error?: string;
}

interface SearchLimitInfo {
  daily_limit: number;
  used_today: number;
  remaining_today: number;
  can_search: boolean;
  last_reset?: string;
}

export default function StockAnalysis() {
  const [symbol, setSymbol] = useState('');
  const [analysisType, setAnalysisType] = useState<'technical' | 'ai' | 'both'>('both');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [searchLimitInfo, setSearchLimitInfo] = useState<SearchLimitInfo | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Fetch search status on component mount
  useEffect(() => {
    fetchSearchStatus();
  }, []);

  const fetchSearchStatus = async () => {
    try {
      const response = await stockAnalysis.getSearchStatus();
      setSearchLimitInfo(response.data);
    } catch (error) {
      console.error('Failed to fetch search status:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!symbol.trim()) {
      setMessage({ type: 'error', text: 'Please enter a stock symbol' });
      return;
    }

    setLoading(true);
    setResult(null);
    setMessage(null);

    try {
      const response = await stockAnalysis.analyze(symbol.toUpperCase(), analysisType);
      
      if (response.data.success && response.data.data) {
        setResult(response.data.data);
        
        // Update search limit info from response
        if (response.data.search_limit_info) {
          setSearchLimitInfo(response.data.search_limit_info);
        }
        
        setMessage({ type: 'success', text: `Analysis completed for ${symbol.toUpperCase()}` });
      } else {
        // Check if it's a search limit error
        if (response.data.search_limit_info && !response.data.search_limit_info.can_search) {
          setSearchLimitInfo(response.data.search_limit_info);
          throw new Error(response.data.error || 'Daily search limit reached');
        } else {
          throw new Error(response.data.error || 'Analysis failed');
        }
      }
    } catch (error: any) {
      console.error('Analysis error:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Analysis failed';
      setMessage({ type: 'error', text: errorMessage });
      setResult({ symbol: symbol.toUpperCase(), error: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Search Limit Info */}
      {searchLimitInfo && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-medium text-blue-900">Daily Search Limit</h4>
              <p className="text-sm text-blue-700">
                {searchLimitInfo.used_today} of {searchLimitInfo.daily_limit} searches used today
              </p>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-blue-900">
                {searchLimitInfo.remaining_today} remaining
              </div>
              {!searchLimitInfo.can_search && (
                <div className="text-sm text-red-600 font-medium">
                  Limit reached
                </div>
              )}
            </div>
          </div>
          
          {/* Progress bar */}
          <div className="mt-2 w-full bg-blue-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(searchLimitInfo.used_today / searchLimitInfo.daily_limit) * 100}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Message Display */}
      {message && (
        <div className={`mb-4 p-3 rounded-md text-sm ${
          message.type === 'success' 
            ? 'bg-green-50 text-green-800 border border-green-200' 
            : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}

      {/* Search Form */}
      <form onSubmit={handleSubmit}>
        <div>
          <div>
            <div>
              <label htmlFor="symbol">
                Stock Symbol
              </label>
              <div>
                <input
                  id="symbol"
                  type="text"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                  placeholder="Enter stock symbol (e.g., AAPL, GOOGL, RELIANCE.NS, TCS)"
                  disabled={loading || (searchLimitInfo && !searchLimitInfo.can_search)}
                />
              </div>
            </div>
            
            <div>
              <label htmlFor="analysisType">
                Analysis Type
              </label>
              <select
                id="analysisType"
                value={analysisType}
                onChange={(e) => setAnalysisType(e.target.value as any)}
                disabled={loading || (searchLimitInfo && !searchLimitInfo.can_search)}
              >
                <option value="both">Technical + AI</option>
                <option value="technical">Technical Only</option>
                <option value="ai">AI Only</option>
              </select>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading || !symbol.trim() || (searchLimitInfo && !searchLimitInfo.can_search)}
            >
              {loading ? (
                <div>
                  <div>Loading...</div>
                  <span>Analyzing...</span>
                </div>
              ) : searchLimitInfo && !searchLimitInfo.can_search ? (
                <div>
                  <span>Daily Limit Reached</span>
                </div>
              ) : (
                <div>
                  <span>Analyze Stock</span>
                </div>
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Results */}
      {result && (
        <div className="mt-8 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-2xl font-bold text-gray-900">
              Analysis Results for {result.symbol}
            </h3>
            <div className="flex items-center space-x-2">
              {result.technical_data && (
                <>
                  <span className={`px-3 py-1 text-sm font-medium rounded-full ${
                    result.technical_data.is_indian_stock 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-blue-100 text-blue-800'
                  }`}>
                    {result.technical_data.currency}
                  </span>
                  <span className="text-xs text-gray-500">
                    Updated: {result.technical_data.last_updated}
                  </span>
                </>
              )}
              {result.error && (
                <span className="px-3 py-1 text-sm font-medium text-red-800 bg-red-100 rounded-full">
                  Analysis Failed
                </span>
              )}
            </div>
          </div>

          {result.error ? (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="text-center">
                <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Analysis Failed</h4>
                <p className="text-gray-600">{result.error}</p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Technical Analysis */}
              {result.technical_data && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                  <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                        <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      </div>
                      <h4 className="text-lg font-semibold text-gray-900">Technical Analysis</h4>
                    </div>
                  </div>
                  <div className="p-6 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700">Current Price:</span>
                        <span className="text-lg font-bold text-gray-900">
                          {result.technical_data.current_price_formatted}
                        </span>
                      </div>
                      
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700">RSI:</span>
                        <span className="text-lg font-semibold text-gray-900">
                          {result.technical_data.rsi.toFixed(2)}
                        </span>
                      </div>
                      
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700">MACD:</span>
                        <span className="text-lg font-semibold text-gray-900">
                          {result.technical_data.macd.toFixed(3)}
                        </span>
                      </div>
                      
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700">20-day SMA:</span>
                        <span className="text-lg font-semibold text-gray-900">
                          {result.technical_data.sma_20_formatted}
                        </span>
                      </div>
                      
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700">50-day SMA:</span>
                        <span className="text-lg font-semibold text-gray-900">
                          {result.technical_data.sma_50_formatted}
                        </span>
                      </div>
                      
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700">1-day Change:</span>
                        <span className={`text-lg font-semibold ${result.technical_data.price_change_1d >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {result.technical_data.price_change_1d >= 0 ? '+' : ''}{result.technical_data.price_change_1d.toFixed(2)}%
                        </span>
                      </div>
                      
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700">5-day Change:</span>
                        <span className={`text-lg font-semibold ${result.technical_data.price_change_5d >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {result.technical_data.price_change_5d >= 0 ? '+' : ''}{result.technical_data.price_change_5d.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700 block mb-2">Support Levels:</span>
                        <p className="text-sm text-gray-600 break-words">
                          {result.technical_data.support_levels_formatted.join(', ')}
                        </p>
                      </div>
                      
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700 block mb-2">Resistance Levels:</span>
                        <p className="text-sm text-gray-600 break-words">
                          {result.technical_data.resistance_levels_formatted.join(', ')}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* AI Analysis */}
              {result.ai_analysis && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                  <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                        <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                      </div>
                      <h4 className="text-lg font-semibold text-gray-900">AI Analysis</h4>
                    </div>
                  </div>
                  <div className="p-6">
                    <div className="space-y-3">
                      <span className="font-medium text-gray-700 block">Analysis:</span>
                      <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                        <div className="max-h-96 overflow-y-auto prose prose-sm max-w-none">
                          <ReactMarkdown
                            components={{
                              h1: ({ children }) => <h1 className="text-xl font-bold text-gray-900 mb-3">{children}</h1>,
                              h2: ({ children }) => <h2 className="text-lg font-bold text-gray-900 mb-2">{children}</h2>,
                              h3: ({ children }) => <h3 className="text-md font-bold text-gray-900 mb-2">{children}</h3>,
                              h4: ({ children }) => <h4 className="text-sm font-bold text-gray-900 mb-2">{children}</h4>,
                              p: ({ children }) => <p className="text-sm text-gray-700 leading-relaxed mb-3">{children}</p>,
                              ul: ({ children }) => <ul className="space-y-2 mb-3 pl-4">{children}</ul>,
                              li: ({ children }) => <li className="text-sm text-gray-700 leading-relaxed">{children}</li>,
                              strong: ({ children }) => <strong className="text-gray-900 font-semibold">{children}</strong>,
                              em: ({ children }) => <em className="text-gray-700 italic">{children}</em>,
                              code: ({ children }) => <code className="text-sm text-gray-900 bg-gray-100 px-1 py-0.5 rounded">{children}</code>,
                              blockquote: ({ children }) => <blockquote className="text-sm text-gray-700 italic border-l-4 border-gray-300 pl-4 my-3">{children}</blockquote>,
                            }}
                          >
                            {result.ai_analysis.ai_analysis}
                          </ReactMarkdown>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Rule-based Analysis */}
              {result.rule_analysis && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                  <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                        <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <h4 className="text-lg font-semibold text-gray-900">Rule-based Analysis</h4>
                    </div>
                  </div>
                  <div className="p-6 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700">Recommendation:</span>
                        <span className={`px-3 py-1 text-sm font-semibold rounded-full ${
                          result.rule_analysis.recommendation === 'BUY' ? 'bg-green-100 text-green-800' :
                          result.rule_analysis.recommendation === 'SELL' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {result.rule_analysis.recommendation}
                        </span>
                      </div>
                      
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700">Confidence:</span>
                        <span className={`px-3 py-1 text-sm font-semibold rounded-full ${
                          result.rule_analysis.confidence === 'HIGH' ? 'bg-blue-100 text-blue-800' :
                          result.rule_analysis.confidence === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {result.rule_analysis.confidence}
                        </span>
                      </div>
                    </div>
                    
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <span className="font-medium text-gray-700 block mb-3">Key Points:</span>
                      <ul className="space-y-2">
                        {result.rule_analysis.key_points.map((point, index) => (
                          <li key={index} className="flex items-start">
                            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                            <span className="text-sm text-gray-700 leading-relaxed">{point}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Quick Tips */}
      {!result && !loading && (
        <div>
          <div>
            <div>
              <h4>Quick Tips</h4>
            </div>
          </div>
          <div>
            <div>
              <div>
                <p>Enter stock symbols in uppercase (e.g., AAPL, GOOGL, RELIANCE.NS, TCS)</p>
              </div>
              <div>
                <p>Add .NS suffix for Indian stocks to ensure Rupee pricing (e.g., RELIANCE.NS)</p>
              </div>
              <div>
                <p>Indian stocks show prices in Rupees (₹), international stocks in Dollars ($)</p>
              </div>
              <div>
                <p>Technical analysis provides RSI, MACD, and support/resistance levels</p>
              </div>
              <div>
                <p>AI analysis offers sentiment analysis and confidence scores</p>
              </div>
              <div>
                <p>Combine both analyses for comprehensive insights</p>
              </div>
              <div>
                <p>You have {searchLimitInfo?.daily_limit || 10} searches per day</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 