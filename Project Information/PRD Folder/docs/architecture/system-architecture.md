# System Architecture

This document outlines the architecture of the 3D Print System, including its components, deployment model, and integration patterns.

## 1. High-Level Architecture

The 3D Print System follows a clear separation between backend and frontend, designed for beginner-friendly development and deployment:

### 1.1 Key Components

- **Flask API Backend**: RESTful API handling all business logic and data operations
- **Next.js Frontend**: Modern web interface consuming the API endpoints
- **PostgreSQL Database**: Persistent storage for job and event data
- **Redis & RQ**: Message broker and worker for asynchronous tasks
- **File Storage**: Structured network-mounted storage for 3D model files
- **SlicerOpener**: Custom protocol handler for opening files in local applications

### 1.2 Architectural Principles

1. **API-First Design**: Complete separation between frontend and backend, connected only via RESTful API endpoints.
2. **Event-Driven Architecture**: All significant actions generate immutable event records for auditing and tracking.
3. **File Resilience**: Critical file metadata is duplicated in both database and filesystem for maximum resilience.
4. **Stateless Authentication**: Simple JWT-based authentication for workstations with per-action staff attribution.
5. **Beginner-Friendly Implementation**: Clear organization, minimized complexity, and progressive enhancement.

## 2. Deployment Topology

The system uses a centralized backend architecture to ensure stability and simplify management:

### 2.1 Backend Host (One Computer)

- A single staff PC or server acts as the backend host
- Runs the entire Docker Compose stack:
  - Flask API container
  - PostgreSQL database container
  - Redis message broker container
  - RQ worker container
  - Next.js frontend container
- This centralized approach prevents database conflicts and simplifies backup procedures

### 2.2 Client Workstations (Up to Two Computers)

- Additional staff computers that access the system via web browser
- Connect to the backend host via its network IP address
- Only require the SlicerOpener protocol handler to be installed locally
- Do not run any server code

### 2.3 Shared Network Storage

- Mounted at the same path on all computers (backend host and client workstations)
- Example paths: `Z:\storage\` on Windows or `/mnt/3dprint_files` on Linux
- Contains standardized directory structure for different job statuses
- Path consistency is critical for correct file operations

## 3. Component Architecture

### 3.1 Backend (Flask API) Components

```
backend/
├── app/
│   ├── __init__.py      # App factory
│   ├── config.py        # Configuration
│   ├── models/
│   │   ├── job.py       # Job model
│   │   └── event.py     # Event log model
│   ├── routes/
│   │   ├── auth.py      # Authentication endpoints
│   │   ├── jobs.py      # Job management endpoints
│   │   └── submit.py    # Student submission endpoints
│   ├── services/        # Business logic
│   │   ├── file_service.py
│   │   ├── email_service.py
│   │   └── auth_service.py
│   └── utils/           # Utilities
│       ├── decorators.py # Auth decorators
│       └── validators.py # Input validation
├── migrations/          # Database migrations
├── .env                 # Backend environment variables
├── requirements.txt     # Python dependencies
└── run.py               # Development server
```

#### Key Backend Modules

- **Models**: Core data structures for Job and Event records
- **Routes**: API endpoints organized by functional area using Flask Blueprints
- **Services**: Business logic implementation separated from route handlers
- **Utils**: Shared utility functions and decorators

### 3.2 Frontend (Next.js) Components

```
frontend/
├── app/                 # App Router pages
│   ├── dashboard/
│   │   └── page.tsx     # Staff dashboard
│   ├── submit/
│   │   └── page.tsx     # Student submission form
│   ├── login/
│   │   └── page.tsx     # Workstation login
│   ├── confirm/
│   │   └── [token]/
│   │       └── page.tsx # Student confirmation
│   ├── globals.css      # Global styles
│   ├── layout.tsx       # Root layout
│   └── page.tsx         # Home page
├── components/          # UI Components
│   ├── dashboard/       # Dashboard-specific components
│   ├── submission/      # Form components
│   └── ui/              # shadcn/ui components
├── lib/                 # Utility functions
│   ├── api.ts           # API client functions
│   └── utils.ts         # General utilities
├── types/               # TypeScript types
│   └── job.ts           # Job-related types
└── .env.local           # Frontend environment variables
```

#### Key Frontend Features

- **App Router**: Modern file-based routing with server and client components
- **TypeScript**: Full type safety throughout the application
- **Tailwind CSS**: Utility-first styling with custom animations and themes
- **shadcn/ui**: Complete UI component library based on Radix UI primitives
- **React Context**: Advanced state management for dashboard data and real-time updates

### 3.3 SlicerOpener Protocol Handler

The SlicerOpener component is a simple yet critical custom protocol handler that enables direct file opening:

```
SlicerOpener/
├── SlicerOpener.py      # Protocol handler script
├── config.ini           # Configuration file
├── register.bat         # Windows registry setup
└── SlicerOpener.exe     # Compiled executable (PyInstaller)
```

- **Protocol Registration**: Registers a custom `3dprint://` protocol in the system
- **Security Validation**: Validates that file paths are within the authorized storage area
- **Slicer Integration**: Opens the appropriate slicer application based on file type
- **Error Handling**: Provides clear GUI feedback for any failures

