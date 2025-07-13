#!/usr/bin/env python3
"""
Test Gemini AI Integration specifically
"""

import requests
import json
import time

BACKEND_URL = "https://ea84c4c4-fbd0-4a37-b838-0349c1356239.preview.emergentagent.com/api"

def test_gemini_ai_integration():
    """Test if Gemini AI is actually being used vs fallback"""
    
    # Test with a very specific product that should generate different responses
    test_products = [
        {
            "product_name": "Luxury Diamond Ring",
            "product_description": "Premium 2-carat diamond engagement ring with platinum setting"
        },
        {
            "product_name": "Cheap Plastic Toy",
            "product_description": "Low-quality plastic toy that breaks easily"
        }
    ]
    
    responses = []
    
    for product in test_products:
        try:
            response = requests.post(
                f"{BACKEND_URL}/analyze-product",
                json=product,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                trust_score = data.get("trust_score", {})
                responses.append({
                    "product": product["product_name"],
                    "overall_score": trust_score.get("overall_score"),
                    "summary": trust_score.get("summary"),
                    "recommendation": trust_score.get("recommendation")
                })
                print(f"✅ {product['product_name']}: Score {trust_score.get('overall_score')}")
                print(f"   Summary: {trust_score.get('summary')}")
                print(f"   Recommendation: {trust_score.get('recommendation')}")
                print()
            else:
                print(f"❌ Failed to analyze {product['product_name']}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error analyzing {product['product_name']}: {e}")
            return False
    
    # Check if we're getting fallback responses (all scores are exactly 75)
    if len(responses) == 2:
        scores = [r["overall_score"] for r in responses]
        summaries = [r["summary"] for r in responses]
        
        # If both scores are exactly 75 and summaries are identical, likely using fallback
        if all(score == 75.0 for score in scores) and summaries[0] == summaries[1]:
            print("⚠️  WARNING: Appears to be using fallback analysis (identical scores and summaries)")
            print("   This suggests Gemini AI integration may not be working properly")
            return "fallback"
        else:
            print("✅ AI integration appears to be working (varied responses)")
            return True
    
    return False

if __name__ == "__main__":
    print("🧪 Testing Gemini AI Integration")
    print("=" * 50)
    result = test_gemini_ai_integration()
    
    if result == "fallback":
        print("\n📋 RESULT: Using fallback analysis - AI integration needs investigation")
    elif result:
        print("\n📋 RESULT: AI integration working properly")
    else:
        print("\n📋 RESULT: AI integration test failed")