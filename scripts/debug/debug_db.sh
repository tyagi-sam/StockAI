#!/bin/bash

echo "🔍 Database Connection Diagnostic"
echo "================================"

echo "1. Checking PostgreSQL container status..."
docker ps | grep postgres

echo ""
echo "2. Checking PostgreSQL logs..."
docker logs $(docker ps -q --filter "name=postgres") --tail 10

echo ""
echo "3. Checking backend container status..."
docker ps | grep backend

echo ""
echo "4. Checking DATABASE_URL in backend container..."
docker exec stock_ai_backend env | grep DATABASE_URL

echo ""
echo "5. Testing network connectivity..."
docker exec stock_ai_backend ping -c 3 postgres

echo ""
echo "6. Testing direct database connection..."
docker exec stock_ai_backend python3 -c "
import asyncio
import asyncpg
import os

async def test_connection():
    url = os.getenv('DATABASE_URL')
    print(f'DATABASE_URL: {url}')
    
    try:
        conn = await asyncpg.connect(url)
        print('✅ Connection successful!')
        
        # Test a simple query
        result = await conn.fetchval('SELECT 1')
        print(f'✅ Query test successful: {result}')
        
        await conn.close()
        return True
    except Exception as e:
        print(f'❌ Connection failed: {e}')
        return False

asyncio.run(test_connection())
"

echo ""
echo "7. Checking if database exists..."
docker exec $(docker ps -q --filter "name=postgres") psql -U stock_ai_user -d stock_ai -c "\l" 2>/dev/null || echo "❌ Cannot connect to database"

echo ""
echo "8. Checking Docker networks..."
docker network ls | grep stock_ai 