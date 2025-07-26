from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict
from datetime import datetime
import talib
import numpy as np
from openai import OpenAI
import os
import json
from pydantic import BaseModel
import yfinance as yf

from ...db.session import get_db
from ...core.config import settings
# Removed Zerodha service import - using yfinance instead
from ...core.auth import get_current_user
from ...models.user import User
from ...core.logger import logger

router = APIRouter()

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
    """Get stock data using yfinance with support for Indian stocks"""
    try:
        logger.info(f"Using yfinance for {symbol}")
        
        # Try different symbol formats for Indian stocks
        symbol_variants = [
            symbol,  # Original symbol
            f"{symbol}.NS",  # NSE format
            f"{symbol}.BO",  # BSE format
            f"{symbol}.NSE",  # Alternative NSE format
        ]
        
        for variant in symbol_variants:
            try:
                logger.debug(f"Trying yfinance with symbol: {variant}")
                ticker = yf.Ticker(variant)
                hist = ticker.history(period=f"{days}d")
                
                if not hist.empty:
                    data = []
                    for date, row in hist.iterrows():
                        data.append({
                            "date": date.strftime("%Y-%m-%d"),
                            "open": float(row["Open"]),
                            "high": float(row["High"]),
                            "low": float(row["Low"]),
                            "close": float(row["Close"]),
                            "volume": int(row["Volume"])
                        })
                    
                    logger.info(f"Retrieved {len(data)} data points using yfinance for {variant}")
                    return data
            except Exception as e:
                logger.debug(f"Failed with symbol {variant}: {str(e)}")
                continue
        
        logger.error(f"All symbol variants failed for {symbol}")
        return None
        
    except Exception as e:
        logger.error(f"yfinance failed for {symbol}: {str(e)}")
        return None

class StockAnalysisRequest(BaseModel):
    symbol: str
    analysis_type: str = "technical"  # technical, ai, or both

class TechnicalData(BaseModel):
    symbol: str
    current_price: float
    rsi: float
    macd: float
    macd_signal: float
    sma_20: float
    sma_50: float
    volume: int
    volume_sma_20: float
    volume_ratio: float
    price_change_5d: float
    price_change_1d: float
    support_levels: list
    resistance_levels: list
    pivot_points: dict

class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

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
        
        # Calculate technical indicators
        rsi = talib.RSI(close_prices)[-1]
        macd, macd_signal, _ = talib.MACD(close_prices)
        sma_20 = talib.SMA(close_prices, timeperiod=20)[-1]
        sma_50 = talib.SMA(close_prices, timeperiod=50)[-1]
        
        # Calculate support and resistance
        support_levels, resistance_levels, pivot_points = calculate_support_resistance(high_prices, low_prices, close_prices)
        
        # Calculate volume analysis
        volume_sma_20, volume_ratio = calculate_volume_analysis(volumes, close_prices)
        
        # Calculate price changes
        current_price = close_prices[-1]
        price_change_1d = ((current_price - close_prices[-2]) / close_prices[-2]) * 100 if len(close_prices) > 1 else 0
        price_change_5d = ((current_price - close_prices[-6]) / close_prices[-6]) * 100 if len(close_prices) > 5 else 0
        
        return TechnicalData(
            symbol=symbol.upper(),
            current_price=current_price,
            rsi=rsi,
            macd=macd[-1],
            macd_signal=macd_signal[-1],
            sma_20=sma_20,
            sma_50=sma_50,
            volume=volumes[-1],
            volume_sma_20=volume_sma_20,
            volume_ratio=volume_ratio,
            price_change_5d=price_change_5d,
            price_change_1d=price_change_1d,
            support_levels=support_levels,
            resistance_levels=resistance_levels,
            pivot_points=pivot_points
        )
        
    except Exception as e:
        logger.error(f"Error getting technical analysis for {symbol}: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to analyze {symbol}: {str(e)}")

