#!/bin/bash

echo "🚀 Starting Stock AI Backend..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
until python3 -c "
import asyncio
import asyncpg
import os

async def check_db():
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        await conn.close()
        return True
    except:
        return False

if asyncio.run(check_db()):
    print('Database is ready!')
    exit(0)
else:
    print('Database not ready yet...')
    exit(1)
" 2>/dev/null; do
    echo "Database not ready, waiting..."
    sleep 2
done

echo "✅ Database is ready!"

# Run migrations
echo "🔄 Running database migrations..."
python3 -m alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully!"
else
    echo "❌ Migration failed!"
    exit 1
fi

# Start the application
echo "🚀 Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 