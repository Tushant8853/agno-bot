#!/usr/bin/env python3
"""
Comprehensive API Testing for Agno Bot Backend
Tests all endpoints with real data and provides detailed results.
"""

import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List
import sys
import os

# Configuration
BASE_URL = "http://localhost:8000"
API_VERSION = "v1"
TIMEOUT = 30

class APITester:
    """Comprehensive API testing class."""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_tokens = {}
        self.test_data = {}
        
        # Real test data
        self.test_users = [
            {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "password": "SecurePass123"
            },
            {
                "username": "jane_smith",
                "email": "jane.smith@example.com", 
                "password": "StrongPass456"
            },
            {
                "username": "alex_wong",
                "email": "alex.wong@example.com",
                "password": "ComplexPass789"
            }
        ]
        
        self.test_messages = [
            "Hello, I'm interested in learning about artificial intelligence.",
            "What are the latest developments in machine learning?",
            "Can you help me understand neural networks?",
            "I prefer Python for data science projects.",
            "What's the difference between supervised and unsupervised learning?",
            "Tell me about deep learning applications in healthcare.",
            "I work as a software engineer and want to transition to AI.",
            "What programming languages are best for AI development?",
            "Can you explain the concept of transfer learning?",
            "I'm curious about natural language processing."
        ]
        
        self.test_queries = [
            "user preferences",
            "learning interests", 
            "technical background",
            "AI knowledge",
            "programming experience"
        ]
    
    def log_test(self, test_name: str, status: str, details: Dict[str, Any] = None):
        """Log test results."""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        
        # Print result
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict[str, Any]:
        """Make HTTP request and return response details."""
        # Handle root-level endpoints (root and health)
        if endpoint in ["", "health"]:
            url = f"{self.base_url}/{endpoint}"
        else:
            url = f"{self.base_url}/api/{API_VERSION}/{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=TIMEOUT)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=TIMEOUT)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=TIMEOUT)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=TIMEOUT)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                "success": 200 <= response.status_code < 300
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "status_code": 0,
                "error": str(e),
                "success": False
            }
        except json.JSONDecodeError as e:
            return {
                "status_code": response.status_code,
                "error": f"JSON decode error: {str(e)}",
                "body": response.text,
                "success": False
            }
    
    def test_health_endpoints(self):
        """Test health and root endpoints."""
        print("\n🔍 Testing Health Endpoints")
        print("=" * 50)
        
        # Test root endpoint
        response = self.make_request("GET", "")
        self.log_test(
            "Root Endpoint",
            "PASS" if response["success"] else "FAIL",
            {
                "status_code": response["status_code"],
                "response_keys": list(response.get("body", {}).keys()) if isinstance(response.get("body"), dict) else []
            }
        )
        
        # Test health endpoint
        response = self.make_request("GET", "health")
        self.log_test(
            "Health Check",
            "PASS" if response["success"] else "FAIL",
            {
                "status_code": response["status_code"],
                "services": response.get("body", {}).get("services", {}) if isinstance(response.get("body"), dict) else {}
            }
        )
    
    def test_authentication(self):
        """Test authentication endpoints."""
        print("\n🔐 Testing Authentication Endpoints")
        print("=" * 50)
        
        for i, user_data in enumerate(self.test_users):
            user_id = f"user_{i+1}"
            
            # Test user registration
            response = self.make_request("POST", "auth/signup", user_data)
            if response["success"]:
                self.test_data[f"{user_id}_tokens"] = response["body"]["tokens"]
                self.log_test(
                    f"User Registration - {user_data['username']}",
                    "PASS",
                    {
                        "user_id": response["body"]["user"]["id"],
                        "username": response["body"]["user"]["username"],
                        "has_access_token": "access_token" in response["body"]["tokens"]
                    }
                )
            else:
                self.log_test(
                    f"User Registration - {user_data['username']}",
                    "FAIL",
                    {"error": response.get("body", {}).get("detail", "Unknown error")}
                )
            
            # Test user login
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            response = self.make_request("POST", "auth/login", login_data)
            if response["success"]:
                self.auth_tokens[user_id] = response["body"]["tokens"]
                self.log_test(
                    f"User Login - {user_data['username']}",
                    "PASS",
                    {
                        "user_id": response["body"]["user"]["id"],
                        "has_session_token": "session_token" in response["body"]["tokens"]
                    }
                )
            else:
                self.log_test(
                    f"User Login - {user_data['username']}",
                    "FAIL",
                    {"error": response.get("body", {}).get("detail", "Unknown error")}
                )
    
    def test_authenticated_endpoints(self):
        """Test endpoints that require authentication."""
        print("\n🔒 Testing Authenticated Endpoints")
        print("=" * 50)
        
        for user_id, tokens in self.auth_tokens.items():
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            
            # Test get current user profile
            response = self.make_request("GET", "auth/me", headers=headers)
            self.log_test(
                f"Get User Profile - {user_id}",
                "PASS" if response["success"] else "FAIL",
                {
                    "status_code": response["status_code"],
                    "user_id": response.get("body", {}).get("user", {}).get("id") if response["success"] else None
                }
            )
            
            # Test get user sessions
            response = self.make_request("GET", "auth/sessions", headers=headers)
            self.log_test(
                f"Get User Sessions - {user_id}",
                "PASS" if response["success"] else "FAIL",
                {
                    "status_code": response["status_code"],
                    "session_count": response.get("body", {}).get("count", 0) if response["success"] else 0
                }
            )
    
    def test_chat_endpoints(self):
        """Test chat endpoints."""
        print("\n💬 Testing Chat Endpoints")
        print("=" * 50)
        
        # Test with first authenticated user
        if not self.auth_tokens:
            self.log_test("Chat Endpoints", "SKIP", {"reason": "No authenticated users available"})
            return
        
        user_id = list(self.auth_tokens.keys())[0]
        tokens = self.auth_tokens[user_id]
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        session_id = str(uuid.uuid4())
        
        for i, message in enumerate(self.test_messages[:5]):  # Test first 5 messages
            chat_data = {
                "message": message,
                "session_id": session_id,
                "user_id": user_id
            }
            
            response = self.make_request("POST", "chat/send", chat_data, headers)
            self.log_test(
                f"Send Chat Message {i+1}",
                "PASS" if response["success"] else "FAIL",
                {
                    "status_code": response["status_code"],
                    "message_length": len(message),
                    "has_response": "response" in response.get("body", {}) if response["success"] else False
                }
            )
            
            # Small delay between messages
            time.sleep(1)
    
    def test_memory_endpoints(self):
        """Test memory endpoints."""
        print("\n🧠 Testing Memory Endpoints")
        print("=" * 50)
        
        if not self.auth_tokens:
            self.log_test("Memory Endpoints", "SKIP", {"reason": "No authenticated users available"})
            return
        
        user_id = list(self.auth_tokens.keys())[0]
        tokens = self.auth_tokens[user_id]
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        session_id = str(uuid.uuid4())
        
        # Test memory context
        response = self.make_request("GET", f"memory/context/{session_id}", headers=headers)
        self.log_test(
            "Get Memory Context",
            "PASS" if response["success"] else "FAIL",
            {
                "status_code": response["status_code"],
                "facts_count": len(response.get("body", {}).get("facts", [])) if response["success"] else 0,
                "relationships_count": len(response.get("body", {}).get("relationships", [])) if response["success"] else 0
            }
        )
        
        # Test memory search
        for query in self.test_queries[:3]:  # Test first 3 queries
            search_data = {
                "query": query,
                "query_type": "semantic",
                "limit": 5
            }
            
            response = self.make_request("POST", "memory/search", search_data, headers)
            self.log_test(
                f"Memory Search - '{query}'",
                "PASS" if response["success"] else "FAIL",
                {
                    "status_code": response["status_code"],
                    "results_count": response.get("body", {}).get("total_count", 0) if response["success"] else 0,
                    "search_time_ms": response.get("body", {}).get("search_time_ms", 0) if response["success"] else 0
                }
            )
        
        # Test create relationship - use query parameters instead of JSON body
        relationship_params = {
            "source_entity": "user",
            "target_entity": "ai_learning", 
            "relationship_type": "interested_in",
            "session_id": session_id,
            "confidence": 0.9
        }
        
        # Make POST request with query parameters
        url = f"{self.base_url}/api/{API_VERSION}/memory/relationships"
        response = self.session.post(url, params=relationship_params, headers=headers, timeout=TIMEOUT)
        
        try:
            response_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.json() if 'application/json' in response.headers.get('content-type', '') else response.text,
                "success": 200 <= response.status_code < 300
            }
        except Exception as e:
            response_data = {
                "status_code": response.status_code,
                "error": str(e),
                "success": False
            }
        self.log_test(
            "Create Memory Relationship",
            "PASS" if response_data["success"] else "FAIL",
            {
                "status_code": response_data["status_code"],
                "relationship_id": response_data.get("body", {}).get("id") if response_data["success"] else None
            }
        )
        
        # Test get facts
        response = self.make_request("GET", "memory/facts", headers=headers)
        self.log_test(
            "Get Memory Facts",
            "PASS" if response["success"] else "FAIL",
            {
                "status_code": response["status_code"],
                "facts_count": len(response.get("body", [])) if response["success"] else 0
            }
        )
        
        # Test get relationships
        response = self.make_request("GET", "memory/relationships", headers=headers)
        self.log_test(
            "Get Memory Relationships",
            "PASS" if response["success"] else "FAIL",
            {
                "status_code": response["status_code"],
                "relationships_count": len(response.get("body", [])) if response["success"] else 0
            }
        )
        
        # Test memory analytics
        response = self.make_request("GET", "memory/analytics", headers=headers)
        self.log_test(
            "Get Memory Analytics",
            "PASS" if response["success"] else "FAIL",
            {
                "status_code": response["status_code"],
                "total_facts": response.get("body", {}).get("total_facts", 0) if response["success"] else 0,
                "total_relationships": response.get("body", {}).get("total_relationships", 0) if response["success"] else 0
            }
        )
        
        # Test memory stats
        response = self.make_request("GET", "memory/stats", headers=headers)
        self.log_test(
            "Get Memory Stats",
            "PASS" if response["success"] else "FAIL",
            {
                "status_code": response["status_code"],
                "memory_usage_mb": response.get("body", {}).get("memory_usage_mb", 0) if response["success"] else 0
            }
        )
    
    def test_websocket_endpoint(self):
        """Test WebSocket endpoint."""
        print("\n🔌 Testing WebSocket Endpoint")
        print("=" * 50)
        
        # Test WebSocket endpoint availability (basic check)
        response = self.make_request("GET", "ws/")
        self.log_test(
            "WebSocket Endpoint",
            "PASS" if response["status_code"] in [200, 405, 426] else "FAIL",  # 405 = Method Not Allowed, 426 = Upgrade Required
            {
                "status_code": response["status_code"],
                "note": "WebSocket requires special client testing"
            }
        )
    
    def test_error_handling(self):
        """Test error handling."""
        print("\n⚠️ Testing Error Handling")
        print("=" * 50)
        
        # Test invalid endpoint
        response = self.make_request("GET", "invalid/endpoint")
        self.log_test(
            "Invalid Endpoint",
            "PASS" if response["status_code"] == 404 else "FAIL",
            {"status_code": response["status_code"]}
        )
        
        # Test invalid authentication
        headers = {"Authorization": "Bearer invalid_token"}
        response = self.make_request("GET", "auth/me", headers=headers)
        self.log_test(
            "Invalid Authentication",
            "PASS" if response["status_code"] == 401 else "FAIL",
            {"status_code": response["status_code"]}
        )
        
        # Test invalid JSON
        response = self.make_request("POST", "auth/login", {"invalid": "json"})
        self.log_test(
            "Invalid Login Data",
            "PASS" if response["status_code"] in [400, 422] else "FAIL",
            {"status_code": response["status_code"]}
        )
    
    def test_logout(self):
        """Test logout functionality."""
        print("\n🚪 Testing Logout")
        print("=" * 50)
        
        for user_id, tokens in self.auth_tokens.items():
            headers = {"X-Session-Token": tokens.get("session_token", "")}
            response = self.make_request("POST", "auth/logout", headers=headers)
            self.log_test(
                f"Logout - {user_id}",
                "PASS" if response["success"] else "FAIL",
                {"status_code": response["status_code"]}
            )
    
    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n📊 Generating Test Report")
        print("=" * 50)
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIP"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Create report
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": round(success_rate, 2)
            },
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat(),
            "api_version": API_VERSION,
            "base_url": BASE_URL
        }
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_test_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"📈 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Skipped: {skipped_tests} ⚠️")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"\n📄 Detailed report saved to: {filename}")
        
        return report
    
    def run_all_tests(self):
        """Run all tests in sequence."""
        print("🚀 Starting Comprehensive API Testing")
        print("=" * 60)
        print(f"Target URL: {self.base_url}")
        print(f"API Version: {API_VERSION}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        try:
            # Run all test suites
            self.test_health_endpoints()
            self.test_authentication()
            self.test_authenticated_endpoints()
            self.test_chat_endpoints()
            self.test_memory_endpoints()
            self.test_websocket_endpoint()
            self.test_error_handling()
            self.test_logout()
            
            # Generate report
            report = self.generate_report()
            
            print("\n🎉 Testing completed!")
            return report
            
        except KeyboardInterrupt:
            print("\n⏹️ Testing interrupted by user")
            return None
        except Exception as e:
            print(f"\n💥 Testing failed with error: {e}")
            return None

def main():
    """Main function to run the API tests."""
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server health check failed: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("Please make sure the backend server is running.")
        sys.exit(1)
    
    # Run tests
    tester = APITester()
    report = tester.run_all_tests()
    
    if report:
        success_rate = report["test_summary"]["success_rate"]
        if success_rate >= 90:
            print("🎯 Excellent! API is working well.")
        elif success_rate >= 70:
            print("👍 Good! API is mostly working.")
        else:
            print("⚠️ API needs attention. Check the detailed report.")
    
    return report

if __name__ == "__main__":
    main() 