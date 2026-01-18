# Test Suite for Bootstrap Budget Tracker
# Created by: Otilia
# Tests for database operations, helper functions, and Flask routes

import pytest
import os
import sys
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, init_db, get_db
from helpers import (
    calculate_roi,
    calculate_budget_usage,
    check_budget_alert,
    calculate_ctr,
    calculate_conversion_rate,
    validate_date_range,
    validate_budget
)


# Fixtures
@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Use a separate test database
    test_db_path = os.path.join(app.instance_path, 'test_campaigns.db')
    app.config['DATABASE'] = test_db_path
    
    with app.test_client() as client:
        with app.app_context():
            # Initialize test database
            init_db()
        yield client
    
    # Cleanup: remove test database after tests
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def authenticated_client(client):
    """Create a client with an authenticated user"""
    # Register a test user
    client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'confirm_password': 'testpass123'
    })
    
    # Login the test user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    })
    
    return client


# ===========================
# HELPER FUNCTION TESTS
# ===========================

def test_calculate_roi_positive():
    """Test ROI calculation with positive return"""
    # 10 conversions * $50 = $500 revenue, spent $200
    # ROI = ((500 - 200) / 200) * 100 = 150%
    roi = calculate_roi(10, 200, 50)
    assert roi == 150.0


def test_calculate_roi_negative():
    """Test ROI calculation with negative return"""
    # 2 conversions * $50 = $100 revenue, spent $200
    # ROI = ((100 - 200) / 200) * 100 = -50%
    roi = calculate_roi(2, 200, 50)
    assert roi == -50.0


def test_calculate_roi_zero_spend():
    """Test ROI calculation when spend is zero"""
    roi = calculate_roi(10, 0, 50)
    assert roi == 0


def test_calculate_budget_usage():
    """Test budget usage percentage calculation"""
    usage = calculate_budget_usage(1000, 750)
    assert usage == 75.0


def test_calculate_budget_usage_over():
    """Test budget usage over 100%"""
    usage = calculate_budget_usage(1000, 1200)
    assert usage == 120.0


def test_calculate_budget_usage_zero_budget():
    """Test budget usage with zero budget"""
    usage = calculate_budget_usage(0, 100)
    assert usage == 0


def test_check_budget_alert_true():
    """Test budget alert when threshold is reached"""
    # 850 spent out of 1000 budget = 85%
    alert = check_budget_alert(1000, 850, 80)
    assert alert is True


def test_check_budget_alert_false():
    """Test budget alert when threshold is not reached"""
    # 700 spent out of 1000 budget = 70%
    alert = check_budget_alert(1000, 700, 80)
    assert alert is False


def test_calculate_ctr():
    """Test Click-Through Rate calculation"""
    # 100 clicks out of 10000 impressions = 1%
    ctr = calculate_ctr(100, 10000)
    assert ctr == 1.0


def test_calculate_ctr_zero_impressions():
    """Test CTR with zero impressions"""
    ctr = calculate_ctr(100, 0)
    assert ctr == 0


def test_calculate_conversion_rate():
    """Test conversion rate calculation"""
    # 10 conversions out of 200 clicks = 5%
    rate = calculate_conversion_rate(10, 200)
    assert rate == 5.0


def test_calculate_conversion_rate_zero_clicks():
    """Test conversion rate with zero clicks"""
    rate = calculate_conversion_rate(10, 0)
    assert rate == 0


def test_validate_date_range_valid():
    """Test valid date range (end after start)"""
    valid = validate_date_range('2026-01-01', '2026-01-31')
    assert valid is True


def test_validate_date_range_same_day():
    """Test date range with same start and end date"""
    valid = validate_date_range('2026-01-15', '2026-01-15')
    assert valid is True


def test_validate_date_range_invalid():
    """Test invalid date range (end before start)"""
    valid = validate_date_range('2026-01-31', '2026-01-01')
    assert valid is False


def test_validate_date_range_bad_format():
    """Test date validation with bad format"""
    valid = validate_date_range('not-a-date', '2026-01-01')
    assert valid is False


def test_validate_budget_valid():
    """Test budget validation with valid positive number"""
    assert validate_budget(500.50) is True
    assert validate_budget('1000') is True
    assert validate_budget(0.01) is True


