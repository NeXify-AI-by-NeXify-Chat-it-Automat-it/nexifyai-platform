"""
NeXifyAI Admin Calendar Management Tests
Tests for: Admin login, calendar data, booking CRUD, blocked slots, customers
"""
import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "NxAi#Secure2026!"


class TestAdminAuth:
    """Admin authentication tests"""
    
    def test_admin_login_success(self):
        """POST /api/admin/login - successful login"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD.replace('#', '%23').replace('!', '%21')}"
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
        print(f"✓ Admin login successful, token received")
    
    def test_admin_login_invalid_credentials(self):
        """POST /api/admin/login - invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data="username=wrong@example.com&password=wrongpassword"
        )
        assert response.status_code == 401
        print(f"✓ Invalid credentials correctly rejected")


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/admin/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD.replace('#', '%23').replace('!', '%21')}"
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    pytest.skip("Admin authentication failed")


@pytest.fixture
def auth_headers(admin_token):
    """Headers with auth token"""
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }


class TestAdminStats:
    """Admin dashboard stats tests"""
    
    def test_admin_stats(self, auth_headers):
        """GET /api/admin/stats - dashboard statistics"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify stats structure
        assert "total_leads" in data
        assert "new_leads_today" in data
        assert "new_leads_week" in data
        assert "upcoming_bookings" in data
        assert "by_status" in data
        
        # Verify data types
        assert isinstance(data["total_leads"], int)
        assert isinstance(data["upcoming_bookings"], int)
        print(f"✓ Stats: {data['total_leads']} leads, {data['upcoming_bookings']} upcoming bookings")


class TestAdminCalendarData:
    """Admin calendar data tests"""
    
    def test_calendar_data_current_month(self, auth_headers):
        """GET /api/admin/calendar-data - current month data"""
        current_month = datetime.now().strftime("%Y-%m")
        response = requests.get(
            f"{BASE_URL}/api/admin/calendar-data?month={current_month}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "bookings" in data
        assert "blocked_slots" in data
        assert "month" in data
        assert data["month"] == current_month
        assert isinstance(data["bookings"], list)
        assert isinstance(data["blocked_slots"], list)
        print(f"✓ Calendar data: {len(data['bookings'])} bookings, {len(data['blocked_slots'])} blocked slots")
    
    def test_calendar_data_april_2026(self, auth_headers):
        """GET /api/admin/calendar-data - April 2026 (test data month)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/calendar-data?month=2026-04",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify existing test data
        assert len(data["bookings"]) >= 2, "Expected at least 2 bookings in April 2026"
        
        # Verify booking structure
        if data["bookings"]:
            booking = data["bookings"][0]
            assert "booking_id" in booking
            assert "date" in booking
            assert "time" in booking
            assert "vorname" in booking
            assert "nachname" in booking
            assert "email" in booking
            assert "status" in booking
        
        # Verify blocked slot structure
        if data["blocked_slots"]:
            slot = data["blocked_slots"][0]
            assert "slot_id" in slot
            assert "date" in slot
            assert "all_day" in slot
        
        print(f"✓ April 2026: {len(data['bookings'])} bookings, {len(data['blocked_slots'])} blocked slots")


