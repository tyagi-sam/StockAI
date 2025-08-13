import logging
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from openai import OpenAI
from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.search_limit import SearchLimitService
from app.services.technical_indicators import get_technical_indicators
from app.services.stock_cache import stock_cache_service
from app.core.config import settings
from app.core.logger import logger
from app.core.rate_limiter import limiter

router = APIRouter()

# Currency conversion rates (you can update these or use a live API)
USD_TO_INR_RATE = 83.0  # Approximate rate, can be updated

def convert_utc_to_ist(utc_date):
    """Convert datetime to Indian Standard Time and format for display"""
    try:
        # Check if the date already has timezone info
        if hasattr(utc_date, 'tzinfo') and utc_date.tzinfo is not None:
            # Date already has timezone, convert to IST
            ist_offset = timedelta(hours=5, minutes=30)
            ist_date = utc_date.astimezone(timezone(ist_offset))
        else:
            # Assume UTC and convert to IST
            ist_offset = timedelta(hours=5, minutes=30)
            ist_date = utc_date.replace(tzinfo=timezone.utc).astimezone(timezone(ist_offset))
        
        # Format the date
        formatted_date = ist_date.strftime("%Y-%m-%d %H:%M:%S IST")
        
        # If it's 00:00:00, it's likely end-of-day data
        if ist_date.hour == 0 and ist_date.minute == 0 and ist_date.second == 0:
            return f"{ist_date.strftime('%Y-%m-%d')} (End of Day) IST"
        
        return formatted_date
        
    except Exception as e:
        logger.error(f"Error converting timezone: {e}")
        return utc_date.strftime("%Y-%m-%d %H:%M:%S UTC")

def format_currency(amount: float, currency: str) -> str:
    """Format amount with appropriate currency symbol"""
    if currency == "INR":
        return f"₹{amount:,.2f}"
    else:
        return f"${amount:,.2f}"

def calculate_support_resistance(high_prices: np.ndarray, low_prices: np.ndarray, close_prices: np.ndarray, periods: int = 20) -> tuple:
    """Calculate support and resistance levels using pivot points and recent highs/lows"""
    try:
        # Get recent data for analysis
        recent_highs = high_prices[-periods:]
        recent_lows = low_prices[-periods:]
        
        # Find significant highs and lows
        resistance_levels = []
        support_levels = []
        
        # Resistance levels (recent highs)
        for i in range(1, len(recent_highs) - 1):
            if recent_highs[i] > recent_highs[i-1] and recent_highs[i] > recent_highs[i+1]:
                resistance_levels.append(float(recent_highs[i]))
        
        # Support levels (recent lows)
        for i in range(1, len(recent_lows) - 1):
            if recent_lows[i] < recent_lows[i-1] and recent_lows[i] < recent_lows[i+1]:
                support_levels.append(float(recent_lows[i]))
        
        # Sort and get top 3 levels
        resistance_levels = sorted(list(set(resistance_levels)), reverse=True)[:3]
        support_levels = sorted(list(set(support_levels)))[:3]
        
        # Calculate pivot points
        current_high = float(high_prices[-1])
        current_low = float(low_prices[-1])
        current_close = float(close_prices[-1])
        
        pivot_point = (current_high + current_low + current_close) / 3
        r1 = (2 * pivot_point) - current_low
        r2 = pivot_point + (current_high - current_low)
        s1 = (2 * pivot_point) - current_high
        s2 = pivot_point - (current_high - current_low)
        
        pivot_points = {
            "pivot": round(pivot_point, 2),
            "r1": round(r1, 2),
            "r2": round(r2, 2),
            "s1": round(s1, 2),
            "s2": round(s2, 2)
        }
        
        return support_levels, resistance_levels, pivot_points
        
    except Exception as e:
        logger.error(f"Error calculating support/resistance: {e}", exc_info=True)
        return [], [], {}

def calculate_volume_analysis(volumes: np.ndarray, close_prices: np.ndarray) -> tuple:
    """Calculate volume-based indicators"""
    try:
        # Volume SMA (20-day)
        volume_sma_20 = float(np.mean(volumes[-20:])) if len(volumes) >= 20 else float(np.mean(volumes))
        
        # Current volume ratio
        current_volume = float(volumes[-1])
        volume_ratio = current_volume / volume_sma_20 if volume_sma_20 > 0 else 1.0
        
        return volume_sma_20, volume_ratio
        
    except Exception as e:
        logger.error(f"Error calculating volume analysis: {e}", exc_info=True)
        return 0.0, 1.0

