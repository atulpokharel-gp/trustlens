import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('b2c');
  const [productInput, setProductInput] = useState('');
  const [productName, setProductName] = useState('');
  const [productDescription, setProductDescription] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  const [recentProducts, setRecentProducts] = useState([]);
  const [productReviews, setProductReviews] = useState([]);
  const [showReviews, setShowReviews] = useState(true);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Fetch dashboard data for B2B
  useEffect(() => {
    if (activeTab === 'b2b') {
      fetchDashboardData();
      fetchRecentProducts();
    }
  }, [activeTab]);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/dashboard/analytics`);
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const fetchRecentProducts = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/products?limit=5`);
      const data = await response.json();
      setRecentProducts(data.products || []);
    } catch (error) {
      console.error('Error fetching recent products:', error);
    }
  };

  const analyzeProduct = async () => {
    if (!productInput.trim() && !productName.trim()) {
      alert('Please enter a product URL or name');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/analyze-product`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_url: productInput.trim() || null,
          product_name: productName.trim() || null,
          product_description: productDescription.trim() || null
        }),
      });

      const data = await response.json();
      setAnalysisResult(data);
    } catch (error) {
      console.error('Error analyzing product:', error);
      alert('Error analyzing product. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getTrustScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getTrustScoreBg = (score) => {
    if (score >= 80) return 'bg-green-100 border-green-300';
    if (score >= 60) return 'bg-yellow-100 border-yellow-300';
    return 'bg-red-100 border-red-300';
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return '😊';
      case 'negative':
        return '😞';
      default:
        return '😐';
    }
  };

  const renderB2CInterface = () => (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Trust Lens
        </h1>
        <p className="text-lg text-gray-600">
          AI-Powered Product Trust Analysis
        </p>
        <p className="text-sm text-gray-500 mt-2">
          Get instant insights from reviews across Amazon, eBay, Walmart, Target & AliExpress
        </p>
      </div>

      {/* Analysis Input */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h2 className="text-2xl font-semibold mb-4">Analyze a Product</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Product URL (optional)
            </label>
            <input
              type="url"
              value={productInput}
              onChange={(e) => setProductInput(e.target.value)}
              placeholder="https://amazon.com/product-link or https://ebay.com/item/..."
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Product Name
            </label>
            <input
              type="text"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="e.g., iPhone 15 Pro, Samsung Galaxy Watch, etc."
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Product Description (optional)
            </label>
            <textarea
              value={productDescription}
              onChange={(e) => setProductDescription(e.target.value)}
              placeholder="Brief description of the product..."
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <button
            onClick={analyzeProduct}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
          >
            {loading ? 'Analyzing...' : 'Analyze Product Trust Score'}
          </button>
        </div>
      </div>

      {/* Analysis Results */}
      {analysisResult && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">Trust Analysis Results</h2>
          
          {/* Product Info */}
          <div className="mb-6">
            <h3 className="text-xl font-medium text-gray-900">{analysisResult.name}</h3>
            <p className="text-gray-600 mt-1">{analysisResult.description}</p>
          </div>

          {/* Overall Trust Score */}
          <div className={`rounded-lg p-4 border-2 mb-6 ${getTrustScoreBg(analysisResult.trust_score.overall_score)}`}>
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-lg font-semibold text-gray-900">Overall Trust Score</h4>
                <p className="text-sm text-gray-600">Based on {analysisResult.trust_score.total_reviews} reviews</p>
              </div>
              <div className="text-right">
                <div className={`text-4xl font-bold ${getTrustScoreColor(analysisResult.trust_score.overall_score)}`}>
                  {analysisResult.trust_score.overall_score}
                </div>
                <div className="text-sm text-gray-600">out of 100</div>
              </div>
            </div>
          </div>

          {/* Aspect Analysis */}
          <div className="mb-6">
            <h4 className="text-lg font-semibold mb-4">Aspect Analysis</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {analysisResult.trust_score.aspect_analysis.map((aspect, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h5 className="font-medium text-gray-900">{aspect.aspect}</h5>
                    <span className="text-lg">{getSentimentIcon(aspect.sentiment)}</span>
                  </div>
                  <div className={`text-2xl font-bold ${getTrustScoreColor(aspect.score)} mb-2`}>
                    {aspect.score}
                  </div>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {aspect.key_points.map((point, pointIndex) => (
                      <li key={pointIndex} className="flex items-start">
                        <span className="text-blue-500 mr-2">•</span>
                        {point}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>

          {/* Summary and Recommendation */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-blue-50 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-2">Summary</h4>
              <p className="text-blue-800">{analysisResult.trust_score.summary}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <h4 className="font-semibold text-green-900 mb-2">Recommendation</h4>
              <p className="text-green-800">{analysisResult.trust_score.recommendation}</p>
            </div>
          </div>

          {/* Platforms Analyzed */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">Platforms Analyzed</h4>
            <div className="flex flex-wrap gap-2">
              {['Amazon', 'eBay', 'Walmart', 'Target', 'AliExpress'].map((platform) => (
                <span key={platform} className="px-3 py-1 bg-white rounded-full text-sm font-medium text-gray-700 border">
                  {platform}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderB2BDashboard = () => (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Trust Lens B2B Dashboard</h1>
        <p className="text-gray-600 mt-2">Analytics and insights for business clients</p>
      </div>

      {/* Analytics Cards */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Total Products</h3>
            <p className="text-3xl font-bold text-gray-900">{dashboardData.total_products}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Total Reviews</h3>
            <p className="text-3xl font-bold text-gray-900">{dashboardData.total_reviews}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Avg Trust Score</h3>
            <p className="text-3xl font-bold text-gray-900">{dashboardData.average_trust_score}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Products Today</h3>
            <p className="text-3xl font-bold text-gray-900">{dashboardData.recent_activity.products_analyzed_today}</p>
          </div>
        </div>
      )}

      {/* Recent Products */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recently Analyzed Products</h2>
        </div>
        <div className="p-6">
          {recentProducts.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No products analyzed yet. Use the B2C interface to analyze your first product.</p>
          ) : (
            <div className="space-y-4">
              {recentProducts.map((product, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{product.name}</h3>
                    <p className="text-sm text-gray-600">{product.description}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      Analyzed: {new Date(product.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  {product.trust_score && (
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${getTrustScoreColor(product.trust_score.overall_score)}`}>
                        {product.trust_score.overall_score}
                      </div>
                      <div className="text-sm text-gray-600">Trust Score</div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* API Information */}
      <div className="mt-8 bg-blue-50 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-blue-900 mb-4">API Access</h2>
        <p className="text-blue-800 mb-4">
          Integrate Trust Lens into your applications using our RESTful API:
        </p>
        <div className="bg-white rounded p-4 font-mono text-sm">
          <p className="text-gray-700">POST /api/analyze-product</p>
          <p className="text-gray-700">GET /api/product/{'{product_id}'}</p>
          <p className="text-gray-700">GET /api/products</p>
          <p className="text-gray-700">GET /api/dashboard/analytics</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-blue-600">Trust Lens</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setActiveTab('b2c')}
                className={`px-4 py-2 rounded-md font-medium ${
                  activeTab === 'b2c'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:text-blue-600'
                }`}
              >
                Consumer
              </button>
              <button
                onClick={() => setActiveTab('b2b')}
                className={`px-4 py-2 rounded-md font-medium ${
                  activeTab === 'b2b'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:text-blue-600'
                }`}
              >
                Business
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="py-8">
        {activeTab === 'b2c' ? renderB2CInterface() : renderB2BDashboard()}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="text-center text-gray-600">
            <p>&copy; 2024 Trust Lens. AI-powered product trust analysis.</p>
            <p className="mt-2 text-sm">
              Analyzing reviews from Amazon, eBay, Walmart, Target, and AliExpress
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;