def create_analysis_prompt(tech_data: TechnicalData) -> str:
    """Create a prompt for AI analysis"""
    prompt = f"""
    Analyze the following stock data for {tech_data.symbol}:
    
    Current Price: ${tech_data.current_price:.2f}
    RSI: {tech_data.rsi:.2f}
    MACD: {tech_data.macd:.2f}
    MACD Signal: {tech_data.macd_signal:.2f}
    20-day SMA: ${tech_data.sma_20:.2f}
    50-day SMA: ${tech_data.sma_50:.2f}
    1-day Change: {tech_data.price_change_1d:.2f}%
    5-day Change: {tech_data.price_change_5d:.2f}%
    Volume Ratio: {tech_data.volume_ratio:.2f}
    
    Support Levels: {tech_data.support_levels}
    Resistance Levels: {tech_data.resistance_levels}
    Pivot Points: {tech_data.pivot_points}
    
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

def get_rule_based_analysis(tech_data: TechnicalData) -> dict:
    """Perform rule-based analysis using technical indicators"""
    try:
        analysis = {
            "summary": "",
            "recommendation": "HOLD",
            "confidence": "MEDIUM",
            "key_points": []
        }
    
        # RSI analysis
        if tech_data.rsi > 70:
            analysis["key_points"].append("RSI indicates overbought conditions")
            analysis["recommendation"] = "SELL"
        elif tech_data.rsi < 30:
            analysis["key_points"].append("RSI indicates oversold conditions")
            analysis["recommendation"] = "BUY"
    
        # MACD analysis
        if tech_data.macd > tech_data.macd_signal:
            analysis["key_points"].append("MACD is bullish (above signal line)")
        else:
            analysis["key_points"].append("MACD is bearish (below signal line)")
    
        # Moving average analysis
        if tech_data.current_price > tech_data.sma_20 > tech_data.sma_50:
            analysis["key_points"].append("Price above both moving averages - bullish trend")
        elif tech_data.current_price < tech_data.sma_20 < tech_data.sma_50:
            analysis["key_points"].append("Price below both moving averages - bearish trend")
    
        # Volume analysis
        if tech_data.volume_ratio > 1.5:
            analysis["key_points"].append("High volume indicates strong interest")
        elif tech_data.volume_ratio < 0.5:
            analysis["key_points"].append("Low volume indicates weak interest")
    
        # Price change analysis
        if tech_data.price_change_1d > 2:
            analysis["key_points"].append("Strong positive momentum")
        elif tech_data.price_change_1d < -2:
            analysis["key_points"].append("Strong negative momentum")
    
        # Create summary
        analysis["summary"] = f"Technical analysis for {tech_data.symbol}: {len(analysis['key_points'])} key indicators analyzed."
        
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
async def analyze_stock(
    request: StockAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze a stock using technical indicators and AI"""
    try:
        logger.info(f"Stock analysis requested for {request.symbol} by user {current_user.email}")
        
        # Get technical analysis
        tech_data = get_technical_analysis(request.symbol, current_user)
        
        # Prepare response data
        response_data = {
            "symbol": tech_data.symbol,
            "technical_data": tech_data.dict(),
            "analysis_type": request.analysis_type
        }
        
        # Add AI analysis if requested and available
        if request.analysis_type in ["ai", "both"] and client:
            try:
                ai_analysis = await get_ai_analysis(tech_data)
                response_data["ai_analysis"] = ai_analysis
            except Exception as e:
                logger.warning(f"AI analysis failed for {request.symbol}: {e}")
                response_data["ai_analysis"] = {"error": "AI analysis unavailable"}
        
        # Add rule-based analysis as fallback
        if request.analysis_type in ["technical", "both"] or not client:
            rule_analysis = get_rule_based_analysis(tech_data)
            response_data["rule_analysis"] = rule_analysis
        
        logger.info(f"Analysis completed successfully for {request.symbol}")
        
        return AnalysisResponse(
            success=True,
            data=response_data
        )
        
    except ValueError as e:
        logger.warning(f"Invalid request for {request.symbol}: {e}")
        return AnalysisResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        logger.error(f"Analysis failed for {request.symbol}: {e}", exc_info=True)
        return AnalysisResponse(
            success=False,
            error="Internal server error"
        )

@router.get("/health")
async def health_check():
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