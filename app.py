# Bootstrap Budget Tracker - Main Application
# Created by: Otilia
# A marketing campaign manager for small businesses

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Database configuration
DATABASE = os.path.join(app.instance_path, 'campaigns.db')

# Ensure instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# Initialize database on startup
with app.app_context():
    init_db_on_startup = True


# Database helper functions
def get_db():
    """Connect to the database"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def init_db():
    """Initialize the database with tables"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

        # Campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                budget REAL NOT NULL,
                channel TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                date DATE NOT NULL,
                impressions INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                spend REAL DEFAULT 0.0,
                FOREIGN KEY (campaign_id) REFERENCES campaigns (id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        conn.close()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")


# Login required decorator
def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Routes
@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in, otherwise to login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')
        
        # Hash password and save user
        password_hash = generate_password_hash(password)
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            conn.close()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('login.html')
        
        conn = get_db()
        cursor = conn.cursor()
        user = cursor.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard showing all campaigns"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get filter parameters from URL
    filter_channel = request.args.get('channel', '')
    filter_status = request.args.get('status', '')
    
    # Build SQL query with filters
    query = '''
        SELECT c.*, 
               COALESCE(SUM(m.spend), 0) as total_spend,
               COALESCE(SUM(m.impressions), 0) as total_impressions,
               COALESCE(SUM(m.clicks), 0) as total_clicks,
               COALESCE(SUM(m.conversions), 0) as total_conversions
        FROM campaigns c
        LEFT JOIN metrics m ON c.id = m.campaign_id
        WHERE c.user_id = ?
    '''
    
    params = [session['user_id']]
    
    # Add filters if provided
    if filter_channel:
        query += ' AND c.channel = ?'
        params.append(filter_channel)
    
    if filter_status:
        query += ' AND c.status = ?'
        params.append(filter_status)
    
    query += ' GROUP BY c.id ORDER BY c.created_at DESC'
    
    campaigns = cursor.execute(query, params).fetchall()
    
    conn.close()
    
    # Calculate ROI for each campaign
    campaigns_with_roi = []
    for campaign in campaigns:
        campaign_dict = dict(campaign)
        
        # Calculate ROI
        if campaign_dict['total_spend'] > 0 and campaign_dict['total_conversions'] > 0:
            # Simplified ROI: (conversions - spend) / spend * 100
            roi = ((campaign_dict['total_conversions'] * 50 - campaign_dict['total_spend']) / campaign_dict['total_spend']) * 100
            campaign_dict['roi'] = round(roi, 2)
        else:
            campaign_dict['roi'] = 0
        
        # Calculate budget usage percentage
        if campaign_dict['budget'] > 0:
            budget_used = (campaign_dict['total_spend'] / campaign_dict['budget']) * 100
            campaign_dict['budget_used_percent'] = round(budget_used, 2)
        else:
            campaign_dict['budget_used_percent'] = 0
        
        campaigns_with_roi.append(campaign_dict)
    
    return render_template('dashboard.html', campaigns=campaigns_with_roi)


@app.route('/campaign/create', methods=['GET', 'POST'])
@login_required
def create_campaign():
    """Create a new campaign"""
    if request.method == 'POST':
        name = request.form.get('name')
        budget = request.form.get('budget')
        channel = request.form.get('channel')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        # Validation
        if not all([name, budget, channel, start_date, end_date]):
            flash('All fields are required.', 'danger')
            return render_template('create_campaign.html')
        
        try:
            budget = float(budget)
            if budget <= 0:
                raise ValueError
        except ValueError:
            flash('Budget must be a positive number.', 'danger')
            return render_template('create_campaign.html')
        
        # Save campaign
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO campaigns (user_id, name, budget, channel, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], name, budget, channel, start_date, end_date))
        conn.commit()
        conn.close()
        
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('create_campaign.html')


@app.route('/campaign/<int:campaign_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_campaign(campaign_id):
    """Edit an existing campaign"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get campaign (ensure it belongs to logged-in user)
    campaign = cursor.execute('''
        SELECT * FROM campaigns WHERE id = ? AND user_id = ?
    ''', (campaign_id, session['user_id'])).fetchone()
    
    if not campaign:
        conn.close()
        flash('Campaign not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        budget = request.form.get('budget')
        channel = request.form.get('channel')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        status = request.form.get('status')
        
        # Validation
        if not all([name, budget, channel, start_date, end_date, status]):
            flash('All fields are required.', 'danger')
            return render_template('edit_campaign.html', campaign=campaign)
        
        try:
            budget = float(budget)
            if budget <= 0:
                raise ValueError
        except ValueError:
            flash('Budget must be a positive number.', 'danger')
            return render_template('edit_campaign.html', campaign=campaign)
        
        # Update campaign
        cursor.execute('''
            UPDATE campaigns 
            SET name = ?, budget = ?, channel = ?, start_date = ?, end_date = ?, status = ?
            WHERE id = ? AND user_id = ?
        ''', (name, budget, channel, start_date, end_date, status, campaign_id, session['user_id']))
        conn.commit()
        conn.close()
        
        flash('Campaign updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    conn.close()
    return render_template('edit_campaign.html', campaign=campaign)


@app.route('/campaign/<int:campaign_id>/delete', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    """Delete a campaign"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Delete campaign (ensure it belongs to logged-in user)
    cursor.execute('''
        DELETE FROM campaigns WHERE id = ? AND user_id = ?
    ''', (campaign_id, session['user_id']))
    
    conn.commit()
    conn.close()
    
    flash('Campaign deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/campaign/<int:campaign_id>/metrics', methods=['GET', 'POST'])
@login_required
def add_metrics(campaign_id):
    """Add performance metrics to a campaign"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify campaign belongs to user
    campaign = cursor.execute('''
        SELECT * FROM campaigns WHERE id = ? AND user_id = ?
    ''', (campaign_id, session['user_id'])).fetchone()
    
    if not campaign:
        conn.close()
        flash('Campaign not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        date = request.form.get('date')
        impressions = request.form.get('impressions', 0)
        clicks = request.form.get('clicks', 0)
        conversions = request.form.get('conversions', 0)
        spend = request.form.get('spend', 0)
        
        try:
            impressions = int(impressions)
            clicks = int(clicks)
            conversions = int(conversions)
            spend = float(spend)
        except ValueError:
            flash('Invalid metric values.', 'danger')
            return redirect(url_for('add_metrics', campaign_id=campaign_id))
        
        cursor.execute('''
            INSERT INTO metrics (campaign_id, date, impressions, clicks, conversions, spend)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (campaign_id, date, impressions, clicks, conversions, spend))
        conn.commit()
        conn.close()
        
        flash('Metrics added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    conn.close()
    return render_template('add_metrics.html', campaign=campaign)


# Initialize database before first request
@app.before_request
def before_first_request():
    """Initialize database before first request"""
    if not hasattr(app, 'db_initialized'):
        init_db()
        app.db_initialized = True


if __name__ == '__main__':
    init_db()  # Initialize database on startup
    app.run(debug=True)