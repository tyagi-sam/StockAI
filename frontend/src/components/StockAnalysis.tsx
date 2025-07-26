'use client';

import { useState } from 'react';
import { stockAnalysis } from '../services/api';
import toast from 'react-hot-toast';

interface AnalysisResult {
  symbol: string;
  technical_data?: {
    symbol: string;
    current_price: number;
    rsi: number;
    macd: number;
    macd_signal: number;
    sma_20: number;
    sma_50: number;
    volume: number;
    volume_sma_20: number;
    volume_ratio: number;
    price_change_5d: number;
    price_change_1d: number;
    support_levels: number[];
    resistance_levels: number[];
    pivot_points: {
      pivot: number;
      r1: number;
      r2: number;
      s1: number;
      s2: number;
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

export default function StockAnalysis() {
  const [symbol, setSymbol] = useState('');
  const [analysisType, setAnalysisType] = useState<'technical' | 'ai' | 'both'>('both');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!symbol.trim()) {
      toast.error('Please enter a stock symbol');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await stockAnalysis.analyze(symbol.toUpperCase(), analysisType);
      if (response.data.success && response.data.data) {
        setResult(response.data.data);
        toast.success(`Analysis completed for ${symbol.toUpperCase()}`);
      } else {
        throw new Error(response.data.error || 'Analysis failed');
      }
    } catch (error: any) {
      console.error('Analysis error:', error);
      const errorMessage = error.response?.data?.detail || 'Analysis failed';
      toast.error(errorMessage);
      setResult({ symbol: symbol.toUpperCase(), error: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
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
                  placeholder="Enter stock symbol (e.g., AAPL, GOOGL, MSFT)"
                  disabled={loading}
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
                disabled={loading}
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
              disabled={loading || !symbol.trim()}
            >
              {loading ? (
                <div>
                  <div>Loading...</div>
                  <span>Analyzing...</span>
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
        <div>
          <div>
            <h3>
              Analysis Results for {result.symbol}
            </h3>
            {result.error && (
              <span>
                Analysis Failed
              </span>
            )}
          </div>

          {result.error ? (
            <div>
              <div>
                <div>
                  <h4>Analysis Failed</h4>
                  <p>{result.error}</p>
                </div>
              </div>
            </div>
          ) : (
            <div>
              {/* Technical Analysis */}
              {result.technical_data && (
                <div>
                  <div>
                    <div>
                      <h4>Technical Analysis</h4>
                    </div>
                  </div>
                  <div>
                    <div>
                      <span>Current Price:</span>
                      <span>
                        ${result.technical_data.current_price.toFixed(2)}
                      </span>
                    </div>
                    
                    <div>
                      <div>
                        <span>RSI:</span>
                        <p>
                          {result.technical_data.rsi.toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <span>MACD:</span>
                        <p>
                          {result.technical_data.macd.toFixed(3)}
                        </p>
                      </div>
                    </div>
                    
                    <div>
                      <div>
                        <span>20-day SMA:</span>
                        <p>
                          ${result.technical_data.sma_20.toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <span>50-day SMA:</span>
                        <p>
                          ${result.technical_data.sma_50.toFixed(2)}
                        </p>
                      </div>
                    </div>
                    
                    <div>
                      <div>
                        <span>1-day Change:</span>
                        <p>
                          {result.technical_data.price_change_1d >= 0 ? '+' : ''}{result.technical_data.price_change_1d.toFixed(2)}%
                        </p>
                      </div>
                      <div>
                        <span>5-day Change:</span>
                        <p>
                          {result.technical_data.price_change_5d >= 0 ? '+' : ''}{result.technical_data.price_change_5d.toFixed(2)}%
                        </p>
                      </div>
                    </div>
                    
                    <div>
                      <span>Support Levels:</span>
                      <p>
                        {result.technical_data.support_levels.map(level => `$${level.toFixed(2)}`).join(', ')}
                      </p>
                    </div>
                    
                    <div>
                      <span>Resistance Levels:</span>
                      <p>
                        {result.technical_data.resistance_levels.map(level => `$${level.toFixed(2)}`).join(', ')}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* AI Analysis */}
              {result.ai_analysis && (
                <div>
                  <div>
                    <div>
                      <h4>AI Analysis</h4>
                    </div>
                  </div>
                  <div>
                    <div>
                      <span>Analysis:</span>
                      <div>
                        <pre>
                          {result.ai_analysis.ai_analysis}
                        </pre>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Rule-based Analysis */}
              {result.rule_analysis && (
                <div>
                  <div>
                    <div>
                      <h4>Rule-based Analysis</h4>
                    </div>
                  </div>
                  <div>
                    <div>
                      <span>Recommendation:</span>
                      <span>
                        {result.rule_analysis.recommendation}
                      </span>
                    </div>
                    
                    <div>
                      <span>Confidence:</span>
                      <span>
                        {result.rule_analysis.confidence}
                      </span>
                    </div>
                    
                    <div>
                      <span>Key Points:</span>
                      <ul>
                        {result.rule_analysis.key_points.map((point, index) => (
                          <li key={index}>
                            {point}
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
                <p>Enter stock symbols in uppercase (e.g., AAPL, GOOGL, MSFT)</p>
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
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 