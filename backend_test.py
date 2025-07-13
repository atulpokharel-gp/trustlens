#!/usr/bin/env python3
"""
Trust Lens Backend API Testing Suite
Tests all backend endpoints with focus on AI-powered sentiment analysis
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

# Backend URL from frontend environment
BACKEND_URL = "https://ea84c4c4-fbd0-4a37-b838-0349c1356239.preview.emergentagent.com/api"

class TrustLensAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.created_product_id = None
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def test_health_endpoint(self):
        """Test GET /api/health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy" and "Trust Lens API" in data.get("service", ""):
                    self.log_test("Health Check", True, "API is healthy and responding correctly")
                    return True
                else:
                    self.log_test("Health Check", False, "Invalid health response format", data)
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False

    def test_analyze_product_with_url(self):
        """Test POST /api/analyze-product with product URL"""
        test_data = {
            "product_url": "https://www.amazon.com/dp/B08N5WRWNW",
            "product_name": "Echo Dot (4th Gen) Smart Speaker",
            "product_description": "Smart speaker with Alexa voice control"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/analyze-product",
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Store product ID for later tests
                self.created_product_id = data.get("id")
                
                # Validate response structure
                required_fields = ["id", "name", "description", "trust_score", "created_at"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Product Analysis (URL)", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                # Validate trust score structure
                trust_score = data.get("trust_score", {})
                trust_required = ["product_id", "overall_score", "total_reviews", "aspect_analysis", "summary", "recommendation"]
                trust_missing = [field for field in trust_required if field not in trust_score]
                
                if trust_missing:
                    self.log_test("Product Analysis (URL)", False, f"Missing trust score fields: {trust_missing}", trust_score)
                    return False
                
                # Validate aspect analysis
                aspects = trust_score.get("aspect_analysis", [])
                if len(aspects) != 3:
                    self.log_test("Product Analysis (URL)", False, f"Expected 3 aspects, got {len(aspects)}", aspects)
                    return False
                
                expected_aspects = ["Quality", "Delivery", "Customer Service"]
                actual_aspects = [aspect.get("aspect") for aspect in aspects]
                
                if not all(aspect in actual_aspects for aspect in expected_aspects):
                    self.log_test("Product Analysis (URL)", False, f"Missing expected aspects. Got: {actual_aspects}", aspects)
                    return False
                
                # Validate score ranges (0-100)
                overall_score = trust_score.get("overall_score", -1)
                if not (0 <= overall_score <= 100):
                    self.log_test("Product Analysis (URL)", False, f"Overall score {overall_score} not in range 0-100")
                    return False
                
                for aspect in aspects:
                    aspect_score = aspect.get("score", -1)
                    if not (0 <= aspect_score <= 100):
                        self.log_test("Product Analysis (URL)", False, f"Aspect score {aspect_score} not in range 0-100")
                        return False
                
                self.log_test("Product Analysis (URL)", True, f"Successfully analyzed product with trust score {overall_score}")
                return True
                
            else:
                self.log_test("Product Analysis (URL)", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Product Analysis (URL)", False, f"Request error: {str(e)}")
            return False

    def test_analyze_product_with_name_only(self):
        """Test POST /api/analyze-product with product name only"""
        test_data = {
            "product_name": "iPhone 15 Pro Max",
            "product_description": "Latest Apple smartphone with advanced camera system"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/analyze-product",
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Basic validation
                if "trust_score" in data and "overall_score" in data["trust_score"]:
                    score = data["trust_score"]["overall_score"]
                    self.log_test("Product Analysis (Name Only)", True, f"Successfully analyzed product with trust score {score}")
                    return True
                else:
                    self.log_test("Product Analysis (Name Only)", False, "Missing trust score in response", data)
                    return False
                    
            else:
                self.log_test("Product Analysis (Name Only)", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Product Analysis (Name Only)", False, f"Request error: {str(e)}")
            return False

    def test_get_product_by_id(self):
        """Test GET /api/product/{id} endpoint"""
        if not self.created_product_id:
            self.log_test("Get Product by ID", False, "No product ID available from previous tests")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/product/{self.created_product_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == self.created_product_id:
                    self.log_test("Get Product by ID", True, "Successfully retrieved product by ID")
                    return True
                else:
                    self.log_test("Get Product by ID", False, "Product ID mismatch", data)
                    return False
            elif response.status_code == 404:
                self.log_test("Get Product by ID", False, "Product not found in database")
                return False
            else:
                self.log_test("Get Product by ID", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Get Product by ID", False, f"Request error: {str(e)}")
            return False

    def test_get_all_products(self):
        """Test GET /api/products endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/products?limit=5&offset=0", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["products", "total", "offset", "limit"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Get All Products", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                products = data.get("products", [])
                total = data.get("total", 0)
                
                self.log_test("Get All Products", True, f"Retrieved {len(products)} products out of {total} total")
                return True
                
            else:
                self.log_test("Get All Products", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Get All Products", False, f"Request error: {str(e)}")
            return False

    def test_get_product_reviews(self):
        """Test GET /api/reviews/{product_id} endpoint"""
        if not self.created_product_id:
            self.log_test("Get Product Reviews", False, "No product ID available from previous tests")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/reviews/{self.created_product_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["product_id", "reviews", "total"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Get Product Reviews", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                reviews = data.get("reviews", [])
                expected_platforms = ["Amazon", "eBay", "Walmart", "Target", "AliExpress"]
                
                if len(reviews) == 5:  # Should have 5 mock reviews
                    platforms_found = [review.get("platform") for review in reviews]
                    if all(platform in expected_platforms for platform in platforms_found):
                        self.log_test("Get Product Reviews", True, f"Retrieved {len(reviews)} reviews from expected platforms")
                        return True
                    else:
                        self.log_test("Get Product Reviews", False, f"Unexpected platforms: {platforms_found}")
                        return False
                else:
                    self.log_test("Get Product Reviews", False, f"Expected 5 reviews, got {len(reviews)}")
                    return False
                    
            else:
                self.log_test("Get Product Reviews", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Get Product Reviews", False, f"Request error: {str(e)}")
            return False

    def test_dashboard_analytics(self):
        """Test GET /api/dashboard/analytics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/dashboard/analytics", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["total_products", "total_reviews", "average_trust_score", "platform_distribution", "recent_activity"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Dashboard Analytics", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                # Validate data types and ranges
                total_products = data.get("total_products", -1)
                total_reviews = data.get("total_reviews", -1)
                avg_score = data.get("average_trust_score", -1)
                
                if total_products < 0 or total_reviews < 0:
                    self.log_test("Dashboard Analytics", False, "Invalid negative counts in analytics")
                    return False
                
                if not (0 <= avg_score <= 100):
                    self.log_test("Dashboard Analytics", False, f"Average trust score {avg_score} not in range 0-100")
                    return False
                
                platform_dist = data.get("platform_distribution", [])
                recent_activity = data.get("recent_activity", {})
                
                self.log_test("Dashboard Analytics", True, 
                             f"Analytics: {total_products} products, {total_reviews} reviews, avg score {avg_score}")
                return True
                
            else:
                self.log_test("Dashboard Analytics", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Dashboard Analytics", False, f"Request error: {str(e)}")
            return False

    def test_ai_sentiment_analysis_quality(self):
        """Test AI sentiment analysis quality and consistency"""
        test_products = [
            {
                "product_name": "Premium Wireless Headphones",
                "product_description": "High-quality noise-canceling headphones with premium sound"
            },
            {
                "product_name": "Budget Phone Case",
                "product_description": "Basic protective case for smartphones"
            }
        ]
        
        analysis_results = []
        
        for i, product in enumerate(test_products):
            try:
                response = self.session.post(
                    f"{self.base_url}/analyze-product",
                    json=product,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    trust_score = data.get("trust_score", {})
                    analysis_results.append({
                        "product": product["product_name"],
                        "overall_score": trust_score.get("overall_score"),
                        "aspects": trust_score.get("aspect_analysis", []),
                        "summary": trust_score.get("summary"),
                        "recommendation": trust_score.get("recommendation")
                    })
                else:
                    self.log_test("AI Sentiment Analysis Quality", False, 
                                 f"Failed to analyze product {i+1}: HTTP {response.status_code}")
                    return False
                    
            except Exception as e:
                self.log_test("AI Sentiment Analysis Quality", False, 
                             f"Error analyzing product {i+1}: {str(e)}")
                return False
        
        # Validate analysis quality
        if len(analysis_results) == 2:
            # Check that both analyses have valid structure
            for result in analysis_results:
                if not all(key in result for key in ["overall_score", "aspects", "summary", "recommendation"]):
                    self.log_test("AI Sentiment Analysis Quality", False, "Incomplete analysis structure")
                    return False
                
                if len(result["aspects"]) != 3:
                    self.log_test("AI Sentiment Analysis Quality", False, "Missing aspect analysis")
                    return False
            
            self.log_test("AI Sentiment Analysis Quality", True, 
                         "AI analysis provides consistent, structured sentiment analysis")
            return True
        else:
            self.log_test("AI Sentiment Analysis Quality", False, "Failed to complete analysis tests")
            return False

    def test_error_handling(self):
        """Test error handling scenarios"""
        # Test invalid product ID
        try:
            response = self.session.get(f"{self.base_url}/product/invalid-id", timeout=10)
            if response.status_code == 404:
                self.log_test("Error Handling (Invalid ID)", True, "Correctly returns 404 for invalid product ID")
            else:
                self.log_test("Error Handling (Invalid ID)", False, f"Expected 404, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Error Handling (Invalid ID)", False, f"Request error: {str(e)}")
            return False
        
        # Test empty product analysis request
        try:
            response = self.session.post(f"{self.base_url}/analyze-product", json={}, timeout=10)
            if response.status_code == 200:
                # Should still work with default values
                data = response.json()
                if "trust_score" in data:
                    self.log_test("Error Handling (Empty Request)", True, "Handles empty request with defaults")
                else:
                    self.log_test("Error Handling (Empty Request)", False, "Empty request didn't generate trust score")
                    return False
            else:
                self.log_test("Error Handling (Empty Request)", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Error Handling (Empty Request)", False, f"Request error: {str(e)}")
            return False
        
        return True

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Trust Lens Backend API Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Core API tests
        self.test_health_endpoint()
        
        # AI-powered product analysis tests (HIGH PRIORITY)
        self.test_analyze_product_with_url()
        self.test_analyze_product_with_name_only()
        self.test_ai_sentiment_analysis_quality()
        
        # Product retrieval tests
        self.test_get_product_by_id()
        self.test_get_all_products()
        self.test_get_product_reviews()
        
        # Dashboard analytics tests (MEDIUM PRIORITY)
        self.test_dashboard_analytics()
        
        # Error handling tests
        self.test_error_handling()
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        return passed == total

if __name__ == "__main__":
    tester = TrustLensAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)