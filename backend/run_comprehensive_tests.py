#!/usr/bin/env python3
"""
Comprehensive Test Runner for Agno Bot Backend
Runs all tests and generates a combined report.
"""

import subprocess
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

def run_command(command: str, description: str) -> Dict[str, Any]:
    """Run a command and return results."""
    print(f"\n🚀 {description}")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "command": command,
            "description": description,
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": round(duration, 2)
        }
        
    except subprocess.TimeoutExpired:
        return {
            "command": command,
            "description": description,
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": "Command timed out after 5 minutes",
            "duration": 300
        }
    except Exception as e:
        return {
            "command": command,
            "description": description,
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": str(e),
            "duration": 0
        }

def check_server_health() -> bool:
    """Check if the backend server is running."""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def generate_combined_report(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a combined test report."""
    total_tests = len(results)
    successful_tests = len([r for r in results if r["success"]])
    failed_tests = total_tests - successful_tests
    
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    # Collect all test reports
    test_reports = []
    for result in results:
        if result["success"] and result["stdout"]:
            # Try to find JSON reports in stdout
            lines = result["stdout"].split('\n')
            for line in lines:
                if line.strip().endswith('.json') and 'report' in line.lower():
                    # Extract filename from the line
                    parts = line.split()
                    for part in parts:
                        if part.endswith('.json'):
                            try:
                                with open(part, 'r') as f:
                                    report = json.load(f)
                                    test_reports.append({
                                        "test_type": result["description"],
                                        "report": report
                                    })
                            except:
                                pass
    
    return {
        "summary": {
            "total_test_suites": total_tests,
            "successful_suites": successful_tests,
            "failed_suites": failed_tests,
            "overall_success_rate": round(success_rate, 2),
            "timestamp": datetime.now().isoformat()
        },
        "test_results": results,
        "detailed_reports": test_reports
    }

def main():
    """Main function to run all tests."""
    print("🎯 Agno Bot Backend - Comprehensive Testing Suite")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Check if server is running
    print("\n🔍 Checking server health...")
    if not check_server_health():
        print("❌ Backend server is not running!")
        print("Please start the backend server first:")
        print("   cd backend")
        print("   python run.py")
        sys.exit(1)
    
    print("✅ Backend server is running")
    
    # Define test commands
    test_commands = [
        {
            "command": "python test_comprehensive_api.py",
            "description": "Comprehensive API Testing"
        },
        {
            "command": "python test_websocket.py",
            "description": "WebSocket Testing"
        }
    ]
    
    # Run all tests
    results = []
    for test in test_commands:
        result = run_command(test["command"], test["description"])
        results.append(result)
        
        if result["success"]:
            print(f"✅ {test['description']} completed successfully")
        else:
            print(f"❌ {test['description']} failed")
            print(f"   Error: {result['stderr']}")
    
    # Generate combined report
    print("\n📊 Generating Combined Test Report")
    print("=" * 60)
    
    combined_report = generate_combined_report(results)
    
    # Save combined report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"combined_test_report_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(combined_report, f, indent=2)
    
    # Print summary
    summary = combined_report["summary"]
    print(f"📈 Overall Test Summary:")
    print(f"   Total Test Suites: {summary['total_test_suites']}")
    print(f"   Successful: {summary['successful_suites']} ✅")
    print(f"   Failed: {summary['failed_suites']} ❌")
    print(f"   Overall Success Rate: {summary['overall_success_rate']:.1f}%")
    print(f"\n📄 Combined report saved to: {filename}")
    
    # Print individual test results
    print(f"\n📋 Individual Test Results:")
    for i, result in enumerate(results, 1):
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"   {i}. {result['description']}: {status} ({result['duration']}s)")
    
    # Final assessment
    success_rate = summary['overall_success_rate']
    if success_rate >= 90:
        print("\n🎯 Excellent! All systems are working well.")
    elif success_rate >= 70:
        print("\n👍 Good! Most systems are working.")
    else:
        print("\n⚠️ Some systems need attention. Check the detailed reports.")
    
    return combined_report

if __name__ == "__main__":
    main() 