def calculate_pivot_points(high: float, low: float, close: float) -> dict:
    """Calculate pivot points for support and resistance"""
    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    s1 = 2 * pivot - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    
    return {
        "pivot": round(pivot, 2),
        "r1": round(r1, 2),
        "r2": round(r2, 2),
        "s1": round(s1, 2),
        "s2": round(s2, 2)
    }

# Initialize OpenAI client with error handling
def get_openai_client():
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        logger.warning("OPENAI_API_KEY not set, AI analysis will be disabled")
        return None
    return OpenAI(api_key=api_key)

try:
    client = get_openai_client()
except Exception as e:
    logger.warning(f"Failed to initialize OpenAI client: {e}")
    client = None

def get_stock_data_yfinance(symbol: str, days: int = 90) -> Optional[List[Dict]]:
    """Get stock data using yfinance with priority for Indian markets"""
    try:
        logger.info(f"Fetching stock data for {symbol}")
        
        # For Indian stocks, try Indian exchanges first
        symbol_variants = [
            f"{symbol}.NS",  # NSE - National Stock Exchange (India)
            f"{symbol}.BO",  # BSE - Bombay Stock Exchange (India)
            symbol,          # Original symbol (for international stocks)
        ]
        
        for variant in symbol_variants:
            try:
                logger.debug(f"Trying yfinance with symbol: {variant}")
                ticker = yf.Ticker(variant)
                hist = ticker.history(period=f"{days}d")
                
                if not hist.empty:
                    # Get exchange info
                    info = ticker.info
                    exchange = info.get('exchange', 'Unknown')
                    currency = info.get('currency', 'USD')
                    
                    logger.info(f"Successfully retrieved data for {variant} from {exchange} in {currency}")
                    
                    data = []
                    for date, row in hist.iterrows():
                        data.append({
                            "date": date.strftime("%Y-%m-%d"),
                            "open": float(row["Open"]),
                            "high": float(row["High"]),
                            "low": float(row["Low"]),
                            "close": float(row["Close"]),
                            "volume": int(row["Volume"]),
                            "exchange": exchange,
                            "currency": currency,
                            "last_updated": convert_utc_to_ist(date)
                        })
                    
                    logger.info(f"Retrieved {len(data)} data points for {variant}")
                    return data
            except Exception as e:
                logger.debug(f"Failed with symbol {variant}: {str(e)}")
                continue
        
        logger.error(f"All symbol variants failed for {symbol}")
        return None
        
    except Exception as e:
        logger.error(f"yfinance failed for {symbol}: {str(e)}")
        return None

def get_currency_info_from_data(stock_data: List[Dict]) -> Dict[str, str]:
    """Determine currency info from actual stock data"""
    if not stock_data:
        return {
            "currency": "USD",
            "symbol": "",
            "exchange": "US",
            "is_indian": False
        }
    
    # Get currency from the first data point
    first_data = stock_data[0]
    currency = first_data.get('currency', 'USD')
    exchange = first_data.get('exchange', 'Unknown')
    
    # Determine if it's Indian based on exchange and currency
    is_indian = (exchange in ['NSE', 'BSE', 'NSI', 'BSE INDIA'] or 
                 currency == 'INR' or 
                 exchange in ['NSE', 'BSE'])
    
    logger.info(f"Currency info from data: {currency}, Exchange: {exchange}, Is Indian: {is_indian}")
    
    return {
        "currency": currency,
        "symbol": "",
        "exchange": exchange,
        "is_indian": is_indian
    }

class StockAnalysisRequest(BaseModel):
    symbol: str
    analysis_type: str = "technical"  # technical, ai, or both

class TechnicalData(BaseModel):
    symbol: str
    current_price: float
    current_price_formatted: str
    currency: str
    is_indian_stock: bool
    last_updated: str
    rsi: float
    macd: float
    macd_signal: float
    sma_20: float
    sma_20_formatted: str
    sma_50: float
    sma_50_formatted: str
    volume: int
    volume_sma_20: float
    volume_ratio: float
    price_change_5d: float
    price_change_1d: float
    support_levels: list
    support_levels_formatted: list
    resistance_levels: list
    resistance_levels_formatted: list
    pivot_points: dict
    pivot_points_formatted: dict

