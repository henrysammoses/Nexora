#!/usr/bin/env python3
"""
Nexorwa Bank Backend API Testing Suite
Tests all API endpoints with JWT authentication
"""

import requests
import sys
import json
from datetime import datetime
import uuid

class NexorwaBankAPITester:
    def __init__(self, base_url="https://3092ed9a-1f76-4a56-b25b-666302ded7b6.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        
        # Test user data
        self.test_user = {
            "full_name": "John Doe",
            "email": f"john.test.{uuid.uuid4().hex[:8]}@nexorwa.com",
            "phone": "9876543210", 
            "password": "securepass123",
            "account_type": "savings"
        }
        
        print(f"🏦 Nexorwa Bank API Testing Suite")
        print(f"📍 Testing against: {self.api_url}")
        print(f"👤 Test user email: {self.test_user['email']}")
        print("=" * 60)

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
            
        if self.token and 'Authorization' not in test_headers:
            test_headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        print(f"   {method} {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"   ✅ PASSED - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(response_data) <= 5:
                        print(f"   📄 Response: {json.dumps(response_data, indent=2)}")
                    else:
                        print(f"   📄 Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                except:
                    print(f"   📄 Response: {response.text[:100]}...")
            else:
                print(f"   ❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📄 Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   📄 Error: {response.text}")

            return success, response.json() if response.text else {}

        except requests.exceptions.RequestException as e:
            print(f"   ❌ FAILED - Network Error: {str(e)}")
            return False, {}
        except Exception as e:
            print(f"   ❌ FAILED - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET", 
            "health",
            200
        )
        
        if success:
            expected_keys = ['status', 'bank', 'version']
            if all(key in response for key in expected_keys):
                print(f"   ✅ Health check response contains all expected keys")
                if response.get('bank') == 'Nexorwa Bank':
                    print(f"   ✅ Bank name verified: {response['bank']}")
                else:
                    print(f"   ⚠️  Unexpected bank name: {response.get('bank')}")
            else:
                print(f"   ⚠️  Missing expected keys in health response")
        
        return success

    def test_user_registration(self):
        """Test user registration"""
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register", 
            200,
            data=self.test_user
        )
        
        if success:
            # Check response structure
            expected_keys = ['access_token', 'token_type', 'user']
            if all(key in response for key in expected_keys):
                print(f"   ✅ Registration response contains all expected keys")
                
                # Store token and user data
                self.token = response['access_token']
                self.user_data = response['user']
                
                # Verify token type
                if response['token_type'] == 'bearer':
                    print(f"   ✅ Token type verified: {response['token_type']}")
                else:
                    print(f"   ⚠️  Unexpected token type: {response['token_type']}")
                
                # Verify user data
                user = response['user']
                if user['email'] == self.test_user['email']:
                    print(f"   ✅ User email verified: {user['email']}")
                else:
                    print(f"   ⚠️  Email mismatch: expected {self.test_user['email']}, got {user['email']}")
                
                if user['account_number'].startswith('NEX'):
                    print(f"   ✅ Account number format verified: {user['account_number']}")
                else:
                    print(f"   ⚠️  Account number format issue: {user['account_number']}")
                
                if user['balance'] == 10000.0:
                    print(f"   ✅ Starting balance verified: ₹{user['balance']}")
                else:
                    print(f"   ⚠️  Unexpected starting balance: ₹{user['balance']}")
                    
            else:
                print(f"   ⚠️  Missing expected keys in registration response")
        
        return success

    def test_duplicate_registration(self):
        """Test duplicate email registration (should fail)"""
        success, response = self.run_test(
            "Duplicate Registration (Should Fail)",
            "POST",
            "auth/register",
            400,  # Expecting 400 Bad Request
            data=self.test_user
        )
        
        if success and 'detail' in response:
            if 'already registered' in response['detail'].lower():
                print(f"   ✅ Duplicate registration properly rejected")
            else:
                print(f"   ⚠️  Unexpected error message: {response['detail']}")
        
        return success

    def test_user_login(self):
        """Test user login"""
        login_data = {
            "email": self.test_user['email'],
            "password": self.test_user['password']
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success:
            # Verify response structure (same as registration)
            expected_keys = ['access_token', 'token_type', 'user']
            if all(key in response for key in expected_keys):
                print(f"   ✅ Login response contains all expected keys")
                
                # Update token (should be new)
                new_token = response['access_token']
                if new_token != self.token:
                    print(f"   ✅ New token generated on login")
                    self.token = new_token
                else:
                    print(f"   ⚠️  Same token returned (might be cached)")
                
            else:
                print(f"   ⚠️  Missing expected keys in login response")
        
        return success

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        invalid_login = {
            "email": self.test_user['email'],
            "password": "wrongpassword"
        }
        
        success, response = self.run_test(
            "Invalid Login (Should Fail)",
            "POST",
            "auth/login",
            401,  # Expecting 401 Unauthorized
            data=invalid_login
        )
        
        if success and 'detail' in response:
            if 'invalid' in response['detail'].lower():
                print(f"   ✅ Invalid login properly rejected")
            else:
                print(f"   ⚠️  Unexpected error message: {response['detail']}")
        
        return success

    def test_protected_route_me(self):
        """Test protected route /auth/me"""
        success, response = self.run_test(
            "Get Current User (/auth/me)",
            "GET",
            "auth/me",
            200
        )
        
        if success:
            # Verify user data matches what we registered
            if response['email'] == self.test_user['email']:
                print(f"   ✅ User data verified via /auth/me")
            else:
                print(f"   ⚠️  User data mismatch in /auth/me")
        
        return success

    def test_protected_route_without_token(self):
        """Test protected route without token (should fail)"""
        # Temporarily remove token
        temp_token = self.token
        self.token = None
        
        success, response = self.run_test(
            "Protected Route Without Token (Should Fail)",
            "GET",
            "auth/me",
            401  # Expecting 401 Unauthorized
        )
        
        # Restore token
        self.token = temp_token
        
        if success and 'detail' in response:
            print(f"   ✅ Protected route properly secured")
        
        return success

    def test_protected_route_invalid_token(self):
        """Test protected route with invalid token"""
        # Use invalid token
        headers = {'Authorization': 'Bearer invalid_token_here'}
        
        success, response = self.run_test(
            "Protected Route With Invalid Token (Should Fail)",
            "GET",
            "auth/me",
            401,  # Expecting 401 Unauthorized
            headers=headers
        )
        
        if success:
            print(f"   ✅ Invalid token properly rejected")
        
        return success

    def test_dashboard_summary(self):
        """Test dashboard summary endpoint"""
        success, response = self.run_test(
            "Dashboard Summary",
            "GET",
            "dashboard/summary",
            200
        )
        
        if success:
            expected_keys = ['account_number', 'balance', 'account_type', 'user_name']
            if all(key in response for key in expected_keys):
                print(f"   ✅ Dashboard summary contains all expected keys")
                
                # Verify data matches user
                if response['user_name'] == self.test_user['full_name']:
                    print(f"   ✅ User name verified: {response['user_name']}")
                else:
                    print(f"   ⚠️  User name mismatch: {response['user_name']}")
                
                if response['account_type'] == self.test_user['account_type']:
                    print(f"   ✅ Account type verified: {response['account_type']}")
                else:
                    print(f"   ⚠️  Account type mismatch: {response['account_type']}")
                    
            else:
                print(f"   ⚠️  Missing expected keys in dashboard response")
        
        return success

    def test_logout(self):
        """Test logout endpoint"""
        success, response = self.run_test(
            "User Logout",
            "POST",
            "auth/logout",
            200
        )
        
        if success and 'message' in response:
            if 'logged out' in response['message'].lower():
                print(f"   ✅ Logout successful")
            else:
                print(f"   ⚠️  Unexpected logout message: {response['message']}")
        
        return success

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print(f"\n🚀 Starting Nexorwa Bank API Tests...")
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_user_registration),
            ("Duplicate Registration", self.test_duplicate_registration),
            ("User Login", self.test_user_login),
            ("Invalid Login", self.test_invalid_login),
            ("Protected Route (/auth/me)", self.test_protected_route_me),
            ("Protected Route Without Token", self.test_protected_route_without_token),
            ("Protected Route Invalid Token", self.test_protected_route_invalid_token),
            ("Dashboard Summary", self.test_dashboard_summary),
            ("User Logout", self.test_logout),
        ]
        
        failed_tests = []
        
        for test_name, test_func in tests:
            try:
                if not test_func():
                    failed_tests.append(test_name)
            except Exception as e:
                print(f"   ❌ EXCEPTION in {test_name}: {str(e)}")
                failed_tests.append(test_name)
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 TEST RESULTS SUMMARY")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   - {test}")
        else:
            print(f"\n🎉 ALL TESTS PASSED!")
        
        print("=" * 60)
        
        return len(failed_tests) == 0

def main():
    """Main test execution"""
    tester = NexorwaBankAPITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print(f"\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())