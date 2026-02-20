"""
Test script for Location Safety RAG API
Run this to test all endpoints with sample data
"""

import requests
from datetime import datetime
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing /health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200, "Health check failed"
    print("✅ Health check passed")

def test_root():
    """Test root endpoint"""
    print("\n🔍 Testing /...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200, "Root endpoint failed"
    print("✅ Root endpoint passed")

def test_submit_feedback():
    """Test feedback submission"""
    print("\n🔍 Testing POST /feedback/submit...")
    
    payload = {
        "question": "How safe is this area late at night?",
        "answer": "Generally safe with good police patrols, though some petty theft occurs",
        "location": {
            "lat": 28.6139,
            "long": 77.2090,
            "name": "Delhi - Connaught Place"
        },
        "rating": 4,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_id": "test_user_1"
    }
    
    print(f"Sending: {json.dumps(payload, indent=2)}")
    response = requests.post(f"{BASE_URL}/feedback/submit", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201, f"Feedback submission failed: {response.text}"
    data = response.json()
    assert data["success"] == True, "Success flag not true"
    assert data["feedback_id"], "No feedback_id returned"
    print("✅ Feedback submission passed")
    return data["feedback_id"]

def test_submit_feedback_invalid():
    """Test invalid feedback submission"""
    print("\n🔍 Testing POST /feedback/submit with invalid data...")
    
    # Too short question
    payload = {
        "question": "Safe?",  # Too short
        "answer": "Yes it is safe for everyone",
        "location": {
            "lat": 28.6139,
            "long": 77.2090,
            "name": "Delhi"
        },
        "rating": 4,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    response = requests.post(f"{BASE_URL}/feedback/submit", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code in [400, 422], "Should reject invalid data"
    print("✅ Invalid data rejection passed")

def test_submit_multiple_feedback():
    """Submit multiple feedback for testing analysis"""
    print("\n🔍 Submitting multiple feedbacks for analysis...")
    
    feedbacks = [
        {
            "question": "Is traffic heavy during rush hours?",
            "answer": "Yes, very heavy traffic from 8-10 AM and 5-7 PM",
            "location": {"lat": 28.6139, "long": 77.2090, "name": "Delhi"},
            "rating": 3,
            "user_id": "user_2"
        },
        {
            "question": "Are streets well lit at night?",
            "answer": "Most main roads are well lit, but some side streets need better lighting",
            "location": {"lat": 28.6139, "long": 77.2090, "name": "Delhi"},
            "rating": 4,
            "user_id": "user_3"
        },
        {
            "question": "How is public transportation safety?",
            "answer": "Metro is very safe, buses during evening can be crowded",
            "location": {"lat": 28.6139, "long": 77.2090, "name": "Delhi"},
            "rating": 4,
            "user_id": "user_4"
        }
    ]
    
    for i, feedback in enumerate(feedbacks, 1):
        feedback["timestamp"] = datetime.utcnow().isoformat() + "Z"
        response = requests.post(f"{BASE_URL}/feedback/submit", json=feedback)
        print(f"Feedback {i}: {response.status_code}")
        assert response.status_code == 201, f"Failed to submit feedback {i}"
    
    print("✅ Multiple feedbacks submitted")

def test_analyze_location():
    """Test location analysis"""
    print("\n🔍 Testing GET /location/analyze...")
    
    params = {
        "lat": 28.6139,
        "long": 77.2090,
        "name": "Delhi - Connaught Place"
    }
    
    print(f"Parameters: {params}")
    response = requests.get(f"{BASE_URL}/location/analyze", params=params)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 Analysis Result:")
        print(f"  Safety Score: {data['safety_profile']['score']}/10")
        print(f"  Trend: {data['safety_profile']['trend']}")
        print(f"  Reports: {data['data_quality']['reports_count']}")
        print(f"  Concerns: {data['insights']['top_concerns']}")
    else:
        print(f"Response: {response.json()}")
    
    assert response.status_code == 200, f"Location analysis failed: {response.text}"
    print("✅ Location analysis passed")

def test_analyze_empty_location():
    """Test analysis for location with no data"""
    print("\n🔍 Testing analysis for empty location...")
    
    params = {
        "lat": 40.7128,  # New York
        "long": -74.0060,
        "name": "New York - No Data"
    }
    
    response = requests.get(f"{BASE_URL}/location/analyze", params=params)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Reports found: {data['data_quality']['reports_count']}")
    
    assert response.status_code == 200, "Should handle empty location"
    print("✅ Empty location handling passed")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Location Safety RAG API - Test Suite")
    print("=" * 60)
    
    try:
        # Basic tests
        test_health()
        test_root()
        
        # Feedback tests
        test_submit_feedback()
        test_submit_feedback_invalid()
        test_submit_multiple_feedback()
        
        # Analysis tests
        test_analyze_location()
        test_analyze_empty_location()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED! 🎉")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("\n⏳ Make sure the server is running: uvicorn app.main:app --reload\n")
    input("Press Enter to start tests...")
    
    success = run_all_tests()
    exit(0 if success else 1)