## 4. Data Flow Architecture

### 4.1 Student Submission Flow

1. Student submits form on Next.js frontend
2. Frontend validates input and sends data to API
3. API validates input again and creates job record
4. API saves file to network storage with standardized naming
5. API creates metadata.json alongside the file
6. API enqueues asynchronous thumbnail generation task
7. Frontend displays success message to student

### 4.2 Staff Approval Flow

1. Staff views job in dashboard
2. Staff opens file using SlicerOpener protocol handler
3. Local slicer application opens the file from network storage
4. Staff prepares the file and saves changes
5. Staff completes approval form on dashboard
6. API processes approval, moves files, and updates database
7. API enqueues asynchronous email notification task
8. Dashboard updates to reflect new status

### 4.3 Event Logging Flow

1. Staff action triggers API endpoint
2. API validates request and processes business logic
3. API creates immutable Event record with:
   - Job ID reference
   - Timestamp
   - Event type
   - Action details (JSON)
   - Staff attribution
   - Workstation ID
4. API returns success response
5. Dashboard shows updated data

## 5. Integration Architecture

### 5.1 API Communication

- Cross-Origin Resource Sharing (CORS) allows frontend to access API
- JWT token for authentication in Authorization header
- RESTful endpoints with consistent error handling
- HTTP Status codes for proper state communication

### 5.2 File System Integration

- Network-mounted storage accessible to all components
- Consistent path structure across all computers
- Metadata stored in database and alongside files for resilience
- File operations follow "copy, update, then delete" pattern for resilience

### 5.3 Email Integration

- Flask-Mail with Office 365 SMTP integration
- Asynchronous sending via RQ worker
- HTML templates for student notifications
- Rate limiting for resend operations

## 6. Concurrency Control

To maintain data integrity in a multi-user environment, the system implements several safeguards:

### 6.1 Job Locking Mechanism

- API-level job locking prevents simultaneous edits
- Lock acquisition required before state-changing actions
- Lock heartbeat extends duration for long operations
- Automatic lock expiration prevents stuck jobs
- Admin override available for manual resolution

### 6.2 Transactional File Operations

- File operations follow "copy, update, then delete" pattern
- Database transaction ensures atomic state changes
- System health audits can detect and resolve inconsistencies

## 7. Security Architecture

### 7.1 Authentication & Authorization

- Workstation-based shared passwords (no individual user accounts)
- Mandatory per-action staff attribution for accountability
- Time-limited JWT tokens for API access
- Staff list managed centrally with active/inactive status

### 7.2 API Security

- Input validation on both client and server
- Rate limiting for public endpoints
- File type and size validation
- Path traversal prevention

### 7.3 Email Security

- Secure, time-limited confirmation tokens
- Rate limiting for resend operations
- Proper SMTP configuration with Office 365

## 8. System Health Monitoring

- Public health check endpoint for monitoring services
- Background integrity audit process
- Logging of all critical operations
- Automated email alerts for system issues 