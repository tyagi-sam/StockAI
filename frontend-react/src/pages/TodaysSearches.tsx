import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { stockAnalysis } from '../services/api';
import Button from '../components/common/Button';
import Card, { CardHeader, CardBody } from '../components/common/Card';
import Alert from '../components/common/Alert';
import type { TodaysSearch, AnalysisResult, Message } from '../types';

export default function TodaysSearches() {
  const navigate = useNavigate();
  const [searches, setSearches] = useState<TodaysSearch[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<Message | null>(null);
  const [expandedSymbols, setExpandedSymbols] = useState<Set<string>>(new Set());
  const [expandedAnalyses, setExpandedAnalyses] = useState<Record<string, AnalysisResult>>({});
  const [expandingLoading, setExpandingLoading] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchTodaysSearches();
  }, []);

  const fetchTodaysSearches = async () => {
    try {
      setLoading(true);
      const response = await stockAnalysis.getTodaysSearches();
      
      if (response.data.success) {
        setSearches(response.data.data);
        if (response.data.count === 0) {
          setMessage({ type: 'info', text: 'No searches found for today. Start analyzing stocks to see them here!' });
        }
      } else {
        throw new Error('Failed to fetch today\'s searches');
      }
    } catch (error: any) {
      console.error('Failed to fetch today\'s searches:', error);
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || error.message || 'Failed to fetch today\'s searches' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExpandAnalysis = async (symbol: string) => {
    if (expandedSymbols.has(symbol)) {
      // Collapse if already expanded
      setExpandedSymbols(prev => {
        const newSet = new Set(prev);
        newSet.delete(symbol);
        return newSet;
      });
      setExpandedAnalyses(prev => {
        const newAnalyses = { ...prev };
        delete newAnalyses[symbol];
        return newAnalyses;
      });
      return;
    }

    try {
      setExpandingLoading(prev => new Set(prev).add(symbol));
      const response = await stockAnalysis.getTodaysSearchDetail(symbol, 'both');
      
      if (response.data.success) {
        setExpandedSymbols(prev => new Set(prev).add(symbol));
        setExpandedAnalyses(prev => ({
          ...prev,
          [symbol]: response.data.data
        }));
      } else {
        throw new Error('Failed to fetch analysis details');
      }
    } catch (error: any) {
      console.error('Failed to fetch analysis details:', error);
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || error.message || 'Failed to fetch analysis details' 
      });
    } finally {
      setExpandingLoading(prev => {
        const newSet = new Set(prev);
        newSet.delete(symbol);
        return newSet;
      });
    }
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence.toUpperCase()) {
      case 'BUY':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'SELL':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'HOLD':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getPriceChangeColor = (change: number) => {
    if (change > 0) return 'text-green-600';
    if (change < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const formatPrice = (price: number, currency: string) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency === 'INR' ? 'INR' : 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const renderAnalysisDetails = (analysis: AnalysisResult) => {
    if (!analysis.technical_data) return null;

    const tech = analysis.technical_data;
    
    return (
      <div id="analysis-details" className="mt-4 space-y-4">
        {/* Technical Indicators */}
        <div id="technical-indicators" className="space-y-4">
          <h4 id="indicators-title" className="text-lg font-semibold text-gray-900 mb-3">Technical Indicators</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div id="rsi-indicator" className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <h5 id="rsi-title" className="text-sm font-medium text-blue-900">RSI</h5>
                <span id="rsi-value" className="text-xl font-bold text-blue-700">{tech.rsi?.toFixed(2) || 'N/A'}</span>
              </div>
            </div>
            
            <div id="macd-indicator" className="bg-purple-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <h5 id="macd-title" className="text-sm font-medium text-purple-900">MACD</h5>
                <span id="macd-value" className="text-xl font-bold text-purple-700">{tech.macd?.toFixed(2) || 'N/A'}</span>
              </div>
            </div>
            
            <div id="sma20-indicator" className="bg-green-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <h5 id="sma20-title" className="text-sm font-medium text-green-900">SMA 20</h5>
                <span id="sma20-value" className="text-xl font-bold text-green-700">{tech.sma_20_formatted || 'N/A'}</span>
              </div>
            </div>
            
            <div id="sma50-indicator" className="bg-orange-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <h5 id="sma50-title" className="text-sm font-medium text-orange-900">SMA 50</h5>
                <span id="sma50-value" className="text-xl font-bold text-orange-700">{tech.sma_50_formatted || 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Support & Resistance */}
        {tech.support_levels && tech.resistance_levels && (
          <div id="support-resistance" className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div id="support-levels" className="bg-red-50 p-4 rounded-lg">
              <h4 id="support-title" className="text-sm font-medium text-red-900 mb-2">Support Levels</h4>
              <div id="support-values" className="space-y-1">
                {tech.support_levels_formatted?.map((level, index) => (
                  <p key={index} className="text-sm text-red-700">{level}</p>
                ))}
              </div>
            </div>
            
            <div id="resistance-levels" className="bg-green-50 p-4 rounded-lg">
              <h4 id="resistance-title" className="text-sm font-medium text-green-900 mb-2">Resistance Levels</h4>
              <div id="resistance-values" className="space-y-1">
                {tech.resistance_levels_formatted?.map((level, index) => (
                  <p key={index} className="text-sm text-green-700">{level}</p>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* AI Analysis */}
        {analysis.ai_analysis && (
          <div id="ai-analysis" className="bg-blue-50 p-4 rounded-lg">
            <h4 id="ai-title" className="text-sm font-medium text-blue-900 mb-2">AI Analysis</h4>
            <div id="ai-content" className="text-sm text-blue-700">
              <ReactMarkdown 
                components={{
                  ul: ({ children }) => (
                    <ul className="list-disc list-inside space-y-1 mb-3">{children}</ul>
                  ),
                  li: ({ children }) => (
                    <li className="text-blue-700">{children}</li>
                  ),
                  strong: ({ children }) => (
                    <strong className="font-bold text-blue-900">{children}</strong>
                  ),
                  p: ({ children }) => (
                    <p className="mb-2">{children}</p>
                  )
                }}
              >
                {analysis.ai_analysis.ai_analysis}
              </ReactMarkdown>
            </div>
          </div>
        )}

        {/* Rule Analysis */}
        {analysis.rule_analysis && (
          <div id="rule-analysis" className="bg-gray-50 p-4 rounded-lg">
            <h4 id="rule-title" className="text-sm font-medium text-gray-900 mb-2">Technical Analysis</h4>
            <p id="rule-summary" className="text-sm text-gray-700 mb-2">{analysis.rule_analysis.summary}</p>
            {analysis.rule_analysis.key_points && (
              <div id="rule-points">
                <h5 id="rule-points-title" className="text-xs font-medium text-gray-600 mb-1">Key Points:</h5>
                <ul id="rule-points-list" className="text-xs text-gray-600 space-y-1">
                  {analysis.rule_analysis.key_points.map((point, index) => (
                    <li key={index} className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div id="todays-searches-loading" className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading today's searches...</p>
        </div>
      </div>
    );
  }

  return (
    <div id="todays-searches-page" className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div id="page-header" className="mb-8">
          <h1 id="page-title" className="text-3xl font-bold text-gray-900 mb-2">
            Today's Searches
          </h1>
          <p id="page-subtitle" className="text-gray-600">
            View and analyze all the stocks you've searched for today
          </p>
        </div>

        {/* Alert Messages */}
        {message && (
          <Alert
            id="todays-searches-alert"
            message={message}
            onClose={() => setMessage(null)}
            className="mb-6"
          />
        )}

        {/* Action Buttons */}
        <div id="action-buttons" className="mb-6 flex space-x-4">
          <Button
            id="back-button"
            onClick={() => navigate('/dashboard')}
            className="bg-gray-600 hover:bg-gray-700 text-white"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Dashboard
          </Button>
          <Button
            id="refresh-button"
            onClick={fetchTodaysSearches}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </Button>
        </div>

        {/* Searches List */}
        {searches.length === 0 ? (
          <Card id="empty-state-card">
            <CardBody>
              <div id="empty-state" className="text-center py-12">
                <div id="empty-icon" className="mx-auto h-12 w-12 text-gray-400 mb-4">
                  <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 id="empty-title" className="text-lg font-medium text-gray-900 mb-2">
                  No searches today
                </h3>
                <p id="empty-description" className="text-gray-600">
                  Start analyzing stocks to see them appear here!
                </p>
              </div>
            </CardBody>
          </Card>
        ) : (
          <div id="searches-grid" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {searches.map((search, index) => (
              <Card key={search.symbol} id={`search-card-${index}`} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                                      <div id={`search-header-${index}`} className="flex items-center justify-between">
                      <h3 id={`search-symbol-${index}`} className="text-xl font-bold text-gray-900">
                        {search.symbol}
                      </h3>
                      <span id={`search-confidence-${index}`} className={`px-2 py-1 text-xs font-medium rounded-full border ${getConfidenceColor(search.confidence_level)}`}>
                        {search.confidence_level}
                      </span>
                    </div>
                </CardHeader>
                
                <CardBody>
                  <div id={`search-content-${index}`} className="space-y-3">
                    {/* Price Info */}
                    <div id={`search-price-${index}`} className="flex items-center justify-between">
                      <span id={`search-price-label-${index}`} className="text-sm text-gray-600">Current Price:</span>
                      <span id={`search-price-value-${index}`} className="text-lg font-semibold text-gray-900">
                        {formatPrice(search.current_price, search.currency)}
                      </span>
                    </div>

                    {/* Price Change */}
                    <div id={`search-change-${index}`} className="flex items-center justify-between">
                      <span id={`search-change-label-${index}`} className="text-sm text-gray-600">1D Change:</span>
                      <span id={`search-change-value-${index}`} className={`text-sm font-medium ${getPriceChangeColor(search.price_change_1d)}`}>
                        {search.price_change_1d > 0 ? '+' : ''}{search.price_change_1d.toFixed(2)}%
                      </span>
                    </div>

                    {/* Timestamp */}
                    <div id={`search-timestamp-${index}`} className="text-xs text-gray-500">
                      Searched: {formatTimestamp(search.timestamp)}
                    </div>

                    {/* Expand Button */}
                    <Button
                      id={`expand-button-${index}`}
                      onClick={() => handleExpandAnalysis(search.symbol)}
                      disabled={expandingLoading.has(search.symbol)}
                      className="w-full mt-3 bg-gray-100 hover:bg-gray-200 text-gray-700"
                    >
                      {expandingLoading.has(search.symbol) ? (
                        <span className="flex items-center">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
                          Loading...
                        </span>
                      ) : expandedSymbols.has(search.symbol) ? (
                        'Collapse Analysis'
                      ) : (
                        'View Full Analysis'
                      )}
                    </Button>
                  </div>

                  {/* Expanded Analysis */}
                  {expandedSymbols.has(search.symbol) && expandedAnalyses[search.symbol] && (
                    <div id={`expanded-analysis-${index}`} className="mt-4 pt-4 border-t border-gray-200">
                      {renderAnalysisDetails(expandedAnalyses[search.symbol])}
                    </div>
                  )}
                </CardBody>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
} 