# Style Guide - 3D Print Management System

## Python/Flask Backend Standards

### Code Organization
```python
# Use Blueprint organization for routes
from flask import Blueprint
bp = Blueprint('jobs', __name__, url_prefix='/api/v1/jobs')

# Group related functionality in services
from app.services.file_service import move_job_file
from app.services.email_service import send_approval_email
```

### Function Naming
```python
# Use descriptive, action-oriented names
def approve_job_with_params(job_id, weight_g, time_hours, staff_name):
    """Approve a job and transition to PENDING status."""
    pass

# Avoid generic names
def process_job(job_id):  # ❌ Too vague
    pass
```

### Error Handling
```python
# Always return structured error responses
try:
    result = perform_file_operation()
except FileNotFoundError:
    return {"error": "file_not_found", "message": "Job file is missing"}, 404
except PermissionError:
    return {"error": "access_denied", "message": "Cannot access file"}, 500

# Log errors with context
logger.error(f"Failed to move file for job {job_id}: {str(e)}")
```

### Database Operations
```python
# Use transactions for multi-step operations
with db.session.begin():
    job.status = 'PENDING'
    job.updated_at = datetime.utcnow()
    
    # Create event log entry
    event = Event(
        job_id=job.id,
        event_type='StaffApproved',
        triggered_by=staff_name,
        workstation_id=current_workstation,
        details={'weight_g': weight_g, 'time_hours': time_hours}
    )
    db.session.add(event)
```

### File Operations
```python
# Always use copy-update-delete pattern
def move_job_file_safely(job, new_status):
    """Move job file using resilient copy-update-delete pattern."""
    old_path = job.file_path
    new_dir = get_status_directory(new_status)
    new_path = os.path.join(new_dir, os.path.basename(old_path))
    
    # 1. Copy file to new location
    shutil.copy2(old_path, new_path)
    
    # 2. Update database within transaction
    with db.session.begin():
        job.file_path = new_path
        job.status = new_status
    
    # 3. Delete original file
    os.remove(old_path)
    
    logger.info(f"Moved job {job.id} file from {old_path} to {new_path}")
```

## TypeScript/React Frontend Standards

### Component Structure
```tsx
// Use descriptive interface names
interface ApprovalModalProps {
  job: Job;
  onApprove: (params: ApprovalParams) => void;
  onCancel: () => void;
}

export function ApprovalModal({ job, onApprove, onCancel }: ApprovalModalProps) {
  // Component implementation
}
```

### State Management
```tsx
// Use meaningful state variable names
const [isSubmitting, setIsSubmitting] = useState(false);
const [selectedStaffMember, setSelectedStaffMember] = useState<string>('');
const [validationErrors, setValidationErrors] = useState<ValidationError[]>([]);

// Clear loading states appropriately
const handleSubmit = async () => {
  setIsSubmitting(true);
  try {
    await approveJob(jobId, approvalParams);
    onSuccess();
  } catch (error) {
    setValidationErrors(parseApiErrors(error));
  } finally {
    setIsSubmitting(false);
  }
};
```

### API Client Patterns
```tsx
// Centralize API calls in lib/api.ts
export async function approveJob(
  jobId: string, 
  params: ApprovalParams
): Promise<Job> {
  const response = await fetch(`/api/v1/jobs/${jobId}/approve`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getWorkstationToken()}`
    },
    body: JSON.stringify(params)
  });
  
  if (!response.ok) {
    throw new ApiError(response.status, await response.json());
  }
  
  return response.json();
}
```

### Form Validation
```tsx
// Use Zod for consistent validation
import { z } from 'zod';

const approvalSchema = z.object({
  weight_g: z.number().min(0.1).max(1000),
  time_hours: z.number().min(0.1).max(100),
  staff_name: z.string().min(1, "Staff member selection required"),
  authoritative_file: z.string().min(1, "File selection required")
});