class TestAdminBookings:
    """Admin booking CRUD tests"""
    
    def test_get_bookings_list(self, auth_headers):
        """GET /api/admin/bookings - list all bookings"""
        response = requests.get(f"{BASE_URL}/api/admin/bookings", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "total" in data
        assert "bookings" in data
        assert isinstance(data["bookings"], list)
        print(f"✓ Bookings list: {data['total']} total")
    
    def test_update_booking_status(self, auth_headers):
        """PATCH /api/admin/bookings/:id - update booking status"""
        # First get a booking
        response = requests.get(f"{BASE_URL}/api/admin/bookings", headers=auth_headers)
        bookings = response.json().get("bookings", [])
        
        if not bookings:
            pytest.skip("No bookings available for testing")
        
        booking_id = bookings[0]["booking_id"]
        original_status = bookings[0]["status"]
        
        # Update status to 'completed'
        new_status = "completed" if original_status != "completed" else "confirmed"
        response = requests.patch(
            f"{BASE_URL}/api/admin/bookings/{booking_id}",
            headers=auth_headers,
            json={"status": new_status}
        )
        assert response.status_code == 200
        assert response.json()["success"] == True
        
        # Verify the update
        response = requests.get(f"{BASE_URL}/api/admin/bookings/{booking_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == new_status
        
        # Restore original status
        requests.patch(
            f"{BASE_URL}/api/admin/bookings/{booking_id}",
            headers=auth_headers,
            json={"status": original_status}
        )
        print(f"✓ Booking status update: {original_status} → {new_status} → {original_status}")
    
    def test_add_booking_notes(self, auth_headers):
        """PATCH /api/admin/bookings/:id - add notes to booking"""
        # Get a booking
        response = requests.get(f"{BASE_URL}/api/admin/bookings", headers=auth_headers)
        bookings = response.json().get("bookings", [])
        
        if not bookings:
            pytest.skip("No bookings available for testing")
        
        booking_id = bookings[0]["booking_id"]
        test_note = f"TEST_Note_{datetime.now().strftime('%H%M%S')}"
        
        response = requests.patch(
            f"{BASE_URL}/api/admin/bookings/{booking_id}",
            headers=auth_headers,
            json={"notes": test_note}
        )
        assert response.status_code == 200
        
        # Verify note was added
        response = requests.get(f"{BASE_URL}/api/admin/bookings/{booking_id}", headers=auth_headers)
        booking = response.json()
        assert "notes" in booking
        # Notes should be a list with the new note
        if isinstance(booking["notes"], list) and booking["notes"]:
            assert any(test_note in str(n) for n in booking["notes"])
        print(f"✓ Booking note added: {test_note}")


class TestAdminBlockedSlots:
    """Admin blocked slots CRUD tests"""
    
    def test_create_blocked_slot(self, auth_headers):
        """POST /api/admin/blocked-slots - create blocked slot"""
        # Create a blocked slot for a future date
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        response = requests.post(
            f"{BASE_URL}/api/admin/blocked-slots",
            headers=auth_headers,
            json={
                "date": future_date,
                "time": "14:00",
                "reason": "TEST_Blocked_Slot",
                "all_day": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "slot_id" in data
        assert data["date"] == future_date
        assert data["time"] == "14:00"
        assert data["reason"] == "TEST_Blocked_Slot"
        assert data["all_day"] == False
        
        # Store slot_id for cleanup
        TestAdminBlockedSlots.test_slot_id = data["slot_id"]
        print(f"✓ Blocked slot created: {data['slot_id']}")
    
    def test_create_all_day_blocked_slot(self, auth_headers):
        """POST /api/admin/blocked-slots - create all-day blocked slot"""
        future_date = (datetime.now() + timedelta(days=31)).strftime("%Y-%m-%d")
        
        response = requests.post(
            f"{BASE_URL}/api/admin/blocked-slots",
            headers=auth_headers,
            json={
                "date": future_date,
                "reason": "TEST_All_Day_Block",
                "all_day": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["all_day"] == True
        TestAdminBlockedSlots.all_day_slot_id = data["slot_id"]
        print(f"✓ All-day blocked slot created: {data['slot_id']}")
    
    def test_blocked_slots_affect_public_api(self, auth_headers):
        """GET /api/booking/slots - blocked slots should not appear"""
        # Get the date of the all-day blocked slot
        future_date = (datetime.now() + timedelta(days=31)).strftime("%Y-%m-%d")
        
        response = requests.get(f"{BASE_URL}/api/booking/slots?date={future_date}")
        assert response.status_code == 200
        data = response.json()
        
        # All-day block should return empty slots
        assert data["slots"] == [], f"Expected empty slots for all-day blocked date, got: {data['slots']}"
        print(f"✓ All-day blocked slot correctly blocks all slots")
    
    def test_delete_blocked_slot(self, auth_headers):
        """DELETE /api/admin/blocked-slots/:id - delete blocked slot"""
        if not hasattr(TestAdminBlockedSlots, 'test_slot_id'):
            pytest.skip("No test slot to delete")
        
        slot_id = TestAdminBlockedSlots.test_slot_id
        response = requests.delete(
            f"{BASE_URL}/api/admin/blocked-slots/{slot_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["success"] == True
        print(f"✓ Blocked slot deleted: {slot_id}")
    
    def test_cleanup_all_day_slot(self, auth_headers):
        """Cleanup: delete all-day blocked slot"""
        if not hasattr(TestAdminBlockedSlots, 'all_day_slot_id'):
            pytest.skip("No all-day slot to delete")
        
        slot_id = TestAdminBlockedSlots.all_day_slot_id
        response = requests.delete(
            f"{BASE_URL}/api/admin/blocked-slots/{slot_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        print(f"✓ All-day blocked slot cleaned up: {slot_id}")


class TestAdminCustomers:
    """Admin customer management tests"""
    
    def test_get_customers_list(self, auth_headers):
        """GET /api/admin/customers - aggregated customer list"""
        response = requests.get(f"{BASE_URL}/api/admin/customers", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "customers" in data
        assert isinstance(data["customers"], list)
        
        if data["customers"]:
            customer = data["customers"][0]
            assert "email" in customer
            assert "vorname" in customer
            assert "nachname" in customer
            assert "total_leads" in customer
            assert "total_bookings" in customer
            assert "first_contact" in customer
            assert "last_contact" in customer
        
        print(f"✓ Customers list: {len(data['customers'])} customers")
    
    def test_customers_search(self, auth_headers):
        """GET /api/admin/customers?search= - search customers"""
        response = requests.get(
            f"{BASE_URL}/api/admin/customers?search=test",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        print(f"✓ Customer search: {len(data['customers'])} results for 'test'")
    
    def test_customer_detail(self, auth_headers):
        """GET /api/admin/customers/:email - customer detail with history"""
        # First get a customer
        response = requests.get(f"{BASE_URL}/api/admin/customers", headers=auth_headers)
        customers = response.json().get("customers", [])
        
        if not customers:
            pytest.skip("No customers available for testing")
        
        email = customers[0]["email"]
        response = requests.get(
            f"{BASE_URL}/api/admin/customers/{email}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "leads" in data
        assert "bookings" in data
        assert isinstance(data["leads"], list)
        assert isinstance(data["bookings"], list)
        print(f"✓ Customer detail: {len(data['leads'])} leads, {len(data['bookings'])} bookings")


class TestAdminLeads:
    """Admin leads management tests"""
    
    def test_get_leads_list(self, auth_headers):
        """GET /api/admin/leads - list all leads"""
        response = requests.get(f"{BASE_URL}/api/admin/leads", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "total" in data
        assert "leads" in data
        assert isinstance(data["leads"], list)
        print(f"✓ Leads list: {data['total']} total")
    
    def test_leads_search(self, auth_headers):
        """GET /api/admin/leads?search= - search leads"""
        response = requests.get(
            f"{BASE_URL}/api/admin/leads?search=test",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "leads" in data
        print(f"✓ Leads search: {len(data['leads'])} results for 'test'")
    
    def test_leads_filter_by_status(self, auth_headers):
        """GET /api/admin/leads?status= - filter by status"""
        response = requests.get(
            f"{BASE_URL}/api/admin/leads?status=neu",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # All returned leads should have status 'neu'
        for lead in data["leads"]:
            assert lead["status"] == "neu"
        print(f"✓ Leads filter: {len(data['leads'])} leads with status 'neu'")
    
    def test_update_lead_status(self, auth_headers):
        """PATCH /api/admin/leads/:id - update lead status"""
        # Get a lead
        response = requests.get(f"{BASE_URL}/api/admin/leads", headers=auth_headers)
        leads = response.json().get("leads", [])
        
        if not leads:
            pytest.skip("No leads available for testing")
        
        lead_id = leads[0]["lead_id"]
        original_status = leads[0]["status"]
        
        # Update status
        new_status = "kontaktiert" if original_status != "kontaktiert" else "neu"
        response = requests.patch(
            f"{BASE_URL}/api/admin/leads/{lead_id}",
            headers=auth_headers,
            json={"status": new_status}
        )
        assert response.status_code == 200
        
        # Restore original status
        requests.patch(
            f"{BASE_URL}/api/admin/leads/{lead_id}",
            headers=auth_headers,
            json={"status": original_status}
        )
        print(f"✓ Lead status update: {original_status} → {new_status} → {original_status}")


class TestBookingStatusValues:
    """Test all booking status values"""
    
    @pytest.mark.parametrize("status", [
        "confirmed", "pending", "completed", "cancelled", "no_show", "rescheduled"
    ])
    def test_booking_status_values(self, auth_headers, status):
        """PATCH /api/admin/bookings/:id - test all status values"""
        # Get a booking
        response = requests.get(f"{BASE_URL}/api/admin/bookings", headers=auth_headers)
        bookings = response.json().get("bookings", [])
        
        if not bookings:
            pytest.skip("No bookings available for testing")
        
        booking_id = bookings[0]["booking_id"]
        original_status = bookings[0]["status"]
        
        # Update to test status
        response = requests.patch(
            f"{BASE_URL}/api/admin/bookings/{booking_id}",
            headers=auth_headers,
            json={"status": status}
        )
        assert response.status_code == 200
        
        # Verify
        response = requests.get(f"{BASE_URL}/api/admin/bookings/{booking_id}", headers=auth_headers)
        assert response.json()["status"] == status
        
        # Restore
        requests.patch(
            f"{BASE_URL}/api/admin/bookings/{booking_id}",
            headers=auth_headers,
            json={"status": original_status}
        )
        print(f"✓ Booking status '{status}' works correctly")


class TestAdminLogout:
    """Admin logout/token invalidation tests"""
    
    def test_unauthorized_access(self):
        """Verify endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 401
        print(f"✓ Unauthorized access correctly rejected")
    
    def test_invalid_token(self):
        """Verify invalid token is rejected"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        assert response.status_code == 401
        print(f"✓ Invalid token correctly rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
