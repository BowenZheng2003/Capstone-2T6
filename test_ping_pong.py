#!/usr/bin/env python3
"""
Simple test script to verify backend ping/pong functionality
"""
import requests
import sys

def test_ping_pong():
    """Test if backend responds to ping with pong"""
    try:
        print("Testing ping/pong connection...")
        response = requests.get("http://localhost:8000/ping")
        
        if response.status_code == 200:
            response_text = response.text.strip().strip('"')
            if response_text == "pong":
                print("✅ SUCCESS: Backend responded with 'pong' to ping!")
                return True
            else:
                print(f"❌ FAILED: Expected 'pong', got '{response_text}'")
                return False
        else:
            print(f"❌ FAILED: Backend responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Cannot connect to backend. Make sure it's running on localhost:8000")
        print("   Start backend with: cd backend && python app.py")
        return False
    except Exception as e:
        print(f"❌ FAILED: Error testing backend: {e}")
        return False

if __name__ == "__main__":
    success = test_ping_pong()
    if success:
        print("\n🎉 Ping/Pong connection is working! You can now test in the frontend.")
    sys.exit(0 if success else 1)
