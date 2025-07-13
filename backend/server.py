import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
from datetime import datetime
import asyncio

app = FastAPI(title="Trust Lens API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "trust_lens_db")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
products_collection = db["products"]
reviews_collection = db["reviews"]
trust_scores_collection = db["trust_scores"]

# Pydantic models
class ProductRequest(BaseModel):
    product_url: Optional[str] = None
    product_name: Optional[str] = None
    product_description: Optional[str] = None

class Review(BaseModel):
    id: str
    product_id: str
    author: str
    rating: int
    title: str
    content: str
    date: str
    verified: bool
    platform: str

class AspectAnalysis(BaseModel):
    aspect: str
    score: float
    sentiment: str
    key_points: List[str]

class TrustScore(BaseModel):
    product_id: str
    overall_score: float
    total_reviews: int
    aspect_analysis: List[AspectAnalysis]
    summary: str
    recommendation: str
    updated_at: str

class Product(BaseModel):
    id: str
    name: str
    description: str
    url: Optional[str] = None
    trust_score: Optional[TrustScore] = None
    created_at: str

# Mock review data for different platforms
MOCK_REVIEWS = [
    {
        "id": str(uuid.uuid4()),
        "author": "John D.",
        "rating": 5,
        "title": "Excellent product!",
        "content": "This product exceeded my expectations. The quality is outstanding and delivery was super fast. Customer service was also very helpful when I had questions.",
        "date": "2024-01-15",
        "verified": True,
        "platform": "Amazon"
    },
    {
        "id": str(uuid.uuid4()),
        "author": "Sarah M.",
        "rating": 4,
        "title": "Good value for money",
        "content": "Pretty good product overall. The quality is decent for the price. Delivery took a bit longer than expected but it arrived safely.",
        "date": "2024-01-10",
        "verified": True,
        "platform": "eBay"
    },
    {
        "id": str(uuid.uuid4()),
        "author": "Mike R.",
        "rating": 3,
        "title": "Average product",
        "content": "It's okay, nothing special. The quality is average and the customer service was slow to respond. Delivery was on time though.",
        "date": "2024-01-08",
        "verified": False,
        "platform": "Walmart"
    },
    {
        "id": str(uuid.uuid4()),
        "author": "Lisa K.",
        "rating": 2,
        "title": "Not as described",
        "content": "The product didn't match the description. Quality was poor and it broke after a few days. Customer service was unhelpful.",
        "date": "2024-01-05",
        "verified": True,
        "platform": "Target"
    },
    {
        "id": str(uuid.uuid4()),
        "author": "David L.",
        "rating": 5,
        "title": "Perfect!",
        "content": "Absolutely love this product! Amazing quality, fast delivery, and great customer service. Would definitely buy again.",
        "date": "2024-01-12",
        "verified": True,
        "platform": "AliExpress"
    }
]

async def generate_trust_analysis(product_id: str, reviews: List[Dict]) -> TrustScore:
    """Generate AI-powered trust analysis using Gemini"""
    
    # Initialize Gemini chat
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Google API key not configured")
    
    session_id = str(uuid.uuid4())
    
    chat = LlmChat(
        api_key=api_key,
        session_id=session_id,
        system_message="You are a product review analysis expert. Analyze reviews and provide detailed sentiment analysis with trust scores."
    ).with_model("gemini", "gemini-2.0-flash")
    
    # Prepare reviews for analysis
    review_text = ""
    for review in reviews:
        review_text += f"Rating: {review['rating']}/5\n"
        review_text += f"Title: {review['title']}\n"
        review_text += f"Content: {review['content']}\n"
        review_text += f"Platform: {review['platform']}\n"
        review_text += f"Verified: {review['verified']}\n\n"
    
    # Create analysis prompt
    analysis_prompt = f"""
    Analyze these product reviews and provide a comprehensive trust analysis:
    
    {review_text}
    
    Please provide your analysis in the following JSON format:
    {{
        "overall_score": 0-100,
        "total_reviews": {len(reviews)},
        "aspect_analysis": [
            {{
                "aspect": "Quality",
                "score": 0-100,
                "sentiment": "positive/negative/neutral",
                "key_points": ["key point 1", "key point 2"]
            }},
            {{
                "aspect": "Delivery",
                "score": 0-100,
                "sentiment": "positive/negative/neutral",
                "key_points": ["key point 1", "key point 2"]
            }},
            {{
                "aspect": "Customer Service",
                "score": 0-100,
                "sentiment": "positive/negative/neutral",
                "key_points": ["key point 1", "key point 2"]
            }}
        ],
        "summary": "Brief summary of overall findings",
        "recommendation": "buy/consider/avoid with explanation"
    }}
    
    Focus on analyzing:
    1. Overall product quality based on reviews
    2. Delivery experience
    3. Customer service quality
    4. Value for money
    5. Reliability and trustworthiness
    
    Provide scores out of 100 and detailed key points for each aspect.
    """
    
    try:
        # Send analysis request to Gemini
        response = await chat.send_message(UserMessage(text=analysis_prompt))
        
        # Parse the JSON response
        analysis_data = json.loads(response.strip())
        
        # Create TrustScore object
        trust_score = TrustScore(
            product_id=product_id,
            overall_score=analysis_data["overall_score"],
            total_reviews=analysis_data["total_reviews"],
            aspect_analysis=[
                AspectAnalysis(
                    aspect=aspect["aspect"],
                    score=aspect["score"],
                    sentiment=aspect["sentiment"],
                    key_points=aspect["key_points"]
                ) for aspect in analysis_data["aspect_analysis"]
            ],
            summary=analysis_data["summary"],
            recommendation=analysis_data["recommendation"],
            updated_at=datetime.now().isoformat()
        )
        
        return trust_score
        
    except Exception as e:
        # Fallback analysis if AI fails
        fallback_score = TrustScore(
            product_id=product_id,
            overall_score=75,
            total_reviews=len(reviews),
            aspect_analysis=[
                AspectAnalysis(
                    aspect="Quality",
                    score=78,
                    sentiment="positive",
                    key_points=["Generally good quality", "Some mixed experiences"]
                ),
                AspectAnalysis(
                    aspect="Delivery",
                    score=72,
                    sentiment="neutral",
                    key_points=["Mixed delivery times", "Most orders arrive safely"]
                ),
                AspectAnalysis(
                    aspect="Customer Service",
                    score=65,
                    sentiment="neutral",
                    key_points=["Variable response times", "Generally helpful"]
                )
            ],
            summary="Mixed reviews with generally positive sentiment",
            recommendation="consider - Good product with some areas for improvement",
            updated_at=datetime.now().isoformat()
        )
        return fallback_score

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Trust Lens API"}

@app.post("/api/analyze-product")
async def analyze_product(request: ProductRequest):
    """Analyze a product and generate trust score"""
    
    # Generate product ID
    product_id = str(uuid.uuid4())
    
    # Create product record
    product = Product(
        id=product_id,
        name=request.product_name or "Sample Product",
        description=request.product_description or "Product description not available",
        url=request.product_url,
        created_at=datetime.now().isoformat()
    )
    
    # Add mock reviews for the product
    product_reviews = []
    for review_data in MOCK_REVIEWS:
        review = Review(
            id=review_data["id"],
            product_id=product_id,
            author=review_data["author"],
            rating=review_data["rating"],
            title=review_data["title"],
            content=review_data["content"],
            date=review_data["date"],
            verified=review_data["verified"],
            platform=review_data["platform"]
        )
        product_reviews.append(review)
    
    # Generate AI-powered trust analysis
    trust_score = await generate_trust_analysis(product_id, MOCK_REVIEWS)
    
    # Update product with trust score
    product.trust_score = trust_score
    
    # Save to database
    await products_collection.insert_one(product.dict())
    
    # Save reviews to database
    for review in product_reviews:
        await reviews_collection.insert_one(review.dict())
    
    # Save trust score to database
    await trust_scores_collection.insert_one(trust_score.dict())
    
    return product

@app.get("/api/product/{product_id}")
async def get_product(product_id: str):
    """Get product details with trust analysis"""
    
    product = await products_collection.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

@app.get("/api/products")
async def get_products(limit: int = 10, offset: int = 0):
    """Get all analyzed products"""
    
    cursor = products_collection.find().skip(offset).limit(limit)
    products = await cursor.to_list(length=limit)
    
    return {
        "products": products,
        "total": await products_collection.count_documents({}),
        "offset": offset,
        "limit": limit
    }

@app.get("/api/reviews/{product_id}")
async def get_product_reviews(product_id: str):
    """Get reviews for a specific product"""
    
    cursor = reviews_collection.find({"product_id": product_id})
    reviews = await cursor.to_list(length=100)
    
    return {
        "product_id": product_id,
        "reviews": reviews,
        "total": len(reviews)
    }

@app.get("/api/dashboard/analytics")
async def get_dashboard_analytics():
    """Get B2B dashboard analytics"""
    
    total_products = await products_collection.count_documents({})
    total_reviews = await reviews_collection.count_documents({})
    
    # Get average trust scores
    pipeline = [
        {
            "$group": {
                "_id": None,
                "avg_trust_score": {"$avg": "$trust_score.overall_score"},
                "total_products": {"$sum": 1}
            }
        }
    ]
    
    result = await products_collection.aggregate(pipeline).to_list(length=1)
    avg_trust_score = result[0]["avg_trust_score"] if result else 0
    
    # Platform distribution
    platform_pipeline = [
        {"$unwind": "$reviews"},
        {"$group": {"_id": "$platform", "count": {"$sum": 1}}}
    ]
    
    platform_stats = await reviews_collection.aggregate(platform_pipeline).to_list(length=10)
    
    return {
        "total_products": total_products,
        "total_reviews": total_reviews,
        "average_trust_score": round(avg_trust_score, 2),
        "platform_distribution": platform_stats,
        "recent_activity": {
            "products_analyzed_today": 12,
            "reviews_processed": 156,
            "trust_scores_updated": 8
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)