class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    search_limit_info: Optional[dict] = None

def get_technical_analysis(symbol: str, user: User) -> TechnicalData:
    """Get technical analysis for a stock symbol"""
    try:
        logger.info(f"Getting technical analysis for symbol: {symbol}")
        
        # Use yfinance as primary source (no authentication required)
        stock_data = get_stock_data_yfinance(symbol, days=90)
        if not stock_data:
            raise ValueError(f"Could not fetch stock data for {symbol}")
        
        # Convert to numpy arrays for technical analysis
        close_prices = np.array([float(d['close']) for d in stock_data])
        high_prices = np.array([float(d['high']) for d in stock_data])
        low_prices = np.array([float(d['low']) for d in stock_data])
        volumes = np.array([int(d['volume']) for d in stock_data])
        
        # Calculate technical indicators using our custom module
        indicators = get_technical_indicators(close_prices, high_prices, low_prices)
        
        rsi = indicators['rsi']
        macd = indicators['macd']
        macd_signal = indicators['macd_signal']
        sma_20 = indicators['sma_20']
        sma_50 = indicators['sma_50']
        
        # Calculate support and resistance
        support_levels, resistance_levels, pivot_points = calculate_support_resistance(high_prices, low_prices, close_prices)
        
        # Calculate volume analysis
        volume_sma_20, volume_ratio = calculate_volume_analysis(volumes, close_prices)
        
        # Calculate price changes
        current_price = close_prices[-1]
        price_change_1d = ((current_price - close_prices[-2]) / close_prices[-2]) * 100 if len(close_prices) > 1 else 0
        price_change_5d = ((current_price - close_prices[-6]) / close_prices[-6]) * 100 if len(close_prices) > 5 else 0
        
        # Get currency info from actual data
        currency_info = get_currency_info_from_data(stock_data)
        logger.info(f"Currency info for {symbol}: {currency_info}")
        
        # Format pivot points with currency
        pivot_points_formatted = {}
        for key, value in pivot_points.items():
            pivot_points_formatted[key] = format_currency(value, currency_info["currency"])
        
        return TechnicalData(
            symbol=symbol.upper(),
            current_price=current_price,
            current_price_formatted=format_currency(current_price, currency_info["currency"]),
            currency=currency_info["currency"],
            is_indian_stock=currency_info["is_indian"],
            last_updated=stock_data[-1]["last_updated"],
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            sma_20=sma_20,
            sma_20_formatted=format_currency(sma_20, currency_info["currency"]),
            sma_50=sma_50,
            sma_50_formatted=format_currency(sma_50, currency_info["currency"]),
            volume=volumes[-1],
            volume_sma_20=volume_sma_20,
            volume_ratio=volume_ratio,
            price_change_5d=price_change_5d,
            price_change_1d=price_change_1d,
            support_levels=support_levels,
            support_levels_formatted=[format_currency(s, currency_info["currency"]) for s in support_levels],
            resistance_levels=resistance_levels,
            resistance_levels_formatted=[format_currency(r, currency_info["currency"]) for r in resistance_levels],
            pivot_points=pivot_points,
            pivot_points_formatted=pivot_points_formatted
        )
        
    except Exception as e:
        logger.error(f"Error getting technical analysis for {symbol}: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to analyze {symbol}: {str(e)}")

def create_analysis_prompt(tech_data: TechnicalData) -> str:
    """Create a prompt for AI analysis"""
    prompt = f"""
    Analyze the following stock data for {tech_data.symbol}:
    
    Current Price: {tech_data.current_price_formatted}
    RSI: {tech_data.rsi:.2f}
    MACD: {tech_data.macd:.2f}
    MACD Signal: {tech_data.macd_signal:.2f}
    20-day SMA: {tech_data.sma_20_formatted}
    50-day SMA: {tech_data.sma_50_formatted}
    1-day Change: {tech_data.price_change_1d:.2f}%
    5-day Change: {tech_data.price_change_5d:.2f}%
    Volume Ratio: {tech_data.volume_ratio:.2f}
    
    Support Levels: {tech_data.support_levels_formatted}
    Resistance Levels: {tech_data.resistance_levels_formatted}
    Pivot Points: {tech_data.pivot_points_formatted}
    
    Please provide:
    1. Technical analysis summary
    2. Buy/Sell/Hold recommendation
    3. Key support and resistance levels
    4. Risk assessment
    5. Short-term price targets
    """
    return prompt

