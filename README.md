# StockAI - AI-Powered Stock Analysis

A modern web application that provides AI-powered stock analysis with technical indicators, built with FastAPI backend and React frontend.

## 🚀 Features

- **AI-Powered Analysis**: Get intelligent stock insights using OpenAI
- **Technical Indicators**: RSI, MACD, Moving Averages, Support/Resistance levels
- **Daily Search Limits**: 10 searches per day per user
- **Secure Authentication**: Email/password and Google OAuth
- **Email Verification**: OTP-based email verification
- **Beautiful UI**: Modern, responsive design with Tailwind CSS
- **Real-time Data**: Live stock data from yfinance
- **Currency Support**: Automatic INR/USD detection for Indian/International stocks

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Primary database
- **Redis**: OTP storage and caching
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations
- **JWT**: Authentication tokens
- **yfinance**: Stock data provider
- **TA-Lib**: Technical analysis library
- **OpenAI**: AI analysis

### Frontend
- **React**: Modern JavaScript framework
- **Vite**: Fast build tool and dev server
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **React Markdown**: Markdown rendering for AI analysis

## 📁 Project Structure

```
stock-ai/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   ├── alembic/            # Database migrations
│   └── requirements.txt    # Python dependencies
├── frontend-react/         # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── types/          # TypeScript types
│   └── package.json        # Node.js dependencies
├── env/                    # Python virtual environment
├── .env                    # Environment variables
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL
- Redis

### 1. Clone and Setup
```bash
git clone <repository-url>
cd stock-ai
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Set up environment variables
cp ../env.example ../.env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
# Install dependencies
cd frontend-react
npm install

# Start development server
npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/stock_ai
POSTGRES_PASSWORD=your_postgres_password

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# Security
JWT_SECRET=your_jwt_secret_key_here_make_it_at_least_32_characters_long
FERNET_KEY=your_fernet_key_here_base64_encoded_32_byte_key

# Google OAuth
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret

# Zerodha API
ZERODHA_API_KEY=your_zerodha_api_key
ZERODHA_API_SECRET=your_zerodha_api_secret

# OpenAI API (Optional)
OPENAI_API_KEY=your_openai_api_key

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_email_app_password
SMTP_TLS=true
SMTP_SSL=false
FROM_EMAIL=noreply@stockai.com
FROM_NAME=StockAI

# OTP Configuration
OTP_EXPIRE_MINUTES=10
OTP_LENGTH=6

# Environment
ENVIRONMENT=development

# CORS Origins
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://frontend:3000

# Frontend URL
FRONTEND_URL=http://localhost:3000

# WebSocket URL
WS_URL=ws://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## 🔐 Security Features

- **Password Hashing**: bcrypt with salt
- **OTP Security**: SHA256 hashed OTPs with unique salts
- **JWT Tokens**: Secure authentication
- **CORS Protection**: Configured for development/production
- **Rate Limiting**: Daily search limits per user
- **Input Validation**: Pydantic models for data validation

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - Email/password login
- `GET /api/v1/auth/login/google` - Google OAuth URL
- `POST /api/v1/auth/callback/google` - Google OAuth callback
- `POST /api/v1/auth/verify-email` - Email verification
- `POST /api/v1/auth/resend-otp` - Resend OTP
- `GET /api/v1/auth/me` - Get current user

### Stock Analysis
- `POST /api/v1/search/analyze` - Analyze stock
- `GET /api/v1/search/search-status` - Get search limits
- `GET /api/v1/search/health` - Health check

## 🎨 Frontend Features

- **Modern UI**: Clean, responsive design
- **Authentication Flow**: Login, registration, email verification
- **Stock Analysis**: Beautiful charts and indicators
- **Search Limits**: Visual progress tracking
- **Error Handling**: User-friendly error messages
- **Loading States**: Smooth loading animations
- **Mobile Responsive**: Works on all devices

## 🚀 Deployment

### Backend Deployment
```bash
# Build Docker image
docker build -t stock-ai-backend ./backend

# Run with Docker Compose
docker-compose up -d
```

### Frontend Deployment
```bash
# Build for production
cd frontend-react
npm run build

# Deploy to your preferred hosting service
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support, email support@stockai.com or create an issue in the repository. 