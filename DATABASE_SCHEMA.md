# Database Schema - Bootstrap Budget Tracker
## Entity-Relationship Diagram (ERD)

```
┌─────────────────────────────────────┐
│            USERS                    │
├─────────────────────────────────────┤
│ PK  id (INTEGER)                    │
│     username (TEXT, UNIQUE)         │
│     email (TEXT, UNIQUE)            │
│     password_hash (TEXT)            │
│     created_at (TIMESTAMP)          │
└─────────────────────────────────────┘
                  │
                  │ 1
                  │
                  │ has many
                  │
                  │ N
                  ▼
┌─────────────────────────────────────┐
│           CAMPAIGNS                 │
├─────────────────────────────────────┤
│ PK  id (INTEGER)                    │
│ FK  user_id (INTEGER) ───────────┐  │
│     name (TEXT)                   │  │
│     budget (REAL)                 │  │
│     channel (TEXT)                │  │
│     start_date (DATE)             │  │
│     end_date (DATE)               │  │
│     status (TEXT)                 │  │
│     created_at (TIMESTAMP)        │  │
└───────────────────────────────────┼──┘
                  │                 │
                  │ 1               │
                  │                 │
                  │ has many        │
                  │                 │
                  │ N               │
                  ▼                 │
┌─────────────────────────────────────┤
│            METRICS                  │
├─────────────────────────────────────┤
│ PK  id (INTEGER)                    │
│ FK  campaign_id (INTEGER) ──────────┘
│     date (DATE)                     │
│     impressions (INTEGER)           │
│     clicks (INTEGER)                │
│     conversions (INTEGER)           │
│     spend (REAL)                    │
└─────────────────────────────────────┘


RELATIONSHIPS:
═════════════

1. USERS → CAMPAIGNS (One-to-Many)
   - One user can have MANY campaigns
   - Each campaign belongs to ONE user
   - Relationship: user_id (FK in campaigns) references id (PK in users)

2. CAMPAIGNS → METRICS (One-to-Many)
   - One campaign can have MANY metrics entries
   - Each metric entry belongs to ONE campaign
   - Relationship: campaign_id (FK in metrics) references id (PK in campaigns)
   - CASCADE DELETE: When campaign is deleted, all its metrics are deleted too


FIELD TYPES & CONSTRAINTS:
═══════════════════════════

USERS Table:
  - id: INTEGER, Primary Key, Auto-increment
  - username: TEXT, NOT NULL, UNIQUE
  - email: TEXT, NOT NULL, UNIQUE
  - password_hash: TEXT, NOT NULL (bcrypt hashed)
  - created_at: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP

CAMPAIGNS Table:
  - id: INTEGER, Primary Key, Auto-increment
  - user_id: INTEGER, NOT NULL, Foreign Key → users.id
  - name: TEXT, NOT NULL
  - budget: REAL (float), NOT NULL, > 0
  - channel: TEXT, NOT NULL (Instagram, Facebook, etc.)
  - start_date: DATE, NOT NULL
  - end_date: DATE, NOT NULL (must be >= start_date)
  - status: TEXT, DEFAULT 'active' (active, paused, completed)
  - created_at: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP

METRICS Table:
  - id: INTEGER, Primary Key, Auto-increment
  - campaign_id: INTEGER, NOT NULL, Foreign Key → campaigns.id (ON DELETE CASCADE)
  - date: DATE, NOT NULL
  - impressions: INTEGER, DEFAULT 0
  - clicks: INTEGER, DEFAULT 0
  - conversions: INTEGER, DEFAULT 0
  - spend: REAL (float), DEFAULT 0.0


BUSINESS LOGIC:
═══════════════

ROI Calculation:
  ROI = ((conversions × $50 - total_spend) / total_spend) × 100

Budget Alert:
  Triggered when: (total_spend / budget) × 100 >= 80%

Click-Through Rate (CTR):
  CTR = (clicks / impressions) × 100

Conversion Rate:
  Conversion Rate = (conversions / clicks) × 100