async def get_ai_analysis(tech_data: TechnicalData) -> dict:
    """Get AI analysis using OpenAI"""
    if not client:
        raise ValueError("OpenAI client not available")
    
    try:
        prompt = create_analysis_prompt(tech_data)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional stock analyst. Provide clear, actionable analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        analysis = response.choices[0].message.content
        return {"ai_analysis": analysis}
        
    except Exception as e:
        logger.error(f"Error getting AI analysis: {e}", exc_info=True)
        raise

def filter_analysis_by_type(analysis_data: dict, requested_type: str) -> dict:
    """Filter analysis data to return only the requested analysis type"""
    filtered_data = {
        "symbol": analysis_data["symbol"],
        "analysis_type": requested_type
    }
    
    # Always include technical data
    if "technical_data" in analysis_data:
        filtered_data["technical_data"] = analysis_data["technical_data"]
    
    # Include AI analysis only if requested
    if requested_type in ["ai", "both"] and "ai_analysis" in analysis_data:
        filtered_data["ai_analysis"] = analysis_data["ai_analysis"]
    
    # Include rule analysis only if requested
    if requested_type in ["technical", "both"] and "rule_analysis" in analysis_data:
        filtered_data["rule_analysis"] = analysis_data["rule_analysis"]
    
    return filtered_data

