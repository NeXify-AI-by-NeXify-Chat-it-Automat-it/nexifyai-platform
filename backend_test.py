#!/usr/bin/env python3
"""
Backend API Testing for NeXifyAI Landing Page
Tests health endpoint and contact form submission
"""
import requests
import sys
from datetime import datetime

class NeXifyAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {response_data}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        return self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )

    def test_company_data_endpoint(self):
        """Test the company data endpoint"""
        return self.run_test(
            "Company Data",
            "GET", 
            "api/company",
            200
        )

    def test_contact_form_valid(self):
        """Test contact form with valid data"""
        valid_data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "email": "max.mustermann@example.com",
            "nachricht": "Ich interessiere mich für Ihre KI-Lösungen und möchte gerne mehr erfahren."
        }
        return self.run_test(
            "Contact Form - Valid Data",
            "POST",
            "api/contact",
            200,
            data=valid_data
        )

    def test_contact_form_invalid_email(self):
        """Test contact form with invalid email"""
        invalid_data = {
            "vorname": "Max",
            "nachname": "Mustermann", 
            "email": "invalid-email",
            "nachricht": "Test message with invalid email"
        }
        return self.run_test(
            "Contact Form - Invalid Email",
            "POST",
            "api/contact",
            422,  # Validation error
            data=invalid_data
        )

    def test_contact_form_short_name(self):
        """Test contact form with too short name"""
        invalid_data = {
            "vorname": "A",  # Too short
            "nachname": "Mustermann",
            "email": "test@example.com",
            "nachricht": "Test message with short name"
        }
        return self.run_test(
            "Contact Form - Short Name",
            "POST",
            "api/contact",
            422,  # Validation error
            data=invalid_data
        )

    def test_contact_form_short_message(self):
        """Test contact form with too short message"""
        invalid_data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "email": "test@example.com",
            "nachricht": "Short"  # Too short
        }
        return self.run_test(
            "Contact Form - Short Message",
            "POST",
            "api/contact",
            422,  # Validation error
            data=invalid_data
        )

    def test_newsletter_subscription(self):
        """Test newsletter subscription"""
        newsletter_data = {
            "email": "newsletter@example.com"
        }
        return self.run_test(
            "Newsletter Subscription",
            "POST",
            "api/newsletter",
            200,
            data=newsletter_data
        )

def main():
    print("🚀 Starting NeXifyAI Backend API Tests")
    print("=" * 50)
    
    # Test with localhost
    tester = NeXifyAPITester("http://localhost:8001")
    
    # Run all tests
    tests = [
        tester.test_health_endpoint,
        tester.test_company_data_endpoint,
        tester.test_contact_form_valid,
        tester.test_contact_form_invalid_email,
        tester.test_contact_form_short_name,
        tester.test_contact_form_short_message,
        tester.test_newsletter_subscription
    ]
    
    for test in tests:
        test()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())