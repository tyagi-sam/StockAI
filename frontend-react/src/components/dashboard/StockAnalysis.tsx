import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { useNavigate } from 'react-router-dom';
import { stockAnalysis } from '../../services/api';
import Button from '../common/Button';
import InputWithIcon from '../common/InputWithIcon';
import Alert from '../common/Alert';
import Card, { CardHeader, CardBody } from '../common/Card';
import type { AnalysisResult, SearchLimitInfo, Message } from '../../types';

// Tooltip component with better positioning
const Tooltip = ({ children, content }: { children: React.ReactNode; content: string }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const handleMouseEnter = (e: React.MouseEvent) => {
    setMousePosition({ x: e.clientX, y: e.clientY });
    setIsVisible(true);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    setMousePosition({ x: e.clientX, y: e.clientY });
  };

  const handleMouseLeave = () => {
    setIsVisible(false);
  };

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={handleMouseEnter}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        className="cursor-help"
      >
        {children}
      </div>
      {isVisible && (
        <div 
          className="fixed z-[9999] w-64 p-3 text-sm text-white bg-gray-900 rounded-lg shadow-lg pointer-events-none"
          style={{
            left: mousePosition.x + 10,
            top: mousePosition.y - 10,
            transform: 'translateY(-100%)'
          }}
        >
          {content}
          <div className="absolute top-full left-4 w-2 h-2 bg-gray-900 transform rotate-45"></div>
        </div>
      )}
    </div>
  );
};