def get_rule_based_analysis(tech_data: TechnicalData) -> dict:
    """Perform rule-based analysis using technical indicators with weighted scoring"""
    try:
        analysis = {
            "summary": "",
            "recommendation": "HOLD",
            "confidence": "MEDIUM",
            "key_points": []
        }
        
        # Initialize scoring system
        buy_signals = 0
        sell_signals = 0
        total_signals = 0
        
        # RSI Analysis (Weight: 25%)
        if tech_data.rsi > 70:
            analysis["key_points"].append("RSI indicates overbought conditions (>70)")
            sell_signals += 1
            total_signals += 1
        elif tech_data.rsi < 30:
            analysis["key_points"].append("RSI indicates oversold conditions (<30)")
            buy_signals += 1
            total_signals += 1
        elif tech_data.rsi > 60:
            analysis["key_points"].append("RSI showing bullish momentum (60-70)")
            buy_signals += 0.5
            total_signals += 1
        elif tech_data.rsi < 40:
            analysis["key_points"].append("RSI showing bearish momentum (30-40)")
            sell_signals += 0.5
            total_signals += 1
        else:
            analysis["key_points"].append("RSI in neutral range (40-60)")
            total_signals += 1
        
        # MACD Analysis (Weight: 25%)
        if tech_data.macd > tech_data.macd_signal:
            if tech_data.macd > 0:
                analysis["key_points"].append("MACD bullish and above zero line")
                buy_signals += 1
            else:
                analysis["key_points"].append("MACD bullish but below zero line")
                buy_signals += 0.5
            total_signals += 1
        else:
            if tech_data.macd < 0:
                analysis["key_points"].append("MACD bearish and below zero line")
                sell_signals += 1
            else:
                analysis["key_points"].append("MACD bearish but above zero line")
                sell_signals += 0.5
            total_signals += 1
        
        # Moving Average Analysis (Weight: 20%)
        if tech_data.current_price > tech_data.sma_20 > tech_data.sma_50:
            analysis["key_points"].append("Price above both moving averages - strong bullish trend")
            buy_signals += 1
            total_signals += 1
        elif tech_data.current_price < tech_data.sma_20 < tech_data.sma_50:
            analysis["key_points"].append("Price below both moving averages - strong bearish trend")
            sell_signals += 1
            total_signals += 1
        elif tech_data.current_price > tech_data.sma_20:
            analysis["key_points"].append("Price above 20-day SMA - short-term bullish")
            buy_signals += 0.5
            total_signals += 1
        else:
            analysis["key_points"].append("Price below 20-day SMA - short-term bearish")
            sell_signals += 0.5
            total_signals += 1
        
        # Volume Analysis (Weight: 15%)
        if tech_data.volume_ratio > 1.5:
            if buy_signals > sell_signals:
                analysis["key_points"].append("High volume confirms bullish momentum")
                buy_signals += 0.5
            elif sell_signals > buy_signals:
                analysis["key_points"].append("High volume confirms bearish momentum")
                sell_signals += 0.5
            else:
                analysis["key_points"].append("High volume indicates strong interest")
            total_signals += 1
        elif tech_data.volume_ratio < 0.5:
            analysis["key_points"].append("Low volume suggests weak conviction")
            total_signals += 1
        
        # Price Momentum Analysis (Weight: 15%)
        if tech_data.price_change_1d > 2:
            analysis["key_points"].append("Strong positive daily momentum (+{:.1f}%)".format(tech_data.price_change_1d))
            buy_signals += 0.5
            total_signals += 1
        elif tech_data.price_change_1d < -2:
            analysis["key_points"].append("Strong negative daily momentum ({:.1f}%)".format(tech_data.price_change_1d))
            sell_signals += 0.5
            total_signals += 1
        
        if tech_data.price_change_5d > 5:
            analysis["key_points"].append("Strong weekly uptrend (+{:.1f}%)".format(tech_data.price_change_5d))
            buy_signals += 0.5
            total_signals += 1
        elif tech_data.price_change_5d < -5:
            analysis["key_points"].append("Strong weekly downtrend ({:.1f}%)".format(tech_data.price_change_5d))
            sell_signals += 0.5
            total_signals += 1
        
        # Calculate recommendation based on signal strength
        if total_signals > 0:
            buy_ratio = buy_signals / total_signals
            sell_ratio = sell_signals / total_signals
            
            # Determine recommendation
            if buy_ratio > 0.6:
                analysis["recommendation"] = "BUY"
                if buy_ratio > 0.8:
                    analysis["confidence"] = "HIGH"
                else:
                    analysis["confidence"] = "MEDIUM"
            elif sell_ratio > 0.6:
                analysis["recommendation"] = "SELL"
                if sell_ratio > 0.8:
                    analysis["confidence"] = "HIGH"
                else:
                    analysis["confidence"] = "MEDIUM"
            else:
                analysis["recommendation"] = "HOLD"
                if abs(buy_ratio - sell_ratio) < 0.2:
                    analysis["confidence"] = "LOW"
                else:
                    analysis["confidence"] = "MEDIUM"
        
        # Create summary
        analysis["summary"] = f"Technical analysis for {tech_data.symbol}: {len(analysis['key_points'])} indicators analyzed. Signal strength: {buy_signals:.1f} buy vs {sell_signals:.1f} sell signals."
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in rule-based analysis: {e}", exc_info=True)
        return {
            "summary": "Analysis failed",
            "recommendation": "HOLD",
            "confidence": "LOW",
            "key_points": ["Unable to complete analysis"]
        }

