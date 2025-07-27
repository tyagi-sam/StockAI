export interface User {
  id: number;
  email: string;
  name: string;
  is_email_verified: boolean;
  email_verified_at?: string;
  daily_search_count: number;
  last_search_reset?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterResponse {
  message: string;
  user: User;
}

export interface VerifyEmailResponse {
  message: string;
  access_token: string;
  user: User;
}

export interface ResendOtpResponse {
  message: string;
}

export interface SearchLimitInfo {
  daily_limit: number;
  used_today: number;
  remaining_today: number;
  can_search: boolean;
  last_reset?: string;
}

export interface TechnicalData {
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
}

export interface RuleAnalysis {
  summary: string;
  recommendation: string;
  confidence: string;
  key_points: string[];
}

export interface AIAnalysis {
  ai_analysis: string;
}

export interface AnalysisResult {
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

export interface AnalysisResponse {
  success: boolean;
  data?: AnalysisResult;
  error?: string;
  search_limit_info?: SearchLimitInfo;
}

export interface SearchStatusResponse {
  search_limit_info: SearchLimitInfo;
}

export interface Message {
  type: 'success' | 'error' | 'warning' | 'info';
  text: string;
} 