def test_validate_budget_invalid():
    """Test budget validation with invalid values"""
    assert validate_budget(0) is False
    assert validate_budget(-100) is False
    assert validate_budget('not-a-number') is False
    assert validate_budget(None) is False


# ===========================
# FLASK ROUTE TESTS
# ===========================

def test_index_redirect_to_login(client):
    """Test that index redirects to login when not authenticated"""
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location


def test_register_page_loads(client):
    """Test that registration page loads"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Create Your Account' in response.data


def test_register_user_success(client):
    """Test successful user registration"""
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful' in response.data


def test_register_password_mismatch(client):
    """Test registration with mismatched passwords"""
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'different123'
    }, follow_redirects=True)
    
    assert b'Passwords do not match' in response.data


def test_register_duplicate_username(client):
    """Test registration with existing username"""
    # First registration
    client.post('/register', data={
        'username': 'duplicate',
        'email': 'first@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    
    # Try to register again with same username
    response = client.post('/register', data={
        'username': 'duplicate',
        'email': 'second@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert b'already exists' in response.data


def test_login_page_loads(client):
    """Test that login page loads"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login to Your Account' in response.data


def test_login_success(client):
    """Test successful login"""
    # Register user first
    client.post('/register', data={
        'username': 'logintest',
        'email': 'login@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    
    # Login
    response = client.post('/login', data={
        'username': 'logintest',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Welcome back' in response.data


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/login', data={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert b'Invalid username or password' in response.data


def test_logout(authenticated_client):
    """Test user logout"""
    response = authenticated_client.get('/logout', follow_redirects=True)
    assert b'logged out' in response.data


def test_dashboard_requires_login(client):
    """Test that dashboard requires authentication"""
    response = client.get('/dashboard', follow_redirects=True)
    assert b'Please log in' in response.data


def test_dashboard_loads_for_authenticated_user(authenticated_client):
    """Test that dashboard loads for logged-in user"""
    response = authenticated_client.get('/dashboard')
    assert response.status_code == 200
    assert b'Your Marketing Campaigns' in response.data


def test_create_campaign_page_loads(authenticated_client):
    """Test that create campaign page loads"""
    response = authenticated_client.get('/campaign/create')
    assert response.status_code == 200
    assert b'Create New Campaign' in response.data


def test_create_campaign_success(authenticated_client):
    """Test successful campaign creation"""
    response = authenticated_client.post('/campaign/create', data={
        'name': 'Test Campaign',
        'budget': '500.00',
        'channel': 'Instagram',
        'start_date': '2026-02-01',
        'end_date': '2026-02-28'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Campaign created successfully' in response.data
    assert b'Test Campaign' in response.data


def test_create_campaign_invalid_budget(authenticated_client):
    """Test campaign creation with invalid budget"""
    response = authenticated_client.post('/campaign/create', data={
        'name': 'Bad Budget Campaign',
        'budget': '-100',
        'channel': 'Facebook',
        'start_date': '2026-02-01',
        'end_date': '2026-02-28'
    }, follow_redirects=True)
    
    assert b'Budget must be a positive number' in response.data


def test_create_campaign_missing_fields(authenticated_client):
    """Test campaign creation with missing required fields"""
    response = authenticated_client.post('/campaign/create', data={
        'name': 'Incomplete Campaign',
        'budget': '500'
        # Missing channel and dates
    }, follow_redirects=True)
    
    assert b'All fields are required' in response.data


# ===========================
# DATABASE TESTS
# ===========================

def test_database_initialization(client):
    """Test that database tables are created"""
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if users table exists
        result = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        ).fetchone()
        assert result is not None
        
        # Check if campaigns table exists
        result = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='campaigns'"
        ).fetchone()
        assert result is not None
        
        # Check if metrics table exists
        result = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='metrics'"
        ).fetchone()
        assert result is not None
        
        conn.close()


def test_user_insertion(client):
    """Test that users can be inserted into database"""
    with app.app_context():
        from werkzeug.security import generate_password_hash
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            ('dbtest', 'db@test.com', generate_password_hash('password'))
        )
        conn.commit()
        
        # Verify user was inserted
        user = cursor.execute(
            'SELECT * FROM users WHERE username = ?', ('dbtest',)
        ).fetchone()
        
        assert user is not None
        assert user['email'] == 'db@test.com'
        
        conn.close()


# Run tests with: pytest test_app.py -v
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
