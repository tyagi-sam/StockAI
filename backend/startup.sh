#!/bin/bash

echo "🚀 Starting Stock AI Backend..."

# Wait for database to be ready with timeout
echo "⏳ Waiting for database to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    # Try a simple connection test
    if python3 -c "
import asyncio
import asyncpg
import os
import sys

async def check_db():
    try:
        # Use a simple connection test
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        await conn.execute('SELECT 1')
        await conn.close()
        return True
    except Exception as e:
        print(f'Connection failed: {str(e)}', file=sys.stderr)
        return False

try:
    if asyncio.run(check_db()):
        print('Database is ready!')
        exit(0)
    else:
        print('Database not ready yet...')
        exit(1)
except Exception as e:
    print(f'Check failed: {str(e)}', file=sys.stderr)
    exit(1)
" 2>/dev/null; then
        echo "✅ Database is ready!"
        break
    else
        attempt=$((attempt + 1))
        echo "Database not ready, waiting... (attempt $attempt/$max_attempts)"
        sleep 3
    fi
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Database connection timeout after $max_attempts attempts"
    echo "🔍 Debugging info:"
    echo "DATABASE_URL: $DATABASE_URL"
    echo "PostgreSQL container status:"
    docker ps | grep postgres || echo "No PostgreSQL container found"
    echo "Trying to connect manually..."
    python3 -c "
import asyncio
import asyncpg
import os
print('DATABASE_URL:', os.getenv('DATABASE_URL'))
async def test():
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        print('Manual connection successful!')
        await conn.close()
    except Exception as e:
        print('Manual connection failed:', e)
asyncio.run(test())
"
    exit 1
fi

# Run migrations
echo "🔄 Running database migrations..."
if python3 -m alembic upgrade head; then
    echo "✅ Migrations completed successfully!"
else
    echo "❌ Migration failed!"
    exit 1
fi

# Start the application
echo "🚀 Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 