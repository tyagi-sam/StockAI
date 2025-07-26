from kiteconnect import KiteConnect
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import json
import requests

from ..core.config import settings
from ..core.logger import logger
from ..models.trade import Trade, TradeSide, TradeStatus
from ..core.security import decrypt_sensitive_data

class ZerodhaService:
    def __init__(self, api_key: str = settings.ZERODHA_API_KEY):
        logger.info(f"Initializing Zerodha service with API key: {api_key}")
        self.kite = KiteConnect(api_key=api_key)
        # Note: We're using public market data APIs that don't require user authentication
        
    def set_access_token(self, access_token: str):
        """Set the access token for API calls (for user-specific data)"""
        # Check if the token is encrypted (Fernet tokens start with specific pattern)
        if access_token and access_token.startswith('gAAAAA'):
            try:
                access_token = decrypt_sensitive_data(access_token)
                logger.debug("Successfully decrypted access token")
            except Exception as e:
                logger.error(f"Failed to decrypt access token: {str(e)}", exc_info=True)
                # If decryption fails, assume it's a plain token and continue
                logger.warning("Assuming token is plain text and continuing...")
        
        logger.debug(f"Setting access token: {access_token[:10]}...")
        self.kite.set_access_token(access_token)
    
    def get_login_url(self) -> str:
        """Get the Zerodha login URL for OAuth (deprecated - using Google OAuth instead)"""
        logger.warning("Zerodha OAuth is deprecated. Using Google OAuth for user authentication.")
        raise NotImplementedError("Zerodha OAuth is deprecated. Use Google OAuth instead.")
    
    def generate_session(self, request_token: str) -> Dict:
        """Generate session from the request token (deprecated)"""
        logger.warning("Zerodha OAuth is deprecated. Using Google OAuth for user authentication.")
        raise NotImplementedError("Zerodha OAuth is deprecated. Use Google OAuth instead.")
    
    def exchange_token(self, request_token: str) -> Dict:
        """Exchange request token for access token (deprecated)"""
        logger.warning("Zerodha OAuth is deprecated. Using Google OAuth for user authentication.")
        raise NotImplementedError("Zerodha OAuth is deprecated. Use Google OAuth instead.")
    
    def get_user_profile(self) -> Dict:
        """Get user profile information (requires authentication)"""
        logger.debug("Fetching user profile")
        try:
            profile = self.kite.profile()
            logger.info(f"Retrieved profile for user: {profile.get('user_name')}")
            return profile
        except Exception as e:
            logger.error("Failed to fetch user profile", exc_info=True)
            raise
    
    def get_positions(self) -> List[Dict]:
        """Get current positions (requires authentication)"""
        logger.debug("Fetching positions")
        try:
            positions = self.kite.positions()["net"]
            logger.info(f"Retrieved {len(positions)} positions")
            return positions
        except Exception as e:
            logger.error("Failed to fetch positions", exc_info=True)
            raise
    
    def get_orders(self) -> List[Dict]:
        """Get today's orders (requires authentication)"""
        logger.debug("Fetching orders")
        try:
            orders = self.kite.orders()
            logger.info(f"Retrieved {len(orders)} orders")
            return orders
        except Exception as e:
            logger.error("Failed to fetch orders", exc_info=True)
            raise
    
    def get_trades(self) -> List[Dict]:
        """Get today's trades (requires authentication)"""
        logger.debug("Fetching trades")
        try:
            trades = self.kite.trades()
            logger.info(f"Retrieved {len(trades)} trades")
            return trades
        except Exception as e:
            logger.error("Failed to fetch trades", exc_info=True)
            raise
    
    def parse_trade(self, order_data: Dict) -> Optional[Trade]:
        """Parse order data into Trade model"""
        try:
            return Trade(
                id=order_data.get("order_id"),
                symbol=order_data.get("tradingsymbol"),
                side=TradeSide.BUY if order_data.get("transaction_type") == "BUY" else TradeSide.SELL,
                quantity=order_data.get("quantity", 0),
                price=order_data.get("price", 0),
                status=TradeStatus.COMPLETE if order_data.get("status") == "COMPLETE" else TradeStatus.PENDING,
                timestamp=datetime.fromisoformat(order_data.get("order_timestamp", "").replace("Z", "+00:00")) if order_data.get("order_timestamp") else datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to parse trade: {str(e)}", exc_info=True)
            return None
    
    def calculate_pnl(self, trades: List[Trade]) -> float:
        """Calculate total P&L from trades"""
        total_pnl = 0.0
        for trade in trades:
            if trade.side == TradeSide.BUY:
                total_pnl -= trade.quantity * trade.price
            else:
                total_pnl += trade.quantity * trade.price
        return total_pnl
    
    def get_holdings(self) -> List[Dict]:
        """Get current holdings (requires authentication)"""
        logger.debug("Fetching holdings")
        try:
            holdings = self.kite.holdings()
            logger.info(f"Retrieved {len(holdings)} holdings")
            return holdings
        except Exception as e:
            logger.error("Failed to fetch holdings", exc_info=True)
            raise
    
    def get_instruments(self, exchange: str = "NSE") -> List[Dict]:
        """Get instruments for an exchange (public data)"""
        logger.debug(f"Fetching instruments for exchange: {exchange}")
        try:
            instruments = self.kite.instruments(exchange)
            logger.info(f"Retrieved {len(instruments)} instruments for {exchange}")
            return instruments
        except Exception as e:
            logger.error(f"Failed to fetch instruments for {exchange}", exc_info=True)
            raise
    
    def get_historical_data(self, instrument_token: int, from_date: str, to_date: str, interval: str = "day") -> List[Dict]:
        """Get historical data for an instrument (public data)"""
        logger.debug(f"Fetching historical data for token {instrument_token} from {from_date} to {to_date}")
        try:
            data = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
            logger.info(f"Retrieved {len(data)} historical data points")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch historical data: {str(e)}", exc_info=True)
            raise
    
    def search_instrument(self, symbol: str, exchange: str = "NSE") -> Optional[Dict]:
        """Search for an instrument by symbol (public data)"""
        logger.debug(f"Searching for instrument: {symbol} on {exchange}")
        try:
            instruments = self.get_instruments(exchange)
            for instrument in instruments:
                if instrument.get("tradingsymbol", "").upper() == symbol.upper():
                    logger.info(f"Found instrument: {instrument.get('tradingsymbol')}")
                    return instrument
            logger.warning(f"Instrument not found: {symbol} on {exchange}")
            return None
        except Exception as e:
            logger.error(f"Failed to search instrument: {str(e)}", exc_info=True)
            raise
    
    def get_stock_data(self, symbol: str, days: int = 90) -> Optional[List[Dict]]:
        """Get stock data for a symbol (public data)"""
        logger.debug(f"Fetching stock data for {symbol} for {days} days")
        try:
            # Search for the instrument
            instrument = self.search_instrument(symbol)
            if not instrument:
                logger.warning(f"Instrument not found for symbol: {symbol}")
                return None
            
            # Calculate date range
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            to_date = datetime.now().strftime("%Y-%m-%d")
            
            # Get historical data
            data = self.get_historical_data(
                instrument_token=instrument["instrument_token"],
                from_date=from_date,
                to_date=to_date,
                interval="day"
            )
            
            logger.info(f"Retrieved {len(data)} data points for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to get stock data for {symbol}: {str(e)}", exc_info=True)
            raise

# Create a singleton instance for stock data fetching
# Note: This service is now only used for fetching public stock data, not for user authentication
zerodha_service = ZerodhaService() 