// Validate before submission
const handleApprove = () => {
  const validation = approvalSchema.safeParse(formData);
  if (!validation.success) {
    setErrors(validation.error.flatten().fieldErrors);
    return;
  }
  
  onApprove(validation.data);
};
```

## Database Schema Conventions

### Table Naming
- Use singular nouns: `job`, `event`, `payment` (not `jobs`, `events`)
- Use snake_case for column names: `student_name`, `created_at`
- Use descriptive foreign key names: `job_id`, `staff_name`

### Column Types
```sql
-- Use appropriate data types
id VARCHAR(36) PRIMARY KEY,          -- UUID as string
created_at TIMESTAMP NOT NULL DEFAULT NOW(),
weight_g DECIMAL(6,2),               -- 6 digits, 2 decimal places
cost_usd DECIMAL(6,2),               -- Monetary values
status VARCHAR(20) NOT NULL,         -- Enum-like strings
details JSONB,                       -- PostgreSQL JSON with indexing
```

### Indexes
```sql
-- Index frequently queried columns
CREATE INDEX idx_job_status ON job(status);
CREATE INDEX idx_job_created_at ON job(created_at);
CREATE INDEX idx_event_job_id ON event(job_id);
CREATE INDEX idx_event_timestamp ON event(timestamp);
```

## API Design Standards

### Endpoint Naming
```
GET    /api/v1/jobs              # List jobs
GET    /api/v1/jobs/{id}         # Get specific job
POST   /api/v1/jobs/{id}/approve # Action on specific job
PATCH  /api/v1/jobs/{id}/notes   # Update specific field
DELETE /api/v1/jobs/{id}         # Delete job
```

### Response Format
```json
{
  "success": true,
  "data": {
    "job": { /* job object */ }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}

// Error responses
{
  "error": "validation_failed",
  "message": "Required fields are missing",
  "details": {
    "weight_g": ["Weight is required"],
    "staff_name": ["Staff member must be selected"]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Authentication Headers
```
Authorization: Bearer <workstation_jwt>
Content-Type: application/json
X-Workstation-ID: front-desk-computer
```

## File and Directory Conventions

### Project Structure
```
backend/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # API endpoints (Blueprints)
│   ├── services/        # Business logic
│   └── utils/           # Helper utilities
├── tests/               # Test files mirror app structure
└── migrations/          # Database schema changes

frontend/
├── app/                 # Next.js App Router pages
├── components/          # Reusable UI components
│   ├── dashboard/       # Dashboard-specific components
│   ├── forms/           # Form components
│   └── ui/              # shadcn/ui components
├── lib/                 # Utilities and API client
└── types/               # TypeScript type definitions
```

### File Naming
- Python files: `snake_case.py`
- React components: `PascalCase.tsx`
- Types/interfaces: `PascalCase.ts`
- Utility functions: `camelCase.ts`
- API routes: `kebab-case.py` (for blueprints)

## Environment Variables

### Naming Convention
```bash
# Backend (.env)
FLASK_ENV=development
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-secret-key
MAIL_SERVER=smtp.office365.com
STORAGE_BASE_PATH=/mnt/3dprint_storage

# Frontend (.env.local)
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
NEXT_PUBLIC_ENVIRONMENT=development
```

### Security Rules
- Never commit actual `.env` files
- Always provide `.env.example` templates
- Use descriptive variable names
- Group related variables together
- Document required vs optional variables

## Testing Standards

### Test Organization
```python
# Backend tests mirror app structure
tests/
├── test_models.py       # Database model tests
├── test_routes_jobs.py  # Job endpoint tests  
├── test_services.py     # Business logic tests
└── test_file_operations.py  # File handling tests
```

### Test Naming
```python
def test_approve_job_creates_event_log():
    """Test that approving a job creates proper event log entry."""
    pass

def test_approve_job_moves_file_to_pending():
    """Test that approval moves file to Pending directory.""" 
    pass

def test_approve_job_requires_staff_attribution():
    """Test that approval fails without staff_name parameter."""
    pass
```

## Documentation Standards

### Code Comments
```python
def calculate_print_cost(weight_g: float, material: str) -> Decimal:
    """
    Calculate print cost based on weight and material type.
    
    Args:
        weight_g: Weight in grams (positive number)
        material: Either 'filament' or 'resin'
        
    Returns:
        Cost in USD, minimum $3.00
        
    Raises:
        ValueError: If weight is negative or material is invalid
    """
    pass
```

### README Structure
1. Project overview
2. Quick start instructions  
3. Development setup
4. API documentation links
5. Deployment instructions
6. Contributing guidelines

### Commit Messages
```
feat: add job approval workflow with staff attribution
fix: resolve file path validation in Windows environments  
docs: update API documentation for payment endpoints
refactor: simplify job status transition logic
test: add integration tests for email confirmation flow
```