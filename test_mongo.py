#!/usr/bin/env python3
"""
Simple MongoDB connection test
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def test_mongo():
    MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    DB_NAME = os.environ.get("DB_NAME", "trust_lens_db")
    
    print(f"Connecting to: {MONGO_URL}")
    print(f"Database: {DB_NAME}")
    
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Test connection
        await client.admin.command('ismaster')
        print("✅ MongoDB connection successful")
        
        # Test collections
        products_collection = db["products"]
        reviews_collection = db["reviews"]
        
        # Count documents
        product_count = await products_collection.count_documents({})
        review_count = await reviews_collection.count_documents({})
        
        print(f"Products in DB: {product_count}")
        print(f"Reviews in DB: {review_count}")
        
        # Test find operation
        cursor = products_collection.find().limit(1)
        products = await cursor.to_list(length=1)
        print(f"Sample product: {products}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ MongoDB error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mongo())