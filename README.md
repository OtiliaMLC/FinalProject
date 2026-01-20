# Bootstrap Budget Tracker 💰

**A marketing campaign manager for small businesses and startups on tight budgets**

Created by: Otilia  
Course: CPNITS - Final Project  
Date: January 2026

---

## 📋 Project Description

Bootstrap Budget Tracker helps small business owners and startup founders track their marketing campaigns, monitor spending, and calculate ROI without expensive marketing software. Users can create campaigns, input performance data, and get instant insights on what's working.

## ✨ Features

### Must Have (Core Features)
- ✅ User registration and login system
- ✅ Create, read, update, delete campaigns (full CRUD)
- ✅ Track campaign details: name, budget, channel, dates
- ✅ Record performance metrics: impressions, clicks, conversions, spending
- ✅ Automatic ROI calculation
- ✅ Dashboard with campaign overview
- ✅ SQLite database storage

### Should Have
- ✅ Budget alerts (warning at 80% usage)
- ⏳ Filter campaigns by channel or date
- ⏳ Visual performance charts
- ⏳ Export data as CSV

### Could Have
- ⏳ Side-by-side campaign comparison
- ⏳ Channel recommendations
- ⏳ Dark mode

## 🛠️ Technology Stack

- **Backend:** Python 3.10+ with Flask
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript
- **Testing:** pytest
- **Deployment:** Render

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (venv)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd c:\Users\stefa\Desktop\Otilia
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to: `http://127.0.0.1:5000`

## 🧪 Running Tests

Run the pytest test suite:

```bash
pytest test_app.py -v
```

For detailed output:
```bash
pytest test_app.py -v -s
```

## 📊 Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - User email
- `password_hash` - Hashed password
- `created_at` - Registration timestamp

### Campaigns Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `name` - Campaign name
- `budget` - Total budget amount
- `channel` - Marketing channel (Instagram, Facebook, etc.)
- `start_date` - Campaign start date
- `end_date` - Campaign end date
- `status` - Campaign status (active, paused, completed)
- `created_at` - Creation timestamp

### Metrics Table
- `id` - Primary key
- `campaign_id` - Foreign key to campaigns
- `date` - Metric date
- `impressions` - Number of ad impressions
- `clicks` - Number of clicks
- `conversions` - Number of conversions
- `spend` - Amount spent

## 🎯 How to Use

1. **Register an account** - Create your user account
2. **Login** - Access your dashboard
3. **Create a campaign** - Set up a new marketing campaign with budget and details
4. **Add metrics** - Track daily performance (impressions, clicks, conversions, spend)
5. **Monitor ROI** - View automatic ROI calculations
6. **Get alerts** - Receive warnings when budget usage exceeds 80%
7. **Manage campaigns** - Edit, pause, or delete campaigns as needed

## 📈 ROI Calculation

The app calculates ROI using this formula:

```
ROI = ((Total Revenue - Total Spend) / Total Spend) × 100
```

Where:
- **Total Revenue** = Number of Conversions × Average Conversion Value ($50)
- **Total Spend** = Sum of all spending on the campaign

## 📝 Testing Coverage

The pytest suite covers:
- ✅ ROI calculation functions
- ✅ Budget alert logic
- ✅ Date and budget validation
- ✅ Database operations (CRUD)
- ✅ User authentication (register, login, logout)
- ✅ Flask route responses
- ✅ Campaign creation and management

## 🔒 Security Notes

- Passwords are hashed using Werkzeug's security functions
- Session-based authentication
- SQL injection protection via parameterized queries
- CSRF protection built into Flask

## 📚 Learning Outcomes

This project demonstrates:
- Full-stack web development with Flask
- Database design and SQLite implementation
- User authentication and session management
- CRUD operations
- Responsive CSS design (Flexbox/Grid)
- Test-driven development with pytest
- Deployment to production environment

## 🚀 Deployment to Render

https://finalproject-2vqr.onrender.com/


## 🤝 Credits

- Created by: Otilia
- Course: Creative Programming for Non-IT Students (CPNITS)
- Instructor: Victor
- Institution: NhlStenden

## 📄 License

Educational project for CPNITS Final Assignment - January 2026

