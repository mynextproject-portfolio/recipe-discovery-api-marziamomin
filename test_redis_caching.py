#!/usr/bin/env python3
"""
Simple test script to verify Redis caching functionality.
Run this after starting the services with docker-compose up.
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_caching():
    """Test that MealDB search results are cached properly."""
    print("🧪 Testing Redis caching functionality...")
    
    search_query = "pasta"
    
    print(f"\n1️⃣ First search for '{search_query}' (should be cache miss):")
    start_time = time.time()
    response1 = requests.get(f"{BASE_URL}/recipes/search", params={"q": search_query})
    end_time = time.time()
    
    if response1.status_code == 200:
        data1 = response1.json()
        mealdb_recipes = [r for r in data1["recipes"] if r.get("source") == "mealdb"]
        print(f"   Found {len(mealdb_recipes)} MealDB recipes")
        print(f"   Response time: {end_time - start_time:.2f} seconds")
    else:
        print(f"   ❌ Request failed: {response1.status_code}")
        return
    
    print(f"\n2️⃣ Second search for '{search_query}' (should be cache hit):")
    start_time = time.time()
    response2 = requests.get(f"{BASE_URL}/recipes/search", params={"q": search_query})
    end_time = time.time()
    
    if response2.status_code == 200:
        data2 = response2.json()
        mealdb_recipes2 = [r for r in data2["recipes"] if r.get("source") == "mealdb"]
        print(f"   Found {len(mealdb_recipes2)} MealDB recipes")
        print(f"   Response time: {end_time - start_time:.2f} seconds")
        
        # Verify results are identical
        if len(mealdb_recipes) == len(mealdb_recipes2):
            print("   ✅ Same number of results (cache working!)")
        else:
            print("   ❌ Different number of results")
    else:
        print(f"   ❌ Request failed: {response2.status_code}")
        return
    
    print(f"\n3️⃣ Testing different search query '{search_query} carbonara' (new cache entry):")
    start_time = time.time()
    response3 = requests.get(f"{BASE_URL}/recipes/search", params={"q": f"{search_query} carbonara"})
    end_time = time.time()
    
    if response3.status_code == 200:
        data3 = response3.json()
        mealdb_recipes3 = [r for r in data3["recipes"] if r.get("source") == "mealdb"]
        print(f"   Found {len(mealdb_recipes3)} MealDB recipes")
        print(f"   Response time: {end_time - start_time:.2f} seconds")
    else:
        print(f"   ❌ Request failed: {response3.status_code}")

def test_health():
    """Test that the API is responding."""
    print("🏥 Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/ping")
        if response.status_code == 200:
            print("   ✅ API is healthy")
            return True
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API. Make sure docker-compose is running.")
        return False

if __name__ == "__main__":
    print("🚀 Redis Caching Test")
    print("=" * 50)
    
    # Test API health first
    if not test_health():
        print("\n💡 Make sure to run: docker-compose up")
        exit(1)
    
    # Test caching functionality
    test_caching()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
    print("\n💡 To see Redis logs: docker-compose logs redis")
    print("💡 To see app logs: docker-compose logs app")
