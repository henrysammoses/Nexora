#!/usr/bin/env python3
"""
Nexora Bank Comprehensive Backend API Testing Suite
Tests all API endpoints including new banking features: transactions, investments, loans, chat
"""

import requests
import sys
import json
from datetime import datetime
import uuid

class NexoraBankAPITester:
    def __init__(self, base_url="https://3092ed9a-1f76-4a56-b25b-666302ded7b6.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        
        # Test users data
        self.test_user1 = {
            "full_name": "John Doe",
            "email": f"john.test.{uuid.uuid4().hex[:8]}@nexora.com",
            "phone": "9876543210", 
            "password": "securepass123",
            "account_type": "savings"
        }
        
        self.test_user2 = {
            "full_name": "Jane Smith",
            "email": f"jane.test.{uuid.uuid4().hex[:8]}@nexora.com",
            "phone": "9876543211", 
            "password": "securepass456",
            "account_type": "current"
        }
        
        # Store user data after registration
        self.user1_data = None
        self.user2_data = None
        self.user2_token = None
        
        print(f"🏦 Nexora Bank Comprehensive API Testing Suite")
        print(f"📍 Testing against: {self.api_url}")
        print(f"👤 Test user 1: {self.test_user1['email']}")
        print(f"👤 Test user 2: {self.test_user2['email']}")
        print("=" * 80)

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
                response = requests.get(url, headers=test_headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=15)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"   ✅ PASSED - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(response_data) <= 5:
                        print(f"   📄 Response: {json.dumps(response_data, indent=2)}")
                    elif isinstance(response_data, list) and len(response_data) <= 3:
                        print(f"   📄 Response: {json.dumps(response_data, indent=2)}")
                    else:
                        print(f"   📄 Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else f'List with {len(response_data)} items'}")
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

    # ===== BASIC API TESTS =====
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
                if response.get('bank') == 'Nexora Bank':
                    print(f"   ✅ Bank name verified: {response['bank']}")
                else:
                    print(f"   ⚠️  Unexpected bank name: {response.get('bank')}")
            else:
                print(f"   ⚠️  Missing expected keys in health response")
        
        return success

    # ===== AUTHENTICATION TESTS =====
    def test_user1_registration(self):
        """Test user 1 registration"""
        success, response = self.run_test(
            "User 1 Registration",
            "POST",
            "auth/register", 
            200,
            data=self.test_user1
        )
        
        if success:
            expected_keys = ['access_token', 'token_type', 'user']
            if all(key in response for key in expected_keys):
                print(f"   ✅ Registration response contains all expected keys")
                
                # Store token and user data
                self.token = response['access_token']
                self.user1_data = response['user']
                
                # Verify user data
                user = response['user']
                if user['account_number'].startswith('NEX'):
                    print(f"   ✅ Account number format verified: {user['account_number']}")
                
                if user['balance'] == 10000.0:
                    print(f"   ✅ Starting balance verified: ₹{user['balance']}")
                    
            else:
                print(f"   ⚠️  Missing expected keys in registration response")
        
        return success

    def test_user2_registration(self):
        """Test user 2 registration (for transfer testing)"""
        success, response = self.run_test(
            "User 2 Registration",
            "POST",
            "auth/register", 
            200,
            data=self.test_user2
        )
        
        if success:
            self.user2_data = response['user']
            self.user2_token = response['access_token']
            print(f"   ✅ User 2 registered with account: {self.user2_data['account_number']}")
        
        return success

    def test_user1_login(self):
        """Test user 1 login"""
        login_data = {
            "email": self.test_user1['email'],
            "password": self.test_user1['password']
        }
        
        success, response = self.run_test(
            "User 1 Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success:
            self.token = response['access_token']
            print(f"   ✅ Login successful, token updated")
        
        return success

    # ===== DASHBOARD TESTS =====
    def test_dashboard_summary(self):
        """Test dashboard summary endpoint"""
        success, response = self.run_test(
            "Dashboard Summary",
            "GET",
            "dashboard/summary",
            200
        )
        
        if success:
            expected_keys = ['account_number', 'balance', 'account_type', 'user_name', 'total_investments', 'total_loans']
            if all(key in response for key in expected_keys):
                print(f"   ✅ Dashboard summary contains all expected keys")
                
                # Verify data matches user
                if response['user_name'] == self.test_user1['full_name']:
                    print(f"   ✅ User name verified: {response['user_name']}")
                
                if response['account_type'] == self.test_user1['account_type']:
                    print(f"   ✅ Account type verified: {response['account_type']}")
                    
            else:
                print(f"   ⚠️  Missing expected keys in dashboard response")
        
        return success

    # ===== TRANSACTION TESTS =====
    def test_money_transfer_valid(self):
        """Test valid money transfer"""
        if not self.user2_data:
            print(f"   ⚠️  User 2 data not available, skipping transfer test")
            return False
            
        transfer_data = {
            "recipient_account": self.user2_data['account_number'],
            "amount": 1000.0,
            "description": "Test transfer from user 1 to user 2"
        }
        
        success, response = self.run_test(
            "Valid Money Transfer",
            "POST",
            "transactions/transfer",
            200,
            data=transfer_data
        )
        
        if success:
            expected_keys = ['id', 'sender_account', 'recipient_account', 'amount', 'status']
            if all(key in response for key in expected_keys):
                print(f"   ✅ Transfer response contains all expected keys")
                
                if response['amount'] == 1000.0:
                    print(f"   ✅ Transfer amount verified: ₹{response['amount']}")
                
                if response['status'] == 'completed':
                    print(f"   ✅ Transfer status verified: {response['status']}")
                    
            else:
                print(f"   ⚠️  Missing expected keys in transfer response")
        
        return success

    def test_money_transfer_insufficient_balance(self):
        """Test money transfer with insufficient balance"""
        if not self.user2_data:
            print(f"   ⚠️  User 2 data not available, skipping insufficient balance test")
            return False
            
        transfer_data = {
            "recipient_account": self.user2_data['account_number'],
            "amount": 50000.0,  # More than starting balance
            "description": "Test insufficient balance transfer"
        }
        
        success, response = self.run_test(
            "Insufficient Balance Transfer (Should Fail)",
            "POST",
            "transactions/transfer",
            400,  # Expecting 400 Bad Request
            data=transfer_data
        )
        
        if success and 'detail' in response:
            if 'insufficient' in response['detail'].lower():
                print(f"   ✅ Insufficient balance properly rejected")
            else:
                print(f"   ⚠️  Unexpected error message: {response['detail']}")
        
        return success

    def test_money_transfer_invalid_recipient(self):
        """Test money transfer to invalid recipient"""
        transfer_data = {
            "recipient_account": "NEXINVALID123",
            "amount": 500.0,
            "description": "Test invalid recipient transfer"
        }
        
        success, response = self.run_test(
            "Invalid Recipient Transfer (Should Fail)",
            "POST",
            "transactions/transfer",
            404,  # Expecting 404 Not Found
            data=transfer_data
        )
        
        if success and 'detail' in response:
            if 'not found' in response['detail'].lower():
                print(f"   ✅ Invalid recipient properly rejected")
            else:
                print(f"   ⚠️  Unexpected error message: {response['detail']}")
        
        return success

    def test_transaction_history(self):
        """Test transaction history retrieval"""
        success, response = self.run_test(
            "Transaction History",
            "GET",
            "transactions",
            200
        )
        
        if success:
            if isinstance(response, list):
                print(f"   ✅ Transaction history returned as list with {len(response)} transactions")
                
                if len(response) > 0:
                    # Check first transaction structure
                    transaction = response[0]
                    expected_keys = ['id', 'sender_account', 'recipient_account', 'amount', 'transaction_type', 'status']
                    if all(key in transaction for key in expected_keys):
                        print(f"   ✅ Transaction structure verified")
                    else:
                        print(f"   ⚠️  Missing keys in transaction: {list(transaction.keys())}")
                        
            else:
                print(f"   ⚠️  Transaction history not returned as list")
        
        return success

    # ===== INVESTMENT TESTS =====
    def test_create_investment_mutual_fund(self):
        """Test creating a mutual fund investment"""
        investment_data = {
            "investment_type": "mutual_fund",
            "amount": 5000.0,
            "duration_months": 12
        }
        
        success, response = self.run_test(
            "Create Mutual Fund Investment",
            "POST",
            "investments",
            200,
            data=investment_data
        )
        
        if success:
            expected_keys = ['id', 'investment_type', 'amount', 'current_value', 'expected_return', 'maturity_date']
            if all(key in response for key in expected_keys):
                print(f"   ✅ Investment response contains all expected keys")
                
                if response['investment_type'] == 'mutual_fund':
                    print(f"   ✅ Investment type verified: {response['investment_type']}")
                
                if response['amount'] == 5000.0:
                    print(f"   ✅ Investment amount verified: ₹{response['amount']}")
                
                if response['expected_return'] > 0:
                    print(f"   ✅ Expected return calculated: ₹{response['expected_return']}")
                    
            else:
                print(f"   ⚠️  Missing expected keys in investment response")
        
        return success

    def test_create_investment_fixed_deposit(self):
        """Test creating a fixed deposit investment"""
        investment_data = {
            "investment_type": "fixed_deposit",
            "amount": 3000.0,
            "duration_months": 24
        }
        
        success, response = self.run_test(
            "Create Fixed Deposit Investment",
            "POST",
            "investments",
            200,
            data=investment_data
        )
        
        if success:
            if response['investment_type'] == 'fixed_deposit':
                print(f"   ✅ Fixed deposit investment created successfully")
        
        return success

    def test_investment_insufficient_balance(self):
        """Test investment with insufficient balance"""
        investment_data = {
            "investment_type": "equity",
            "amount": 20000.0,  # More than remaining balance
            "duration_months": 12
        }
        
        success, response = self.run_test(
            "Investment Insufficient Balance (Should Fail)",
            "POST",
            "investments",
            400,  # Expecting 400 Bad Request
            data=investment_data
        )
        
        if success and 'detail' in response:
            if 'insufficient' in response['detail'].lower():
                print(f"   ✅ Insufficient balance for investment properly rejected")
            else:
                print(f"   ⚠️  Unexpected error message: {response['detail']}")
        
        return success

    def test_get_investments(self):
        """Test retrieving user investments"""
        success, response = self.run_test(
            "Get User Investments",
            "GET",
            "investments",
            200
        )
        
        if success:
            if isinstance(response, list):
                print(f"   ✅ Investments returned as list with {len(response)} investments")
                
                if len(response) > 0:
                    # Check first investment structure
                    investment = response[0]
                    expected_keys = ['id', 'investment_type', 'amount', 'current_value', 'expected_return']
                    if all(key in investment for key in expected_keys):
                        print(f"   ✅ Investment structure verified")
                    else:
                        print(f"   ⚠️  Missing keys in investment: {list(investment.keys())}")
                        
            else:
                print(f"   ⚠️  Investments not returned as list")
        
        return success

    # ===== LOAN TESTS =====
    def test_apply_personal_loan(self):
        """Test applying for a personal loan"""
        loan_data = {
            "loan_type": "personal",
            "amount": 50000.0,
            "purpose": "Personal expenses",
            "duration_months": 24,
            "monthly_income": 30000.0
        }
        
        success, response = self.run_test(
            "Apply for Personal Loan",
            "POST",
            "loans/apply",
            200,
            data=loan_data
        )
        
        if success:
            expected_keys = ['id', 'loan_type', 'amount', 'purpose', 'interest_rate', 'emi', 'status']
            if all(key in response for key in expected_keys):
                print(f"   ✅ Loan application response contains all expected keys")
                
                if response['loan_type'] == 'personal':
                    print(f"   ✅ Loan type verified: {response['loan_type']}")
                
                if response['amount'] == 50000.0:
                    print(f"   ✅ Loan amount verified: ₹{response['amount']}")
                
                if response['emi'] > 0:
                    print(f"   ✅ EMI calculated: ₹{response['emi']}")
                
                if response['status'] == 'applied':
                    print(f"   ✅ Loan status verified: {response['status']}")
                    
            else:
                print(f"   ⚠️  Missing expected keys in loan response")
        
        return success

    def test_apply_home_loan(self):
        """Test applying for a home loan"""
        loan_data = {
            "loan_type": "home",
            "amount": 2000000.0,
            "purpose": "Home purchase",
            "duration_months": 240,  # 20 years
            "monthly_income": 80000.0
        }
        
        success, response = self.run_test(
            "Apply for Home Loan",
            "POST",
            "loans/apply",
            200,
            data=loan_data
        )
        
        if success:
            if response['loan_type'] == 'home':
                print(f"   ✅ Home loan application created successfully")
                print(f"   📊 EMI for ₹{response['amount']}: ₹{response['emi']}")
        
        return success

    def test_get_loans(self):
        """Test retrieving user loans"""
        success, response = self.run_test(
            "Get User Loans",
            "GET",
            "loans",
            200
        )
        
        if success:
            if isinstance(response, list):
                print(f"   ✅ Loans returned as list with {len(response)} loans")
                
                if len(response) > 0:
                    # Check first loan structure
                    loan = response[0]
                    expected_keys = ['id', 'loan_type', 'amount', 'interest_rate', 'emi', 'status']
                    if all(key in loan for key in expected_keys):
                        print(f"   ✅ Loan structure verified")
                    else:
                        print(f"   ⚠️  Missing keys in loan: {list(loan.keys())}")
                        
            else:
                print(f"   ⚠️  Loans not returned as list")
        
        return success

    # ===== CHAT TESTS =====
    def test_send_chat_message_general(self):
        """Test sending a general chat message"""
        chat_data = {
            "message": "What are your banking services?",
            "category": "general"
        }
        
        success, response = self.run_test(
            "Send General Chat Message",
            "POST",
            "chat",
            200,
            data=chat_data
        )
        
        if success:
            expected_keys = ['id', 'message', 'response', 'category', 'created_at']
            if all(key in response for key in expected_keys):
                print(f"   ✅ Chat response contains all expected keys")
                
                if response['message'] == chat_data['message']:
                    print(f"   ✅ Message verified: {response['message']}")
                
                if response['category'] == 'general':
                    print(f"   ✅ Category verified: {response['category']}")
                
                if len(response['response']) > 0:
                    print(f"   ✅ Response generated: {response['response'][:50]}...")
                    
            else:
                print(f"   ⚠️  Missing expected keys in chat response")
        
        return success

    def test_send_chat_message_loan(self):
        """Test sending a loan-related chat message"""
        chat_data = {
            "message": "Tell me about home loans",
            "category": "loan"
        }
        
        success, response = self.run_test(
            "Send Loan Chat Message",
            "POST",
            "chat",
            200,
            data=chat_data
        )
        
        if success:
            if response['category'] == 'loan':
                print(f"   ✅ Loan category chat message processed")
                if 'home loan' in response['response'].lower():
                    print(f"   ✅ Relevant loan response generated")
        
        return success

    def test_send_chat_message_investment(self):
        """Test sending an investment-related chat message"""
        chat_data = {
            "message": "What investment options do you have?",
            "category": "investment"
        }
        
        success, response = self.run_test(
            "Send Investment Chat Message",
            "POST",
            "chat",
            200,
            data=chat_data
        )
        
        if success:
            if response['category'] == 'investment':
                print(f"   ✅ Investment category chat message processed")
                if 'investment' in response['response'].lower():
                    print(f"   ✅ Relevant investment response generated")
        
        return success

    def test_get_chat_history(self):
        """Test retrieving chat history"""
        success, response = self.run_test(
            "Get Chat History",
            "GET",
            "chat/history",
            200
        )
        
        if success:
            if isinstance(response, list):
                print(f"   ✅ Chat history returned as list with {len(response)} messages")
                
                if len(response) > 0:
                    # Check first message structure
                    message = response[0]
                    expected_keys = ['id', 'message', 'response', 'category', 'created_at']
                    if all(key in message for key in expected_keys):
                        print(f"   ✅ Chat message structure verified")
                    else:
                        print(f"   ⚠️  Missing keys in chat message: {list(message.keys())}")
                        
            else:
                print(f"   ⚠️  Chat history not returned as list")
        
        return success

    # ===== MAIN TEST RUNNER =====
    def run_all_tests(self):
        """Run all API tests in sequence"""
        print(f"\n🚀 Starting Nexora Bank Comprehensive API Tests...")
        
        # Test sequence - organized by feature
        tests = [
            # Basic API Tests
            ("Health Check", self.test_health_check),
            
            # Authentication Tests
            ("User 1 Registration", self.test_user1_registration),
            ("User 2 Registration", self.test_user2_registration),
            ("User 1 Login", self.test_user1_login),
            
            # Dashboard Tests
            ("Dashboard Summary", self.test_dashboard_summary),
            
            # Transaction Tests
            ("Valid Money Transfer", self.test_money_transfer_valid),
            ("Insufficient Balance Transfer", self.test_money_transfer_insufficient_balance),
            ("Invalid Recipient Transfer", self.test_money_transfer_invalid_recipient),
            ("Transaction History", self.test_transaction_history),
            
            # Investment Tests
            ("Create Mutual Fund Investment", self.test_create_investment_mutual_fund),
            ("Create Fixed Deposit Investment", self.test_create_investment_fixed_deposit),
            ("Investment Insufficient Balance", self.test_investment_insufficient_balance),
            ("Get User Investments", self.test_get_investments),
            
            # Loan Tests
            ("Apply for Personal Loan", self.test_apply_personal_loan),
            ("Apply for Home Loan", self.test_apply_home_loan),
            ("Get User Loans", self.test_get_loans),
            
            # Chat Tests
            ("Send General Chat Message", self.test_send_chat_message_general),
            ("Send Loan Chat Message", self.test_send_chat_message_loan),
            ("Send Investment Chat Message", self.test_send_chat_message_investment),
            ("Get Chat History", self.test_get_chat_history),
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
        print("\n" + "=" * 80)
        print(f"📊 COMPREHENSIVE TEST RESULTS SUMMARY")
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
        
        print("=" * 80)
        
        return len(failed_tests) == 0

def main():
    """Main test execution"""
    tester = NexoraBankAPITester()
    
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