// Disclaimer Modal component
const DisclaimerModal = ({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Important Disclaimer</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div className="space-y-4 text-sm text-gray-700">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-amber-800 mb-2">Financial Disclaimer</h3>
                <p className="mb-3">
                  This analysis is for informational purposes only and should not be considered as financial advice. 
                  Stock market investments carry inherent risks, and past performance does not guarantee future results.
                </p>
                <p className="mb-3">
                  Always consult with a qualified financial advisor, broker, or investment professional before making 
                  any investment decisions. The technical indicators and AI analysis provided are tools to assist in 
                  your research, but they should be used as part of a comprehensive investment strategy.
                </p>
                <p className="mb-3">
                  <strong>Key Points:</strong>
                </p>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>This is not investment advice</li>
                  <li>Past performance doesn't guarantee future results</li>
                  <li>Always consult a financial advisor</li>
                  <li>Consider your risk tolerance and investment goals</li>
                  <li>Diversify your portfolio</li>
                  <li>Never invest more than you can afford to lose</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div className="mt-6 flex justify-end">
            <Button
              onClick={onClose}
              className="bg-primary-600 hover:bg-primary-700 text-white"
            >
              I Understand
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function StockAnalysis() {
  const navigate = useNavigate();
  const [symbol, setSymbol] = useState('');
  const [analysisType, setAnalysisType] = useState<'technical' | 'ai' | 'both'>('both');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [searchLimitInfo, setSearchLimitInfo] = useState<SearchLimitInfo | null>(null);
  const [message, setMessage] = useState<Message | null>(null);
  const [showDisclaimer, setShowDisclaimer] = useState(false);

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

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation.toUpperCase()) {
      case 'BUY':
        return 'text-success-600 bg-success-50 border-success-200';
      case 'SELL':
        return 'text-error-600 bg-error-50 border-error-200';
      case 'HOLD':
        return 'text-warning-600 bg-warning-50 border-warning-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence.toUpperCase()) {
      case 'HIGH':
        return 'text-success-600';
      case 'MEDIUM':
        return 'text-warning-600';
      case 'LOW':
        return 'text-error-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div id="stock-analysis-container" className="max-w-6xl mx-auto px-4 py-8">
      {/* Disclaimer Modal */}
      <DisclaimerModal isOpen={showDisclaimer} onClose={() => setShowDisclaimer(false)} />

      {/* Search Limit Info */}
      {searchLimitInfo && (
        <div id="search-limit-info" className="mb-6 p-4 bg-primary-50 border border-primary-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-medium text-primary-900">Daily Search Limit</h4>
              <p className="text-sm text-primary-700">
                {searchLimitInfo.used_today} of {searchLimitInfo.daily_limit} searches used today
              </p>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-primary-900">
                {searchLimitInfo.remaining_today} remaining
              </div>
              {!searchLimitInfo.can_search && (
                <div className="text-sm text-error-600 font-medium">
                  Limit reached
                </div>
              )}
            </div>
          </div>
          
          {/* Progress bar */}
          <div className="mt-2 w-full bg-primary-200 rounded-full h-2">
            <div 
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(searchLimitInfo.used_today / searchLimitInfo.daily_limit) * 100}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Message Display */}
      {message && (
        <Alert 
          id="analysis-message"
          message={message} 
          onClose={() => setMessage(null)}
          className="mb-6"
        />
      )}

      {/* Search Form */}
      <Card id="search-form-card" className="mb-8">
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
            <div>
              <h2 id="search-form-title" className="text-lg sm:text-xl font-bold text-gray-900">
                Stock Analysis
              </h2>
              <p id="search-form-subtitle" className="text-xs sm:text-sm text-gray-600">
                Get AI-powered analysis and technical indicators for any stock
              </p>
            </div>
            <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
              <Button
                onClick={() => setShowDisclaimer(true)}
                size="sm"
                className="bg-amber-600 hover:bg-amber-700 text-white text-xs sm:text-sm w-full sm:w-auto"
              >
                <svg className="w-3 h-3 sm:w-4 sm:h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Read Disclaimer
              </Button>
              <Button
                id="todays-searches-button"
                onClick={() => navigate('/todays-searches')}
                size="sm"
                className="bg-blue-600 hover:bg-blue-700 text-white text-xs sm:text-sm w-full sm:w-auto"
              >
                <svg className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                Today's Searches
              </Button>
            </div>
          </div>
        </CardHeader>
        
        <CardBody>
          <form id="search-form" onSubmit={handleSubmit} className="space-y-6">
            <div id="symbol-field">
              <label htmlFor="symbol-input" className="block text-sm font-medium text-gray-700 mb-2">
                Stock Symbol
              </label>
              <InputWithIcon
                id="symbol-input"
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                placeholder="Enter stock symbol (e.g., AAPL, GOOGL, RELIANCE.NS, TCS)"
                disabled={loading || (searchLimitInfo?.can_search === false)}
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                }
              />
            </div>
            
            <div id="analysis-type-field">
              <label htmlFor="analysis-type-select" className="block text-sm font-medium text-gray-700 mb-2">
                Analysis Type
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <select
                  id="analysis-type-select"
                  value={analysisType}
                  onChange={(e) => setAnalysisType(e.target.value as 'technical' | 'ai' | 'both')}
                  className="input pl-10"
                  disabled={loading}
                >
                  <option value="both">Both (Technical + AI)</option>
                  <option value="technical">Technical Analysis Only</option>
                  <option value="ai">AI Analysis Only</option>
                </select>
              </div>
            </div>

            <Button
              id="analyze-button"
              type="submit"
              loading={loading}
              disabled={loading || !symbol.trim() || (searchLimitInfo?.can_search === false)}
              className="w-full"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Analyze Stock
            </Button>
          </form>
        </CardBody>
      </Card>

      {/* Results */}
      {result && (
        <div id="analysis-results" className="space-y-6">
          {/* Error Result */}
          {result.error && (
            <Card id="error-result-card">
              <CardHeader>
                <h3 id="error-result-title" className="text-lg font-semibold text-error-600">
                  Analysis Failed
                </h3>
              </CardHeader>
              <CardBody>
                <p id="error-result-message" className="text-error-600">
                  {result.error}
                </p>
              </CardBody>
            </Card>
          )}

          {/* Technical Analysis */}
          {result.technical_data && (
            <Card id="technical-analysis-card">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 id="technical-title" className="text-lg font-semibold text-gray-900">
                      Technical Analysis - {result.symbol}
                    </h3>
                    <p id="technical-subtitle" className="text-sm text-gray-600">
                      Last updated: {result.technical_data.last_updated}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getRecommendationColor(result.rule_analysis?.recommendation || 'HOLD')}`}>
                      {result.rule_analysis?.recommendation || 'HOLD'}
                    </span>
                    <span className={`text-xs font-medium ${getConfidenceColor(result.rule_analysis?.confidence || 'MEDIUM')}`}>
                      {result.rule_analysis?.confidence || 'MEDIUM'} Confidence
                    </span>
                  </div>
                </div>
              </CardHeader>
              
              <CardBody>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {/* Current Price */}
                  <div id="current-price-section" className="bg-gray-50 p-4 rounded-lg">
                    <Tooltip content="The current market price of the stock. This is the most recent price at which the stock was traded.">
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                        Current Price
                        <svg className="w-4 h-4 ml-1 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                        </svg>
                      </h4>
                    </Tooltip>
                    <p className="text-2xl font-bold text-gray-900">
                      {result.technical_data.current_price_formatted}
                    </p>
                    <p className="text-sm text-gray-600">
                      Currency: {result.technical_data.currency}
                    </p>
                  </div>

                  {/* RSI */}
                  <div id="rsi-section" className="bg-gray-50 p-4 rounded-lg">
                    <Tooltip content="Relative Strength Index (RSI) measures the speed and magnitude of price changes. Values above 70 indicate overbought conditions, while values below 30 indicate oversold conditions. RSI helps identify potential reversal points.">
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                        RSI
                        <svg className="w-4 h-4 ml-1 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                        </svg>
                      </h4>
                    </Tooltip>
                    <p className="text-2xl font-bold text-gray-900">
                      {result.technical_data.rsi.toFixed(2)}
                    </p>
                    <p className="text-sm text-gray-600">
                      {result.technical_data.rsi > 70 ? 'Overbought' : result.technical_data.rsi < 30 ? 'Oversold' : 'Neutral'}
                    </p>
                  </div>

                  {/* MACD */}
                  <div id="macd-section" className="bg-gray-50 p-4 rounded-lg">
                    <Tooltip content="Moving Average Convergence Divergence (MACD) is a trend-following momentum indicator. It shows the relationship between two moving averages of a stock's price. When MACD crosses above the signal line, it's considered bullish; when it crosses below, it's bearish.">
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                        MACD
                        <svg className="w-4 h-4 ml-1 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                        </svg>
                      </h4>
                    </Tooltip>
                    <p className="text-2xl font-bold text-gray-900">
                      {result.technical_data.macd.toFixed(4)}
                    </p>
                    <p className="text-sm text-gray-600">
                      Signal: {result.technical_data.macd_signal.toFixed(4)}
                    </p>
                  </div>

                  {/* Moving Averages */}
                  <div id="moving-averages-section" className="bg-gray-50 p-4 rounded-lg">
                    <Tooltip content="Simple Moving Averages (SMA) show the average price over a specific period. SMA 20 represents the average price over 20 days, while SMA 50 represents 50 days. When the current price is above the moving average, it's generally considered bullish.">
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                        Moving Averages
                        <svg className="w-4 h-4 ml-1 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                        </svg>
                      </h4>
                    </Tooltip>
                    <p className="text-lg font-semibold text-gray-900">
                      SMA 20: {result.technical_data.sma_20_formatted}
                    </p>
                    <p className="text-lg font-semibold text-gray-900">
                      SMA 50: {result.technical_data.sma_50_formatted}
                    </p>
                  </div>

                  {/* Volume */}
                  <div id="volume-section" className="bg-gray-50 p-4 rounded-lg">
                    <Tooltip content="Volume indicates the number of shares traded. High volume often confirms price movements - if a stock rises on high volume, it's more likely to continue rising. Volume ratio compares current volume to the 20-day average.">
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                        Volume
                        <svg className="w-4 h-4 ml-1 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                        </svg>
                      </h4>
                    </Tooltip>
                    <p className="text-lg font-semibold text-gray-900">
                      {result.technical_data.volume.toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-600">
                      Ratio: {result.technical_data.volume_ratio.toFixed(2)}x avg
                    </p>
                  </div>

                  {/* Price Change */}
                  <div id="price-change-section" className="bg-gray-50 p-4 rounded-lg">
                    <Tooltip content="Price change shows the percentage movement over different time periods. 1D shows yesterday's change, 5D shows the change over the past 5 trading days. These help understand short-term momentum.">
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                        Price Change
                        <svg className="w-4 h-4 ml-1 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                        </svg>
                      </h4>
                    </Tooltip>
                    <p className={`text-lg font-semibold ${result.technical_data.price_change_1d >= 0 ? 'text-success-600' : 'text-error-600'}`}>
                      1D: {result.technical_data.price_change_1d >= 0 ? '+' : ''}{result.technical_data.price_change_1d.toFixed(2)}%
                    </p>
                    <p className={`text-lg font-semibold ${result.technical_data.price_change_5d >= 0 ? 'text-success-600' : 'text-error-600'}`}>
                      5D: {result.technical_data.price_change_5d >= 0 ? '+' : ''}{result.technical_data.price_change_5d.toFixed(2)}%
                    </p>
                  </div>
                </div>

                {/* Support & Resistance */}
                <div id="support-resistance-section" className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div id="support-levels" className="bg-gray-50 p-4 rounded-lg">
                    <Tooltip content="Support levels are price points where the stock has historically found buying interest and bounced back up. These levels can act as floors where the price might stop falling.">
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                        Support Levels
                        <svg className="w-4 h-4 ml-1 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                        </svg>
                      </h4>
                    </Tooltip>
                    <div className="space-y-1">
                      {result.technical_data.support_levels_formatted.map((level, index) => (
                        <p key={index} className="text-sm text-gray-900">{level}</p>
                      ))}
                    </div>
                  </div>
                  
                  <div id="resistance-levels" className="bg-gray-50 p-4 rounded-lg">
                    <Tooltip content="Resistance levels are price points where the stock has historically faced selling pressure and struggled to move higher. These levels can act as ceilings where the price might stop rising.">
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                        Resistance Levels
                        <svg className="w-4 h-4 ml-1 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                        </svg>
                      </h4>
                    </Tooltip>
                    <div className="space-y-1">
                      {result.technical_data.resistance_levels_formatted.map((level, index) => (
                        <p key={index} className="text-sm text-gray-900">{level}</p>
                      ))}
                    </div>
                  </div>
                </div>
              </CardBody>
            </Card>
          )}

          {/* Rule-based Analysis */}
          {result.rule_analysis && (
            <Card id="rule-analysis-card">
              <CardHeader>
                <h3 id="rule-analysis-title" className="text-lg font-semibold text-gray-900">
                  Rule-based Analysis
                </h3>
              </CardHeader>
              <CardBody>
                <div className="space-y-4">
                  <div id="recommendation-section" className="flex items-center space-x-4">
                    <span className={`px-3 py-1 text-sm font-medium rounded-full border ${getRecommendationColor(result.rule_analysis.recommendation)}`}>
                      {result.rule_analysis.recommendation}
                    </span>
                    <span className={`text-sm font-medium ${getConfidenceColor(result.rule_analysis.confidence)}`}>
                      {result.rule_analysis.confidence} Confidence
                    </span>
                  </div>
                  
                  <div id="summary-section">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Summary</h4>
                    <p className="text-gray-900">{result.rule_analysis.summary}</p>
                  </div>
                  
                  <div id="key-points-section">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Key Points</h4>
                    <ul className="space-y-1">
                      {result.rule_analysis.key_points.map((point, index) => (
                        <li key={index} className="text-sm text-gray-900 flex items-start">
                          <span className="text-primary-600 mr-2">•</span>
                          {point}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CardBody>
            </Card>
          )}

          {/* AI Analysis */}
          {result.ai_analysis && (
            <Card id="ai-analysis-card">
              <CardHeader>
                <h3 id="ai-analysis-title" className="text-lg font-semibold text-gray-900">
                  AI Analysis
                </h3>
              </CardHeader>
              <CardBody>
                <div id="ai-analysis-content" className="prose prose-sm max-w-none">
                  <ReactMarkdown
                    components={{
                      h1: ({ children }) => <h1 className="text-xl font-bold text-gray-900 mb-4">{children}</h1>,
                      h2: ({ children }) => <h2 className="text-lg font-semibold text-gray-900 mb-3">{children}</h2>,
                      h3: ({ children }) => <h3 className="text-base font-medium text-gray-900 mb-2">{children}</h3>,
                      p: ({ children }) => <p className="text-gray-700 mb-3 leading-relaxed">{children}</p>,
                      ul: ({ children }) => <ul className="list-disc list-inside space-y-1 mb-3">{children}</ul>,
                      li: ({ children }) => <li className="text-gray-700">{children}</li>,
                      strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                      em: ({ children }) => <em className="italic text-gray-700">{children}</em>,
                      code: ({ children }) => <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono">{children}</code>,
                      blockquote: ({ children }) => <blockquote className="border-l-4 border-primary-500 pl-4 italic text-gray-600 mb-3">{children}</blockquote>,
                      pre: ({ children }) => <pre className="bg-gray-100 p-3 rounded overflow-x-auto text-sm mb-3">{children}</pre>,
                      table: ({ children }) => <table className="w-full border-collapse border border-gray-300 mb-3">{children}</table>,
                      th: ({ children }) => <th className="border border-gray-300 px-3 py-2 bg-gray-50 font-medium text-left">{children}</th>,
                      td: ({ children }) => <td className="border border-gray-300 px-3 py-2">{children}</td>,
                    }}
                  >
                    {result.ai_analysis.ai_analysis}
                  </ReactMarkdown>
                </div>
              </CardBody>
            </Card>
          )}
        </div>
      )}
    </div>
  );
} 