@router.post("/analyze", response_model=AnalysisResponse)
@limiter.limit("3/minute")
async def analyze_stock(
    request: Request,
    stock_request: StockAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze a stock using technical indicators and AI"""
    try:
        logger.info(f"Stock analysis requested for {stock_request.symbol} by user {current_user.email}")
        
        # Check if we have cached data first
        cached_analysis = stock_cache_service.get_cached_analysis(current_user.id, stock_request.symbol)
        if cached_analysis:
            logger.info(f"Using cached analysis for {request.symbol} for user {current_user.email}")
            
            # Filter the cached data to return only the requested analysis type
            filtered_data = filter_analysis_by_type(cached_analysis, stock_request.analysis_type)
            
            # Get search status without incrementing (since we're using cache)
            search_status = await SearchLimitService.get_user_search_status(current_user, db)
            
            return AnalysisResponse(
                success=True,
                data=filtered_data,
                search_limit_info=search_status
            )
        
        # Check search limit before proceeding with new analysis
        can_search, message, remaining = await SearchLimitService.check_and_increment_search_count(current_user, db)
        
        if not can_search:
            logger.warning(f"User {current_user.email} exceeded daily search limit")
            return AnalysisResponse(
                success=False,
                error=message,
                search_limit_info=await SearchLimitService.get_user_search_status(current_user, db)
            )
        
        # Get technical analysis
        tech_data = get_technical_analysis(stock_request.symbol, current_user)
        
        # Always prepare full analysis data (both technical and AI)
        full_response_data = {
            "symbol": tech_data.symbol,
            "technical_data": tech_data.dict(),
            "analysis_type": "both"
        }
        
        # Add AI analysis if available
        if client:
            try:
                ai_analysis = await get_ai_analysis(tech_data)
                full_response_data["ai_analysis"] = ai_analysis
            except Exception as e:
                logger.warning(f"AI analysis failed for {stock_request.symbol}: {e}")
                full_response_data["ai_analysis"] = {"error": "AI analysis unavailable"}
        
        # Add rule-based analysis
        rule_analysis = get_rule_based_analysis(tech_data)
        full_response_data["rule_analysis"] = rule_analysis
        
        # Store the full analysis in cache
        stock_cache_service.store_stock_analysis(current_user.id, stock_request.symbol, full_response_data)
        
        # Filter the response to return only the requested analysis type
        response_data = filter_analysis_by_type(full_response_data, stock_request.analysis_type)
        
        # Get updated search status
        search_status = await SearchLimitService.get_user_search_status(current_user, db)
        
        logger.info(f"Analysis completed successfully for {stock_request.symbol}. User has {remaining} searches remaining.")
        
        return AnalysisResponse(
            success=True,
            data=response_data,
            search_limit_info=search_status
        )
        
    except ValueError as e:
        logger.warning(f"Invalid request for {stock_request.symbol}: {e}")
        return AnalysisResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        logger.error(f"Analysis failed for {stock_request.symbol}: {e}", exc_info=True)
        return AnalysisResponse(
            success=False,
            error="Internal server error"
        )

@router.get("/search-status")
@limiter.limit("20/minute")
async def get_search_status(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's current search status and limits"""
    try:
        search_status = await SearchLimitService.get_user_search_status(current_user, db)
        return search_status
    except Exception as e:
        logger.error(f"Error getting search status for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error getting search status")

@router.get("/todays-searches")
@limiter.limit("20/minute")
async def get_todays_searches(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get today's searches for the current user"""
    try:
        searches = stock_cache_service.get_todays_searches_with_data(current_user.id)
        
        # Format the response to include basic info for list view
        formatted_searches = []
        for search in searches:
            analysis_data = search.get("analysis_data", {})
            technical_data = analysis_data.get("technical_data", {})
            
            # Extract basic info for list view
            basic_info = {
                "symbol": search["symbol"],
                "timestamp": search["timestamp"],
                "current_price": technical_data.get("current_price", 0),
                "confidence_level": technical_data.get("recommendation", "HOLD"),
                "price_change_1d": technical_data.get("price_change_1d", 0),
                "currency": technical_data.get("currency", "USD")
            }
            
            formatted_searches.append(basic_info)
        
        return {
            "success": True,
            "data": formatted_searches,
            "count": len(formatted_searches)
        }
        
    except Exception as e:
        logger.error(f"Failed to get today's searches for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get today's searches")

@router.get("/todays-searches/{symbol}")
@limiter.limit("20/minute")
async def get_todays_search_detail(
    request: Request,
    symbol: str,
    analysis_type: str = "technical",
    current_user: User = Depends(get_current_user)
):
    """Get detailed analysis for a specific stock from today's searches"""
    try:
        cached_analysis = stock_cache_service.get_cached_analysis(current_user.id, symbol)
        
        if not cached_analysis:
            raise HTTPException(status_code=404, detail="Stock not found in today's searches")
        
        # Filter the cached data to return only the requested analysis type
        filtered_data = filter_analysis_by_type(cached_analysis, analysis_type)
        
        return {
            "success": True,
            "data": filtered_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get search detail for user {current_user.id}, symbol {symbol}, type {analysis_type}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get search detail")

@router.get("/health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    """Health check for search service"""
    try:
        return {
            "status": "healthy",
            "service": "stock-analysis",
            "openai_available": client is not None
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Service unhealthy") 