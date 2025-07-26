# Stock AI - AI-Powered Stock Analysis Platform

A modern, dockerized stock analysis application that provides AI-powered technical analysis and trading recommendations using Zerodha API integration.

## Features

- 🔐 **Authentication**: Email/password and Zerodha OAuth login
- 📊 **AI Analysis**: OpenAI-powered stock analysis with technical indicators
- 📈 **Technical Indicators**: RSI, MACD, SMA, Support/Resistance levels
- 🐳 **Dockerized**: Complete containerized setup with PostgreSQL and Redis
- 🎨 **Modern UI**: Beautiful, responsive frontend built with Next.js and Tailwind CSS
- 🔄 **Real-time**: WebSocket support for real-time updates
- 📱 **Responsive**: Mobile-friendly interface

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM with async support
- **PostgreSQL**: Primary database
- **Redis**: Caching and message broker
- **Alembic**: Database migrations
- **Zerodha API**: Stock data integration
- **OpenAI API**: AI-powered analysis

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **Axios**: HTTP client

## Prerequisites

- Docker and Docker Compose
- Zerodha API credentials
- OpenAI API key (optional, for AI analysis)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stock-ai
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file with your credentials:
   - `ZERODHA_API_KEY`: Your Zerodha API key
   - `ZERODHA_API_SECRET`: Your Zerodha API secret
   - `ZERODHA_REDIRECT_URL`: Your OAuth redirect URL
   - `OPENAI_API_KEY`: Your OpenAI API key (optional)
   - `FERNET_KEY`: Generate a 32-byte key for encryption
   - `JWT_SECRET`: Generate a secure JWT secret (min 32 chars)

3. **Generate required keys**
   ```bash
   # Generate Fernet key
   python -c "import base64; print(base64.b64encode(b'your-32-byte-key-here').decode())"
   
   # Generate JWT secret (at least 32 characters)
   openssl rand -base64 32
   ```

4. **Start the application**
   ```bash
   docker-compose up -d
   ```

5. **Run database migrations**
   ```bash
   # Check database connection
   python backend/scripts/migrate.py check
   
   # Run migrations
   python backend/scripts/migrate.py migrate
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `JWT_SECRET` | Secret key for JWT tokens (min 32 chars) | Yes |
| `ZERODHA_API_KEY` | Zerodha API key | Yes |
| `ZERODHA_API_SECRET` | Zerodha API secret | Yes |
| `ZERODHA_REDIRECT_URL` | OAuth redirect URL | Yes |
| `OPENAI_API_KEY` | OpenAI API key | No |
| `FERNET_KEY` | Encryption key (base64 encoded) | Yes |
| `FRONTEND_URL` | Frontend URL | Yes |

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Email/password login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/login/zerodha` - Get Zerodha OAuth URL
- `GET /api/v1/auth/callback/zerodha` - Zerodha OAuth callback
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info

### Stock Analysis
- `POST /api/v1/search/analyze` - Analyze stock with AI
- `GET /api/v1/search/health` - Health check

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations
```bash
# Check migration status
python backend/scripts/migrate.py status

# Create new migration
python backend/scripts/migrate.py create "Description"

# Run migrations
python backend/scripts/migrate.py migrate

# Reset database (WARNING: deletes all data)
python backend/scripts/migrate.py reset
```

## Docker Services

The application consists of the following services:

- **postgres**: PostgreSQL database
- **redis**: Redis cache and message broker
- **backend**: FastAPI application
- **frontend**: Next.js application

## Project Structure

```
stock-ai/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/     # API routes
│   │   ├── core/              # Configuration, auth, security
│   │   ├── db/                # Database session
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── main.py           # FastAPI app
│   ├── alembic/              # Database migrations
│   ├── scripts/              # Utility scripts
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js app router
│   │   ├── components/       # React components
│   │   ├── services/         # API services
│   │   └── types/            # TypeScript types
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Troubleshooting

### Common Issues

1. **Database connection failed**
   - Ensure PostgreSQL container is running
   - Check database credentials in `.env`
   - Run `python backend/scripts/migrate.py check`

2. **Zerodha API errors**
   - Verify API credentials
   - Check redirect URL configuration

3. **Frontend not loading**
   - Ensure backend is running on port 8000
   - Check CORS configuration

4. **Docker build failures**
   - Clear Docker cache: `docker system prune -a`
   - Rebuild: `docker-compose build --no-cache`

5. **Migration errors**
   - Check database connection: `python backend/scripts/migrate.py check`
   - Reset database if needed: `python backend/scripts/migrate.py reset`

### Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
```

## Security Features

- ✅ Environment variable validation
- ✅ Secure JWT token handling
- ✅ Password hashing with bcrypt
- ✅ CORS configuration
- ✅ Input validation with Pydantic
- ✅ Error handling and logging
- ✅ Database migration management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please open an issue on GitHub or contact the development team. 