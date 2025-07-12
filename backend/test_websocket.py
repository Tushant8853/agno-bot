#!/usr/bin/env python3
"""
WebSocket Testing for Agno Bot Backend
Tests real-time communication functionality.
"""

import asyncio
import websockets
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List

# Configuration
WS_URL = "ws://localhost:8000/api/v1/ws/chat"
TIMEOUT = 30

class WebSocketTester:
    """WebSocket testing class."""
    
    def __init__(self):
        self.ws_url = WS_URL
        self.test_results = []
        self.websocket = None
        
        # Real test data for WebSocket
        self.test_messages = [
            {
                "type": "message",
                "content": "Hello, I'm testing the WebSocket connection.",
                "session_id": str(uuid.uuid4()),
                "user_id": "test_user_1"
            },
            {
                "type": "message", 
                "content": "Can you help me understand machine learning?",
                "session_id": str(uuid.uuid4()),
                "user_id": "test_user_2"
            },
            {
                "type": "message",
                "content": "What are the latest developments in AI?",
                "session_id": str(uuid.uuid4()),
                "user_id": "test_user_3"
            }
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
    
    async def test_connection(self):
        """Test WebSocket connection."""
        print("\n🔌 Testing WebSocket Connection")
        print("=" * 50)
        
        try:
            # Test connection
            self.websocket = await asyncio.wait_for(
                websockets.connect(self.ws_url),
                timeout=10
            )
            
            self.log_test(
                "WebSocket Connection",
                "PASS",
                {"url": self.ws_url, "status": "connected"}
            )
            return True
            
        except asyncio.TimeoutError:
            self.log_test(
                "WebSocket Connection",
                "FAIL",
                {"error": "Connection timeout", "url": self.ws_url}
            )
            return False
        except Exception as e:
            self.log_test(
                "WebSocket Connection",
                "FAIL",
                {"error": str(e), "url": self.ws_url}
            )
            return False
    
    async def test_message_sending(self):
        """Test sending messages through WebSocket."""
        print("\n📤 Testing Message Sending")
        print("=" * 50)
        
        if not self.websocket:
            self.log_test("Message Sending", "SKIP", {"reason": "No WebSocket connection"})
            return
        
        try:
            for i, message in enumerate(self.test_messages):
                # Send message
                await self.websocket.send(json.dumps(message))
                
                self.log_test(
                    f"Send Message {i+1}",
                    "PASS",
                    {
                        "message_type": message["type"],
                        "content_length": len(message["content"]),
                        "session_id": message["session_id"]
                    }
                )
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=5
                    )
                    
                    response_data = json.loads(response)
                    self.log_test(
                        f"Receive Response {i+1}",
                        "PASS",
                        {
                            "response_type": response_data.get("type"),
                            "has_content": "content" in response_data,
                            "response_length": len(response) if response else 0
                        }
                    )
                    
                except asyncio.TimeoutError:
                    self.log_test(
                        f"Receive Response {i+1}",
                        "FAIL",
                        {"error": "Response timeout"}
                    )
                except json.JSONDecodeError:
                    self.log_test(
                        f"Receive Response {i+1}",
                        "FAIL",
                        {"error": "Invalid JSON response"}
                    )
                
                # Small delay between messages
                await asyncio.sleep(1)
                
        except Exception as e:
            self.log_test(
                "Message Sending",
                "FAIL",
                {"error": str(e)}
            )
    
    async def test_connection_stability(self):
        """Test connection stability with multiple messages."""
        print("\n🔒 Testing Connection Stability")
        print("=" * 50)
        
        if not self.websocket:
            self.log_test("Connection Stability", "SKIP", {"reason": "No WebSocket connection"})
            return
        
        try:
            # Send multiple messages rapidly
            rapid_messages = [
                {"type": "ping", "content": "ping", "session_id": str(uuid.uuid4())},
                {"type": "message", "content": "Quick test message", "session_id": str(uuid.uuid4())},
                {"type": "ping", "content": "ping", "session_id": str(uuid.uuid4())}
            ]
            
            for i, message in enumerate(rapid_messages):
                await self.websocket.send(json.dumps(message))
                await asyncio.sleep(0.1)  # Very short delay
            
            # Check if connection is still alive
            await self.websocket.ping()
            
            self.log_test(
                "Connection Stability",
                "PASS",
                {"messages_sent": len(rapid_messages), "connection_alive": True}
            )
            
        except Exception as e:
            self.log_test(
                "Connection Stability",
                "FAIL",
                {"error": str(e)}
            )
    
    async def test_error_handling(self):
        """Test WebSocket error handling."""
        print("\n⚠️ Testing Error Handling")
        print("=" * 50)
        
        if not self.websocket:
            self.log_test("Error Handling", "SKIP", {"reason": "No WebSocket connection"})
            return
        
        try:
            # Test invalid JSON
            await self.websocket.send("invalid json")
            
            # Try to receive response
            try:
                response = await asyncio.wait_for(
                    self.websocket.recv(),
                    timeout=3
                )
                self.log_test(
                    "Invalid JSON Handling",
                    "PASS",
                    {"received_response": True, "response_length": len(response)}
                )
            except asyncio.TimeoutError:
                self.log_test(
                    "Invalid JSON Handling",
                    "FAIL",
                    {"error": "No response to invalid JSON"}
                )
            
            # Test malformed message
            malformed_message = {"type": "message"}  # Missing required fields
            await self.websocket.send(json.dumps(malformed_message))
            
            try:
                response = await asyncio.wait_for(
                    self.websocket.recv(),
                    timeout=3
                )
                self.log_test(
                    "Malformed Message Handling",
                    "PASS",
                    {"received_response": True}
                )
            except asyncio.TimeoutError:
                self.log_test(
                    "Malformed Message Handling",
                    "FAIL",
                    {"error": "No response to malformed message"}
                )
                
        except Exception as e:
            self.log_test(
                "Error Handling",
                "FAIL",
                {"error": str(e)}
            )
    
    async def test_connection_cleanup(self):
        """Test proper connection cleanup."""
        print("\n🧹 Testing Connection Cleanup")
        print("=" * 50)
        
        if not self.websocket:
            self.log_test("Connection Cleanup", "SKIP", {"reason": "No WebSocket connection"})
            return
        
        try:
            # Send close message
            await self.websocket.close()
            
            self.log_test(
                "Connection Cleanup",
                "PASS",
                {"status": "connection_closed"}
            )
            
        except Exception as e:
            self.log_test(
                "Connection Cleanup",
                "FAIL",
                {"error": str(e)}
            )
    
    def generate_report(self):
        """Generate WebSocket test report."""
        print("\n📊 Generating WebSocket Test Report")
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
            "websocket_url": self.ws_url
        }
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"websocket_test_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"📈 WebSocket Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Skipped: {skipped_tests} ⚠️")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"\n📄 Detailed report saved to: {filename}")
        
        return report
    
    async def run_all_tests(self):
        """Run all WebSocket tests."""
        print("🚀 Starting WebSocket Testing")
        print("=" * 60)
        print(f"WebSocket URL: {self.ws_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        try:
            # Run all test suites
            connection_success = await self.test_connection()
            
            if connection_success:
                await self.test_message_sending()
                await self.test_connection_stability()
                await self.test_error_handling()
                await self.test_connection_cleanup()
            
            # Generate report
            report = self.generate_report()
            
            print("\n🎉 WebSocket testing completed!")
            return report
            
        except KeyboardInterrupt:
            print("\n⏹️ WebSocket testing interrupted by user")
            return None
        except Exception as e:
            print(f"\n💥 WebSocket testing failed with error: {e}")
            return None

async def main():
    """Main function to run WebSocket tests."""
    # Run tests
    tester = WebSocketTester()
    report = await tester.run_all_tests()
    
    if report:
        success_rate = report["test_summary"]["success_rate"]
        if success_rate >= 90:
            print("🎯 Excellent! WebSocket is working well.")
        elif success_rate >= 70:
            print("👍 Good! WebSocket is mostly working.")
        else:
            print("⚠️ WebSocket needs attention. Check the detailed report.")
    
    return report

if __name__ == "__main__":
    asyncio.run(main()) 