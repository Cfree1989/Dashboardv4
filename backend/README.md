# Flask Backend - 3D Print Management System

## Database Setup and Migrations

### Quick Start with Docker

1. **Start the database service:**
   ```bash
   docker-compose up -d db
   ```

2. **Run database setup:**
   ```bash
   docker-compose run --rm backend python setup_database.py
   ```

3. **Start all services:**
   ```bash
   docker-compose up -d
   ```

### Database Schema

The system uses PostgreSQL with the following tables:

- **`staff`** - Lab personnel management with activation/deactivation
- **`job`** - Complete 3D print request lifecycle tracking
- **`event`** - Immutable audit trail with staff attribution
- **`payment`** - Tiger-Cash transaction records

### Migration Commands

The Flask application includes CLI commands for database management:

```bash
# Initialize database (create tables)
flask init-db

# Reset database (drop and recreate)
flask reset-db

# Create sample staff data
flask seed-db

# Alternative: Use the comprehensive setup script
python setup_database.py
```

### Model Features

#### Job Model
- **Workflow States**: UPLOADED → PENDING → READYTOPRINT → PRINTING → COMPLETED → PAIDPICKEDUP
- **File Tracking**: Original file preservation + authoritative file management
- **Student Confirmation**: Secure token-based email confirmation system
- **Job Locking**: Concurrent access control for staff operations
- **Cost Calculation**: Automatic pricing based on material and weight

#### Event Model
- **Immutable Audit Trail**: All system actions logged permanently
- **Staff Attribution**: Every action tied to specific staff member
- **Workstation Tracking**: Physical computer identification
- **20+ Event Types**: Comprehensive coverage of all system operations

#### Staff Model
- **Turnover Management**: Deactivation preserves historical attribution
- **Active/Inactive States**: Clean staff list management
- **Action Attribution**: Links to event logs for accountability

#### Payment Model
- **Tiger-Cash Integration**: Transaction number tracking
- **Weight Accuracy**: Actual vs estimated weight comparison
- **Cost Analysis**: Price difference calculations and reporting

### Configuration

Environment variables are managed through the config system:

- **Development**: Uses local PostgreSQL or SQLite fallback
- **Testing**: In-memory SQLite for fast test execution
- **Production**: PostgreSQL with strict security settings

### File Structure

```
backend/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # API endpoints (Blueprints)
│   ├── services/        # Business logic
│   └── utils/           # Helper utilities
├── migrations/          # Flask-Migrate files
├── scripts/             # Database utilities
└── setup_database.py   # Comprehensive setup script
```

### Health Check

The API includes a health check endpoint for monitoring:

```
GET /api/v1/health
```

Returns database and worker status for system monitoring.

### Development Notes

- All models use the app factory pattern to avoid circular imports
- Database instance is centralized in `app.database` module
- Flask-Migrate is configured for schema evolution
- Comprehensive CLI commands for common operations
- Sample data seeding for development testing

### Testing

Run the database setup locally:

```bash
# With Docker (recommended)
docker-compose run --rm backend python setup_database.py

# Local testing (requires dependencies)
pip install -r requirements.txt
python setup_database.py
```

The setup script will:
1. Create all database tables
2. Verify schema completeness  
3. Add sample staff members
4. Test model functionality
5. Report system status