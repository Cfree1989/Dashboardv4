# Cursor AI Assistant Tips for 3D Print Management System

## Project Context Commands

When starting a new session, use these to give Cursor context:

```
@project-info.md @masterplan.md - Review project goals and architecture
@docs/requirements/user-stories.md - Understand user workflows  
@docs/context/glossary.md - Learn domain terminology
```

## Common Development Tasks

### Backend Development
```bash
# Start Flask development server
cd backend && python run.py

# Run database migrations
docker-compose run --rm backend flask db upgrade

# Add new migration
docker-compose run --rm backend flask db migrate -m "description"

# Test API endpoints
curl -X GET http://localhost:5000/api/v1/health
```

### Frontend Development
```bash
# Start Next.js development server
cd frontend && npm run dev

# Build for production
cd frontend && npm run build

# Type checking
cd frontend && npm run type-check
```

### Docker Operations  
```bash
# Full system startup
docker-compose up -d

# Rebuild after code changes
docker-compose build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Red Flag Patterns to Avoid

### File Operations
- ❌ Never use simple `os.rename()` - files can disappear
- ✅ Always use copy-update-delete pattern for resilience
- ❌ Don't store relative paths in database
- ✅ Store absolute paths and validate they exist

### API Design
- ❌ Never skip staff attribution for state changes
- ✅ All modals must require staff name selection
- ❌ Don't expose raw database errors to frontend
- ✅ Return structured error messages with recovery hints

### Frontend State
- ❌ Don't cache job data without refresh mechanism
- ✅ Re-fetch job state before showing modals
- ❌ Don't submit forms without loading states
- ✅ Show progress indicators for all async operations

## Troubleshooting Recipes

### File Access Issues
```python
# Always check file exists before operations
import os
if not os.path.exists(file_path):
    logger.error(f"File not found: {file_path}")
    return {"error": "File not accessible"}

# Log all file operations for debugging
logger.info(f"Moving file from {src} to {dest}")
```

### Database Connection Problems
```bash
# Check PostgreSQL is running
docker-compose ps db

# Reset database completely (DEV ONLY)
docker-compose down -v
docker-compose up -d db
docker-compose run --rm backend flask db upgrade
```

### Protocol Handler Issues
```bash
# Re-register protocol on Windows
cd SlicerOpener && register.bat

# Check protocol registration
reg query HKEY_CLASSES_ROOT\3dprint

# Test protocol handler directly
SlicerOpener.exe "3dprint://open?path=C:\path\to\file.stl"
```

### Email Delivery Problems
```python
# Test SMTP configuration
from app.services.email_service import send_test_email
send_test_email("test@example.com")

# Check RQ worker is processing
docker-compose logs -f worker
```

## Code Generation Prompts

### Creating New API Endpoints
```
Create a Flask Blueprint endpoint for [action] that:
- Requires workstation JWT authentication  
- Validates staff_name in request body
- Creates Event log entry with attribution
- Returns structured JSON response
- Handles file operations safely
```

### Creating React Components
```
Create a Next.js component for [feature] that:
- Uses TypeScript with proper types
- Implements shadcn/ui components
- Shows loading states during API calls
- Handles errors with user-friendly messages
- Follows the existing design patterns
```

## Testing Commands

```bash
# Run Python tests
cd backend && python -m pytest tests/

# Run frontend type checking
cd frontend && npm run type-check

# Test Docker build
docker-compose -f docker-compose.yml build

# Test file protocol handler
echo "Testing protocol handler..."
start 3dprint://open?path=Z:\storage\test.stl
```

## Performance Tips

- Use `codebase_search` for understanding workflows before coding
- Reference existing components in `/components` for patterns
- Check `types/job.ts` for TypeScript interfaces
- Always test file operations with actual network storage
- Verify email templates render correctly across clients