# 3D Print System Project Plan (Beginner-Friendly Flask API + Next.js Edition)

## 1. Project Overview
This project will build a Flask-based 3D print job management system **from scratch**, specifically designed for beginners. The system is tailored for an academic/makerspace setting with up to two staff members operating concurrently on separate computers. It uses individual staff accounts and is designed with safeguards to prevent data conflicts and race conditions inherent in a multi-user environment. The system will handle the workflow from student submission to completion, with file tracking, staff approval, and the ability to open the exact uploaded files directly in local applications.

> **Key Design Principle**: This project prioritizes **beginner-friendly implementation** with clear, step-by-step guidance and minimal complexity. We start with a basic working system and iterate to add features.

> **Note:** The system is designed for a multi-user environment and is deployed using Docker. The core services (API, database, background workers) run as containers on a single host machine. Staff can access the system from up to two lab computers via a web browser. Both computers must have access to the same shared network storage for file management, and the `SlicerOpener` protocol handler must be installed locally on each.

The project aims to replace potentially ad-hoc or manual 3D print request systems with a **centralized, API-driven, and workflow-oriented platform.** It uses a **Flask API-only backend** with a **Next.js frontend**, following a clear separation of concerns where the backend handles all business logic and the frontend consumes REST APIs. It prioritizes clarity, efficiency, accurate file tracking, and a **strong, non-fragile foundation**, especially addressing the complexities of file changes introduced by slicer software and ensuring resilience.

## 1.1 User Roles & Personas
The system will cater primarily to two user roles:
●	**Students**: Users submitting 3D models for printing. They need a simple interface for uploading files, providing details, and tracking job progress.
●	**Staff/Admins**: Users managing the print queue, printers, and the system itself. They require tools for reviewing submissions, taking notes about jobs, approving/rejecting jobs, managing files, operating slicer software, tracking job status, and overseeing the system's health.

## 2. Core Features & Requirements

### 2.1 Core Features (Beginner-Friendly Implementation)

**Essential System Features**:
1.  **Student submission process**: Allow students to upload 3D model files (.stl, .obj, .3mf) with metadata (name, email, print_method, color, discipline, course_number) via a **Next.js form**.
2.  **Staff approval workflow**: Enable staff to review, slice files, and approve/reject jobs via a **Next.js dashboard**.
3.  **File lifecycle management**: Track original files through status-based directory structure with `metadata.json` for resilience.
4.  **Job status tracking**: Clear progression through UPLOADED → PENDING → READYTOPRINT → PRINTING → COMPLETED → PAIDPICKEDUP → ARCHIVED, and REJECTED → ARCHIVED.
5.  **Clerk authentication**: Professional authentication system for individual staff accounts with secure session management.
6.  **Email notifications**: **Asynchronously** send automated updates to students for approvals, rejections, and completions.
7.  **Direct file opening**: Custom `3dprint://` protocol handler to open files in local slicer software.

**Advanced Operational Features**:
8.  **Enhanced operational dashboard**: Real-time auto-updating **Next.js interface** with comprehensive staff alerting:
    *   **Auto-updating data**: Dashboard refreshes automatically every 45 seconds without manual intervention
    *   **Sound notifications**: Configurable audio alerts when new jobs are uploaded with browser Audio API and fallback handling
    *   **Visual alert indicators**: Persistent "NEW" badges with pulsing animations for unreviewed jobs until staff acknowledgment
    *   **Job age tracking**: Human-readable time elapsed display ("2d 4h ago") with color-coded prioritization (green < 24h, yellow < 48h, orange < 72h, red > 72h)
    *   **Staff acknowledgment system**: "Mark as Reviewed" functionality to clear visual alerts
    *   **Debug panel**: Development interface showing current state, sound settings, and system health
    *   **Last updated indicator**: Timestamp showing when dashboard data was last refreshed
9.  **Multi-computer support**: System can run on up to two staff computers, as long as both use the same shared storage and database.
10. **Event Logging**: **Immutable event log** tracking all changes with full audit trail tied to individual staff accounts.
11. **Thumbnails**: **Asynchronously** generate previews from uploaded files. If thumbnail generation fails, no thumbnail will be displayed, or a generic placeholder may be shown.

### 2.2 Technical Requirements (Beginner-Focused)

#### 2.2.1 Backend (Flask API-Only)
-   **Framework**: Flask (Python) with **API-only endpoints** - no HTML templates or server-side rendering
-   **Database**: PostgreSQL via SQLAlchemy ORM
-   **Task Queue**: RQ for background jobs (emails, thumbnail generation, and a recurring job to check for expired confirmation tokens).
-   **Email**: Flask-Mail with Office 365 SMTP
-   **Sibling File Detection**: A configurable list of slicer file extensions (e.g.,`.3mf`, `.form`, `.idea`) will be used to automatically detect when a staff member has saved a new authoritative file.
-   **File Storage**: Network-mounted folders with standardized structure:
    ```
    storage/
    ├─ Uploaded/         # New submissions
    ├─ Pending/          # Awaiting staff review
    ├─ ReadyToPrint/     # Approved, ready for printing
    ├─ Printing/         # Currently being printed
    ├─ Completed/        # Finished prints
    ├─ PaidPickedUp/      # Final state
    └─ Archived/         # Archived jobs
    ```

#### 2.2.2 Frontend (Next.js App Router)
-   **Framework**: Next.js 14+ with App Router and TypeScript
-   **Styling**: Tailwind CSS with custom themes and animations
-   **UI Components**: shadcn/ui component library (Radix UI primitives)
-   **Frontend Architecture**:
    -   **Next.js App Router**: Modern file-based routing with server and client components
    -   **TypeScript**: Full type safety throughout the application
    -   **Tailwind CSS**: Utility-first styling with custom animations and themes
    -   **shadcn/ui**: Complete UI component library based on Radix UI primitives
    -   **React Context**: Advanced state management for dashboard data and real-time updates
    -   **Sound System**: Browser Audio API with fallback handling for notifications
-   **Advanced Dashboard Features**:
    -   **Real-time Updates**: Auto-refresh every 45 seconds with visual and audio notifications
    -   **Sound Notifications**: Configurable audio alerts for new job uploads with browser compatibility
    -   **Visual Alert System**: "NEW" badges and pulsing animations for unreviewed jobs
    -   **Job Age Tracking**: Color-coded time elapsed display with human-readable formatting
    -   **Interactive Modals**: Approval/rejection workflows with form validation
    -   **Notes System**: Inline editing with auto-save and keyboard shortcuts
    -   **Debug Panel**: Development troubleshooting with state visibility
-   **Routing Structure**:
    ```
    app/
    ├─ dashboard/page.tsx     # Staff dashboard
    ├─ submit/page.tsx        # Student submission form
    ├─ login/page.tsx         # Staff login (Clerk)
    └─ confirm/[token]/page.tsx # Student confirmation
    ```

#### 2.2.3 Authentication (Clerk Integration)
-   **Clerk Authentication**: Professional authentication service for individual staff accounts
-   **Features**: Multi-factor authentication, session management, user management
-   **Staff Accounts**: Individual accounts for each staff member with proper audit trails
-   **Integration**: Seamless Next.js integration with Clerk SDK
-   **Token Management**: Clerk handles JWT tokens and session management automatically
-   **Backend Validation**: Flask backend validates Clerk-issued JWTs in Authorization headers
-   **User Information**: Staff actions logged with individual user identification for accountability

#### 2.2.4 Key Constraints & Principles
- **No Next.js API Routes**: All server logic handled by Flask backend
- **Beginner-Friendly**: Clear explanations and step-by-step setup
- **API-First Design**: Frontend consumes RESTful Flask API endpoints
- **CORS Configuration**: Enabled for Next.js development server integration

-   **API Communication**:
    -   Cross-Origin Resource Sharing (CORS) will be enabled on the Flask API to allow requests from the Next.js frontend.
    -   The API will be stateless and RESTful.
    -   Native **fetch API** for HTTP requests with error handling and retry logic.
-   **Task Queue**: RQ for **asynchronous processing** (emails, thumbnails).
-   **API Security & Rate Limiting**:
    -   **Flask-Limiter** integration for abuse protection:
        -   `/api/submit`: 3 submissions per IP per hour
        -   `/api/auth/login`: 10 attempts per IP per hour (brute-force protection)
        -   Return `429 Too Many Requests` for exceeded limits
    -   **File Upload Limits**: 50MB max file size, monitor total storage usage
-   **File handling**: Shared network storage (mounted at OS level) with standardized naming, status-based directory structure, and embedded `metadata.json`.
-   **Direct file opening**: Custom protocol handler to open local files in slicer software.
-   **Email**: Flask-Mail with Office 365 SMTP integration.
-   **Database**: **PostgreSQL** with Flask-Migrate for schema management.
-   **Time Display**: All timestamps from the API will be in **UTC**. The Next.js frontend will be responsible for converting and displaying them in the user's local timezone using `date-fns` library.
-   **Pricing Model**: Weight-only pricing ($0.10/gram filament, $0.20/gram resin) with $3.00 minimum charge.
-   **Time Input**: Hour-based time inputs with conservative rounding (always round UP to nearest 0.5 hours).
-   **Critical Dependencies**:
    -   **Backend**: `Flask`, `Flask-SQLAlchemy`, `Flask-Migrate`, `Flask-CORS`, `Flask-Limiter`, `psycopg2-binary`, `python-dotenv`, `PyJWT`, `rq`.
    -   **Frontend**: `next`, `react`, `react-dom`, `typescript`, `tailwindcss`, `@radix-ui/*`, `lucide-react`, `date-fns`, `class-variance-authority`, `clsx`, `tailwind-merge`.

### 2.3 Beginner-Friendly Architecture Principles
This project will adhere to simplicity and clarity while building a robust foundation:

#### 2.3.1 Core Architectural Decisions
1.  **Authentication**: **Clerk-based authentication** for professional individual staff accounts with built-in session management and security.
2.  **API Design**: **Flask API-only backend** with clear RESTful endpoints, no HTML templates or server-side rendering.
3.  **Frontend Separation**: **Next.js frontend** consumes API endpoints, complete separation of concerns.
4.  **Models**: Essential `Job` model, plus an **`Event` model** for comprehensive logging and audit trails.
5.  **File Management**: Straightforward folder structure, accessible via shared network, with `metadata.json` alongside files for resilience.

#### 2.3.2 Implementation Strategy
1.  **Incremental Development**: Start with minimal viable product (MVP), then build upon the foundation with additional features.
2.  **Routes**: API-only routes organized with **Flask Blueprints**, all actions triggering **event logs**.
3.  **Error Handling**: Comprehensive error handling with clear user feedback and logging.
4.  **Testing Strategy**: Focus on API endpoints, business logic, file handling, and workflow events.
5.  **Documentation**: Step-by-step guides for setup, deployment, and maintenance.

#### 2.3.3 Technology Stack Simplification
1.  **Docker-Based Environment**: The entire application stack is defined in a `docker-compose.yml` file, ensuring a consistent, reproducible environment for both development and production. This simplifies setup and eliminates cross-platform compatibility issues.
2.  **No Complex Auth**: Clerk handles all authentication complexity, provides professional UI.
3.  **No Microservices**: Single Flask application with clear module organization.
4.  **Progressive Enhancement**: Build solid foundation first, then add advanced features like custom protocol handlers.
5.  **Progressive Enhancement**: Build solid foundation, then add advanced dashboard features.

### 2.4 User Experience Requirements

#### 2.4.1 Essential UX Features
**Student Submission Experience**:
-   **Dynamic Form Behavior**: Color selection must be disabled until print method is selected, with contextual help text
-   **Progressive Disclosure**: Print method descriptions should be clearly visible to guide material choice
-   **Input Validation**: Real-time client-side validation with visual feedback to prevent submission errors
-   **Educational Content**: Comprehensive introduction text with liability disclaimers and scaling guidance
-   **File Validation**: Immediate feedback on file selection with size and type checking
-   **Accessibility**: Visual error states with red borders, clear error messages, and error scrolling for form submission

**Basic Staff Dashboard Experience**:
-   **Clean Interface**: Simple, professional dashboard showing job cards with essential information
-   **Basic Actions**: Approve/reject modals with form validation and cost calculation
-   **Job Management**: Status updates with clear visual feedback
-   **Clerk Authentication**: Seamless login experience with professional authentication UI

#### 2.4.2 Advanced UX Features
**Enhanced Operational Dashboard UX**:
    *   **Real-time Updates**: Dashboard data refreshes automatically every 45 seconds without user intervention
    *   **Audio Feedback**: Sound notifications play when new jobs are uploaded, with user-controlled toggle
    *   **Visual Alert System**: Unreviewed jobs display prominent "NEW" badges with pulsing highlight borders until acknowledged
    *   **Temporal Awareness**: Job age display with human-readable format ("2d 4h ago") and color-coded prioritization
    *   **Staff Acknowledgment**: Clear "Mark as Reviewed" functionality to manage alert states
    *   **Last Updated Indicator**: Timestamp showing when dashboard data was last refreshed

#### 2.4.3 Universal Design Standards
**Mobile and Accessibility Considerations**: 
- Ensure the submission form and dashboard are fully functional and readable on mobile devices.
- Test UI components with screen readers for basic WCAG 2.1 compliance.
- Ensure keyboard-only navigation works for all modals and interactive elements.

**Professional UI Design Standards**:
- All UI components must follow modern web design best practices
- Use consistent spacing system (multiples of 4px or 8px)
- Implement proper visual hierarchy with appropriate typography scales
- Support system font preferences and user accessibility settings
- Maintain minimum touch target size (44px minimum)
- Use professional color palette with sufficient contrast ratios
- Follow responsive design principles for all screen sizes


#### 2.4.1 Required Submission Form Introduction Text

**The following text must appear at the top of the student submission form, unaltered:**

> Before submitting your model for 3D printing, please ensure you have thoroughly reviewed our Additive Manufacturing Moodle page, read all the guides, and checked the checklist. If necessary, revisit and fix your model before submission. Your model must be scaled and simplified appropriately, often requiring a second version specifically optimized for 3D printing. We will not print models that are broken, messy, or too large. Your model must follow the rules and constraints of the machine. We will not fix or scale your model as we do not know your specific needs or project requirements. We print exactly what you send us; if the scale is wrong or you are unsatisfied with the product, it is your responsibility. We will gladly print another model for you at an additional cost. We are only responsible for print failures due to issues under our control.

## 3. System Architecture & Implementation Structure

### 3.1 Project Structure

The project follows a clear separation between backend and frontend, designed for beginner-friendly development and deployment:

```
V0DASHBOARDV4/
├── frontend/                # Next.js Application
│   ├── app/                 # App Router pages
│   │   ├── dashboard/
│   │   │   └── page.tsx     # Staff dashboard
│   │   ├── submit/
│   │   │   ├── page.tsx     # Student submission form
│   │   │   └── success/
│   │   │       └── page.tsx # Submission success
│   │   ├── login/
│   │   │   └── page.tsx     # Staff login (Clerk)
│   │   ├── confirm/
│   │   │   └── [token]/
│   │   │       └── page.tsx # Student email confirmation
│   │   ├── globals.css      # Global styles
│   │   ├── layout.tsx       # Root layout
│   │   └── page.tsx         # Home page (redirect to dashboard)
│   ├── components/          # UI Components
│   │   ├── dashboard/       # Dashboard-specific components
│   │   │   ├── dashboard.tsx
│   │   │   ├── job-card.tsx
│   │   │   ├── job-list.tsx
│   │   │   ├── status-tabs.tsx
│   │   │   └── modals/
│   │   │       ├── approval-modal.tsx
│   │   │       └── rejection-modal.tsx
│   │   ├── submission/      # Form components
│   │   │   └── submission-form.tsx
│   │   └── ui/              # shadcn/ui components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── input.tsx
│   │       ├── select.tsx
│   │       └── ... (other UI components)
│   ├── lib/                 # Utility functions
│   │   ├── api.ts           # API client functions
│   │   └── utils.ts         # General utilities
│   ├── types/               # TypeScript types
│   │   └── job.ts           # Job-related types
│   ├── .env.local           # Frontend environment variables
│   ├── package.json
│   └── next.config.mjs
│
├── backend/                 # Flask API Application
│   ├── app/
│   │   ├── __init__.py      # App factory
│   │   ├── config.py        # Configuration
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── job.py       # Job model
│   │   │   └── event.py     # Event log model
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py      # Authentication endpoints (Clerk validation)
│   │   │   ├── jobs.py      # Job management endpoints
│   │   │   └── submit.py    # Student submission endpoints
│   │   ├── services/        # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── file_service.py
│   │   │   ├── email_service.py
│   │   │   └── auth_service.py  # Clerk token validation
│   │   └── utils/           # Utilities
│   │       ├── __init__.py
│   │       ├── decorators.py # Auth decorators
│   │       └── validators.py # Input validation
│   ├── migrations/          # Database migrations
│   ├── .env                 # Backend environment variables
│   ├── requirements.txt     # Python dependencies
│   └── run.py               # Development server
│
├── storage/                 # File storage (network-mounted)
│   ├── Uploaded/
│   ├── Pending/
│   ├── ReadyToPrint/
│   ├── Printing/
│   ├── Completed/
│   ├── PaidPickedUp/
│   └── Archived/
│
├── SlicerOpener/            # Protocol handler
│   ├── SlicerOpener.py      # Python script
│   ├── register.bat         # Windows registry setup
│   └── SlicerOpener.exe     # Compiled executable (PyInstaller)
│
├── docker-compose.yml       # Defines all services for development and production
├── .dockerignore            # Specifies files to ignore in Docker builds
└── Dockerfile.backend       # Dockerfile for the Flask API
└── Dockerfile.frontend      # Dockerfile for the Next.js frontend

### 3.2 Database Schema & Models

The system uses PostgreSQL with SQLAlchemy ORM for robust data management and comprehensive audit trails.

#### 3.2.1 Core Models

**Job Model** - Central entity representing each 3D print request:
```python
class Job(db.Model):
   id = db.Column(db.String, primary_key=True)   # uuid4 hex
   student_name = db.Column(db.String(100))
   student_email = db.Column(db.String(100))
   discipline = db.Column(db.String(50))
   class_number = db.Column(db.String(50))
   
   # File Management
   original_filename = db.Column(db.String(256))
   display_name = db.Column(db.String(256))      # Standardized name for dashboard
   file_path = db.Column(db.String(512))         # Path to authoritative file
   metadata_path = db.Column(db.String(512))     # Path to metadata.json
   
   # Job Configuration
   status = db.Column(db.String(50))             # UPLOADED, PENDING, etc.
   printer = db.Column(db.String(64))
   color = db.Column(db.String(32))
   material = db.Column(db.String(32))
   weight_g = db.Column(db.Float)
   time_hours = db.Column(db.Float)
   cost_usd = db.Column(db.Numeric(6, 2))
   
   # Student Confirmation
   acknowledged_minimum_charge = db.Column(db.Boolean, default=False)
   student_confirmed = db.Column(db.Boolean, default=False)
   student_confirmed_at = db.Column(db.DateTime, nullable=True)
   confirm_token = db.Column(db.String(128), nullable=True, unique=True)
   confirm_token_expires = db.Column(db.DateTime, nullable=True)
   is_confirmation_expired = db.Column(db.Boolean, default=False, nullable=False)
   confirmation_last_sent_at = db.Column(db.DateTime, nullable=True)
   
   # Staff Management
   reject_reasons = db.Column(db.JSON, nullable=True)
   staff_viewed_at = db.Column(db.DateTime, nullable=True)    # For visual alerts
   last_updated_by = db.Column(db.String(100), nullable=True) # Clerk user ID
   notes = db.Column(db.Text, nullable=True)                  # Staff notes
   
   # Timestamps
   created_at = db.Column(db.DateTime, default=datetime.utcnow)
   updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
   
   # Relationships
   events = db.relationship('Event', backref='job', lazy=True)
```

**Event Model** - Immutable audit trail for all system actions:
```python
class Event(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   job_id = db.Column(db.String, db.ForeignKey('job.id'), nullable=False)
   timestamp = db.Column(db.DateTime, default=datetime.utcnow)
   event_type = db.Column(db.String(50))         # 'JobCreated', 'StaffApproved', etc.
   details = db.Column(db.JSON, nullable=True)   # Contextual information
   triggered_by = db.Column(db.String(100))      # Clerk user ID or 'student'/'system'
   user_name = db.Column(db.String(100))         # Display name for audit trail
```

#### 3.2.2 Key Design Decisions

**Authentication Integration**: The `last_updated_by` and `triggered_by` fields store Clerk user IDs, enabling full accountability and audit trails tied to individual staff members.

**File Resilience**: Both `file_path` and `metadata_path` ensure data integrity even if database and file system become disconnected.

**Flexible Status System**: String-based status allows for easy expansion of workflow states without schema changes.

**Audit Trail**: Every action creates an immutable Event record with full context for debugging and accountability.

### 3.3 Authentication Architecture

#### 3.3.1 Staff Authentication (Clerk Integration)
**Professional Authentication Service**: The system uses Clerk for staff authentication, providing enterprise-grade security and user management capabilities.

**Key Features**:
- **Individual Staff Accounts**: Each staff member has their own account with proper identity management
- **Multi-Factor Authentication**: Optional MFA support for enhanced security
- **Session Management**: Automatic token refresh and secure session handling
- **User Management**: Easy addition/removal of staff members through Clerk dashboard

**Technical Implementation**:
- **Frontend**: Clerk React SDK provides seamless authentication components and hooks
- **Backend**: Flask validates Clerk-issued JWTs using Clerk's public keys
- **Token Flow**: Clerk handles all JWT generation, validation, and refresh automatically
- **User Context**: Clerk user ID and profile information available throughout the application

#### 3.3.2 Student Authentication
**Email-Based Confirmation**: Students don't need accounts but use secure token-based confirmation for job approval.

**Confirmation Flow**:
- Secure tokens generated using itsdangerous library
- Tokens embedded in email URLs pointing to frontend confirmation pages
- Time-limited expiration with resend capabilities
- No persistent student sessions required

#### 3.3.3 Security & Accountability
**Comprehensive Audit Trail**: Every action is logged with individual staff member identification:
- **Event Logging**: All job actions recorded with Clerk user ID and display name
- **File Operations**: Staff member tracked for all file movements and modifications
- **Admin Actions**: Override and manual actions fully attributed to specific users
- **Timeline Tracking**: Complete chronological history of all system interactions

**Security Benefits**:
- **No Shared Passwords**: Eliminates security risks of shared credentials
- **Individual Accountability**: Every action traceable to specific staff member
- **Professional Standards**: Enterprise-grade authentication suitable for institutional use
- **Compliance Ready**: Audit trails support institutional security requirements

### 3.4 Job Lifecycle & Workflow Management

The system manages 3D print jobs through a comprehensive, event-driven workflow that ensures accountability, file integrity, and clear communication with students.


#### 3.4.1 Core Workflow Principles

**File Resilience Strategy**: 
- **metadata.json** files accompany every job file, containing essential job details for data resilience
- **Original File Preservation**: Student uploads are preserved throughout the entire lifecycle for historical reference and re-slicing needs
- **Authoritative File Tracking**: System tracks both original uploads and staff-modified files (e.g., sliced versions)

**Standardized File Naming**: `FirstAndLastName_PrintMethod_Color_SimpleJobID.original_extension`

**Event-Driven Architecture**: Every action generates immutable event logs with Clerk user attribution for complete audit trails.

#### 3.4.2 Workflow Status Progression

**1. UPLOADED Status**
* **Trigger:** Student completes submission through Next.js form, backend processes `POST /api/submit`
* **File Operations:**
  * File validation (type, size, format) with comprehensive error handling
  * Standardized rename: `JaneDoe_Filament_Blue_123.stl`
  * Storage location: `storage/Uploaded/`
  * **metadata.json** creation with complete job context
  * Database updates: `file_path`, `original_filename`, `display_name`, `metadata_path`
  * Thumbnail generation (asynchronous, failure-tolerant)
* **System Actions:** 
  * Event logging with system attribution
  * Student success page display
  * Job immediately visible in staff dashboard

**Student Submission UI/UX (Corresponds to 'Uploaded' Status)**
    **Page Flow**:
        `React Route (/submit)` → `Upload Form Page` → `API POST to /api/submit` → `File Validation & Job Creation` → `React Route (/submit/success?job=<id>)` OR `Upload Form Page with Errors`
 **Upload Form (`/submit`)**:
  **Form Introduction**: Comprehensive warning text at the top of the form stating:
    "Before submitting your model for 3D printing, please ensure you have thoroughly reviewed our Additive Manufacturing Moodle page, read all the guides, and checked the checklist. If necessary, revisit and fix your model before submission. Your model must be scaled and simplified appropriately, often requiring a second version specifically optimized for 3D printing. We will not print models that are broken, messy, or too large. Your model must follow the rules and constraints of the machine. We will not fix or scale your model as we do not know your specific needs or project requirements. We print exactly what you send us; if the scale is wrong or you are unsatisfied with the product, it is your responsibility. We will gladly print another model for you at an additional cost. We are only responsible for print failures due to issues under our control."
  **Fields**:
    * Student Name (text input, required, 2-100 characters)
    * Student Email (email input, required, validated format, max 100 characters)
    * Discipline (dropdown options, required): Art, Architecture, Landscape Architecture, Interior Design, Engineering, Hobby/Personal, Other
    * Class Number (text input, required, format example: "ARCH 4000 or N/A", max 50 characters, allows "N/A")
    * Print Method (dropdown: "Filament", "Resin", required) with contextual descriptions:
      - Resin: Description: Super high resolution and detail. Slow. Best For: Small items. Cost: More expensive.
      - Filament: Description: Good resolution, suitable for simpler models. Fast. Best For: Medium items. Cost: Least expensive.
    * Color Preference (dynamic dropdown, disabled until Print Method selected, required):
      - Filament Colors (23 options): True Red, True Orange, Light Orange, True Yellow, Dark Yellow, Lime Green, Green, Forest Green, Blue, Electric Blue, Midnight Purple, Light Purple, Clear, True White, Gray, True Black, Brown, Copper, Bronze, True Silver, True Gold, Glow in the Dark, Color Changing
      - Resin Colors (4 options): Black, White, Gray, Clear
    * Printer Dimensions (informational section only, no user input): Displays complete scaling guidance with text: "Will your model fit on our printers? Please check the dimensions (W x D x H): Filament - Prusa MK4S: 9.84" × 8.3" × 8.6" (250 × 210 × 220 mm), Prusa XL: 14.17" × 14.17" × 14.17" (360 × 360 × 360 mm), Raise3D Pro 2 Plus: 12" × 12" × 23.8" (305 × 305 × 605 mm). Resin - Formlabs Form 3: 5.7 × 5.7 × 7.3 inches (145 x 145 x 175 mm). Ensure your model's dimensions are within the specified limits for the printer you plan to use. If your model is too large, consider scaling it down or splitting it into parts. For more guidance, refer to the design guides on our Moodle page or ask for assistance in person. If exporting as .STL or .OBJ you MUST scale it down in millimeters BEFORE exporting. If you do not the scale will not work correctly."
    * Printer Selection (dropdown, required): Students select which printer they think their model fits on. Options: Prusa MK4S, Prusa XL, Raise3D Pro 2 Plus, Formlabs Form 3 (printer names only, dimensions shown in information section above)
    * Minimum Charge Consent (Yes/No dropdown, required): "I understand there is a minimum $3.00 charge for all print jobs, and that the final cost may be higher based on material and time." Students must select "Yes" or "No"
    * File Upload (input type `file`, required, .stl/.obj/.3mf only, 50MB max size)
    * Submit Button
  **Client-Side Validation**:
    - Real-time file validation (type and size checking on selection)
    - Email format validation on blur
    - Color dropdown state management (disabled until method selected)
    - Visual error feedback with red borders and error messages
    - Form submission validation for all field types
    - Error scrolling to first error on submission attempt
    - Submit button loading state during submission
  * Server-Side Validation: All client-side checks re-validated by the Flask API.
- Success Page (/submit/success?job=<id>):
  * Displays a success message within the React application.
  * Shows the Job ID for reference.
  * Provides clear "next steps" messaging (e.g., "Your submission is now with staff for review. You will receive an email if it's rejected or approved, asking for your final confirmation before printing.").

**2. PENDING Status (Awaiting Student Confirmation)**
* **Trigger:** Staff member approves a job through the dashboard, triggering a `POST /api/jobs/<id>/approve` request.
* **Authoritative File Detection (Sibling File Scan):**
  * Upon receiving the approval request, the backend API automatically scans the job's directory (e.g., `storage/Uploaded/`) for a "sibling" file.
  * A sibling file is defined as having the **exact same base name** as the current authoritative file but with a different, recognized slicer file extension (from the configurable list mentioned in Section 2.2.1).
  * **If a sibling file is found:** The system designates it as the new authoritative file. It updates the `job.file_path` and `job.display_name` in the database and logs a `FileSuperseded` event. The original student upload is always preserved. If multiple potential files exist, the most recently modified one is chosen.
  * **If no sibling file is found:** The original file remains authoritative.
* **File Operations:**
  * The (now potentially updated) authoritative file and its `metadata.json` are moved from `storage/Uploaded/` → `storage/Pending/`.
  * The database is updated with the new `file_path` and `metadata_path`.
* **System Actions:**
  * Clerk user attribution for the approval action is logged.
  * Print parameters (weight, time, cost) submitted by the staff are validated.
  * A secure confirmation token is generated for the student.
  * An approval email, containing the job details and confirmation link, is queued for sending.

**Staff Approval UI/UX (Corresponds to 'Pending' Status)**
- Approval Confirmation Modal: Title, message, required input fields (weight, time, material), calculated cost, cancel/approve buttons.

#### 3. Rejected
* **Trigger:** Staff reviews an "Uploaded" job and clicks "Reject". The frontend sends a `POST` request to `/api/jobs/<id>/reject`.
* **File Operations:** The file typically remains in storage/Uploaded/ or may be moved to an storage/Archived_Rejected/. Original uploaded file is preserved.
* **Key Actions:** Staff selects reasons in the React UI, backend logs event. Asynchronous task (SendRejectionEmail) triggered.
* **Email Notification:** Rejection email sent via task queue including reasons.

**Staff Rejection UI/UX (Corresponds to 'Rejected' Status)**
- Rejection Confirmation Modal: Title, message, checkbox group for common reasons, textarea for custom reason, cancel/reject buttons.

#### 4. ReadyToPrint
* **Trigger:** Student clicks the confirmation link. The link opens the React frontend, which sends a `POST` request to `/api/confirm/<token>`.
* **File Operations:** The authoritative file and metadata.json are moved from storage/Pending/ to storage/ReadyToPrint/. job.file_path is updated.
* **Key Actions:** Backend validates token, logs event. job.student_confirmed set to True.
* **Email Notification:** None.

#### 5. Printing
* **Trigger:** Staff clicks "Mark Printing" in the React UI. The frontend sends a `POST` request to `/api/jobs/<id>/mark-printing`.
* **File Operations:** The authoritative file and metadata.json are moved from storage/ReadyToPrint/ to storage/Printing/. job.file_path is updated.
* **Key Actions:** Staff starts print, API logs event.
* **Email Notification:** None.

#### 6. Completed
* **Trigger:** Staff clicks "Mark Complete" in the React UI. The frontend sends a `POST` request to `/api/jobs/<id>/mark-complete`.
* **File Operations:** The authoritative file and metadata.json are moved from storage/Printing/ to storage/Completed/. job.file_path is updated.
* **Key Actions:** Staff removes print, API logs event. Asynchronous task (SendCompletionEmail) triggered.
* **Email Notification:** Completion email sent via task queue.

#### 7. PaidPickedUp
* **Trigger:** Staff clicks "Mark Picked Up" in the React UI. The frontend sends a `POST` request to `/api/jobs/<id>/mark-picked-up`.
* **File Operations:** The authoritative file and metadata.json are moved from storage/Completed/ to storage/PaidPickedUp/. job.file_path is updated.
* **Key Actions:** Student collects print, API logs event.
* **Email Notification:** None.

#### 8. Archived
* **Trigger:** An administrator triggers the archival process via the dashboard, sending a `POST` request to `/api/v1/admin/archive`. The API will process all jobs in `PaidPickedUp` or `Rejected` status that are older than the configured retention period (e.g., 90 days).
* **File Operations:** The authoritative file and `metadata.json` for each eligible job are moved from their current location (e.g., `storage/PaidPickedUp/`) to `storage/Archived/`. The job's `file_path` is updated accordingly.
* **Key Actions:** The job status is changed to `ARCHIVED`. An `Event` is logged for each job that is archived, attributed to the admin who triggered the action.
* **UI/UX**: The admin dashboard will feature a data management section where an admin can review jobs eligible for archival and trigger the process with a confirmation dialog.

**General Staff Dashboard and Job Interaction UI/UX**
- Main Dashboard Layout (/dashboard): Header, status tabs, job list
- Job Row Details: Thumbnail, student name/email, display name, submission date/time, printer/color/material, cost, action buttons, event log viewer
- Job Detail View/Modal: All job metadata, editable fields, calculated cost, full event history, staff notes (editable notes section for staff/internal use), admin override controls
- **Direct Deletion**: A 'Delete' button will be available on job cards/modals for jobs in `UPLOADED` or `PENDING` status. This action is protected by a confirmation dialog to prevent accidental deletion.
- **Time-Limited Revert Actions**: For recent status changes (e.g., `Mark Complete`), a "Revert" button will be conditionally displayed for a short period, allowing staff to quickly correct errors without needing an admin.
- **Search and Filtering**: Dashboard supports search by student name, email, class number, and filtering by printer, discipline, submission date
- **Admin Override Capabilities**: Staff can manually override broken workflows:
  - Manually confirm jobs (bypass student confirmation)
  - Resend approval/confirmation emails with new tokens
  - Arbitrarily change job status for debugging purposes
  - Handle Print Failures: Mark a job in the `PRINTING` state as failed, log the reason, and return it to the `READYTOPRINT` queue without requiring student re-approval.
  - All override actions logged in Event table with `triggered_by = 'admin'`

**Administrative Controls & Manual Overrides UI/UX**
- Status override controls, file management controls, email control during overrides, other admin actions
- **System Health Panel**: A dedicated section in the dashboard for system auditing. It will allow an admin to:
  - Trigger a new file system integrity scan.
  - View the report from the last scan, listing orphaned files and broken database links.
  - Take explicit action on reported items, such as deleting selected orphaned files.
- Notes Management: Staff can add/edit notes for any job. All changes are saved and visible to staff only.
- **Emergency Override Modal**: allows status changes with reason logging
- **Print Failure Modal**: When marking a print as failed, a modal will appear requiring staff to log a reason for the failure before confirming the action to move the job back to the `READYTOPRINT` queue.
- **Resend Email Controls**: Generate new confirmation tokens when original links expire

**Fallback/Manual Processes for Pending Status:**
- If a student doesn't confirm within the token expiry period (e.g., 72 hours), the job is visually flagged on the staff dashboard (e.g., with a yellow warning icon) so staff can take proactive measures.
- Staff can manually resend a confirmation email (generating a new token), which is a rate-limited action.
- Staff can manually mark a job as confirmed if email confirmation fails (e.g., student confirms verbally). This action is logged.
- Students have a self-service option on the "expired link" page to request a new, rate-limited confirmation email.

**Expired Token and Resend Workflow (Student-Facing)**
- **Expired Link Handling**: When a student clicks an invalid or expired confirmation link, they are directed to a user-friendly frontend page (`/confirm/expired?job_id=...`).
- **Clear Messaging**: This page will clearly state that the link has expired and explain the next steps.
- **Self-Service Resend**: The page will feature a "Resend Confirmation Email" button. Clicking this triggers a new, public, but rate-limited API endpoint to send a fresh email with a new token.
- **Throttling**: To prevent abuse, this self-service resend option is limited (e.g., once per hour per job). The UI should reflect this, disabling the button and showing a countdown if a recent request has been made.

**UI/UX Implementation Notes:**
- All status changes must provide immediate visual feedback
- Use professional loading indicators for async operations
- Implement smooth transitions between states
- Provide clear error states with recovery options
- Use consistent iconography across all status indicators
- Follow modern web animation guidelines

## 4. Technical Deep Dive: Direct File Access

> **Note:** All actions listed below automatically trigger an entry in the `Event` log as described in Section 3.2 and 3.4.

### 4.1 Single-Computer Architecture & Resilient Storage
1. **Shared File Storage:**
   - All job files stored on a network share.
   - This share must be mounted at the OS level on the single staff computer running the Flask app, ensuring a consistent path (e.g., Z:\3DPrintFiles\ or /mnt/3dprint_files).
   - The Flask app references files using this path.
   - metadata.json files reside alongside job files, providing resilient metadata handling.

> **Multi-Computer Operation:**
> The system supports running the Flask application on up to two staff computers. Both computers must mount the shared storage at the same path (e.g., both use Z:\storage\ or both use /mnt/3dprint_files/), and both must be able to connect to the same PostgreSQL database. The custom protocol handler (SlicerOpener) must be installed and registered on both computers. Path consistency is critical for correct file access and protocol handler operation.

2. **Database Strategy (PostgreSQL Recommended):**
   - Chosen Approach: The system will use PostgreSQL. The Flask application will run on the single, designated staff computer, acting as the server.
   - Rationale: While SQLite is simpler, PostgreSQL offers superior concurrency, data integrity, and scalability, even in a small lab. This provides a significantly more robust and non-fragile backend, preventing potential locking issues or data corruption, especially with asynchronous tasks or multiple browser sessions accessing the system. It's a foundational choice for long-term resilience.
   - The PostgreSQL server can run on the same staff computer or a dedicated server if available.

### 4.2 Custom Protocol Handler
- A custom URL protocol (e.g., 3dprint://) will be registered on the single staff computer.
- Example URL: 3dprint://open?path=Z:\storage\Uploaded\JaneDoe_Filament_Blue_123.stl

### 4.3 File Opening Solution
1.  **Custom Protocol Registration (Windows Example)**:
    ```
    Windows Registry:
    HKEY_CLASSES_ROOT\3dprint\shell\open\command
    (Default) = "C:\Path\To\SlicerOpener.exe" "%1"
    ```
    (A `.bat` or `.reg` file can automate this setup on staff machines).
2.  **Helper Application (`SlicerOpener.py`)**:
    *   A small Python script (compiled to `.exe` using PyInstaller) that serves as the protocol handler.
    *   **External Configuration**: The script **must** load its settings from an external configuration file (e.g., `config.ini`) located in the same directory. Hardcoding paths is not acceptable. The configuration will define:
        -   The authoritative storage base path (`AUTHORITATIVE_STORAGE_BASE_PATH`).
        -   A list of recognized slicer applications, each with a name, an absolute path to its executable, and a comma-separated list of supported file extensions (e.g., `.stl,.obj,.3mf`).
        -   The path for the local log file.
    *   **Mandatory GUI Feedback**: The script **must** use a GUI toolkit (e.g., `tkinter.messagebox`) to display all user-facing feedback. Command-line output is insufficient. This includes:
        -   Clear error dialogs for any failure (invalid URL, security validation failed, file not found, no compatible slicer configured, slicer executable not found).
        -   A success dialog confirming which file was opened in which slicer.
    *   **Security Validation**: It must perform robust security validation on the file path extracted from the URL, ensuring it is a descendant of the `AUTHORITATIVE_STORAGE_BASE_PATH` to prevent directory traversal attacks.
    *   **Slicer Dispatch Logic**: It must parse the file extension of the requested file and find all compatible slicers from the configuration file.
        -   If exactly one compatible slicer is found, it opens the file directly.
        -   If multiple compatible slicers are found, it **must** display a GUI dialog prompting the user to select which slicer to use.
        -   If no compatible slicers are found, it displays a GUI error dialog.
    *   **Logging**: All actions, configuration loads, validation results, and errors must be logged to a local file for auditing and troubleshooting.
    ```python
    # SlicerOpener.py (Conceptual, with slicer selection)
    import sys, subprocess, os, configparser
    from urllib.parse import urlparse, parse_qs
    import tkinter
    from tkinter import messagebox

    def load_config(config_path='config.ini'):
        parser = configparser.ConfigParser()
        if not parser.read(config_path):
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
        
        config = {
            'storage_base_path': parser.get('main', 'AUTHORITATIVE_STORAGE_BASE_PATH'),
            'slicers': []
        }
        for section in parser.sections():
            if section.startswith('slicer_'):
                config['slicers'].append({
                    'name': parser.get(section, 'name'),
                    'path': parser.get(section, 'path'),
                    'extensions': [ext.strip() for ext in parser.get(section, 'extensions').split(',')]
                })
        return config

    def get_compatible_slicer(file_path, slicers):
        file_ext = os.path.splitext(file_path)[1].lower()
        for slicer in slicers:
            if file_ext in slicer['extensions']:
                return slicer
        return None

    def show_error_popup(title, message):
        tkinter.Tk().withdraw() # Hide the main tkinter window
        messagebox.showerror(title, message)

    def show_success_popup(title, message):
        tkinter.Tk().withdraw() # Hide the main tkinter window
        messagebox.showinfo(title, message)
    
    def ask_slicer_choice(slicer_options):
        # This function must create a GUI dialog to ask the user to pick from a list of slicer names.
        # It should return the chosen slicer's dictionary object or None if cancelled.
        # (Conceptual implementation using tkinter would go here)
        pass

    # --- Main conceptual execution logic ---
    # 1. Load configuration from 'config.ini'.
    # 2. Parse the input URI and validate the file path for security.
    # 3. Find all compatible slicers from the configuration based on the file extension.
    # 4. Check the number of compatible slicers found:
    #    - If zero: Call show_error_popup("No Slicer Found", "No compatible slicer is configured for this file type.")
    #    - If one: Launch that slicer directly with the file path. Call show_success_popup(...).
    #    - If more than one: Call ask_slicer_choice(list_of_slicers).
    #      - If a choice is made, launch the chosen slicer. Call show_success_popup(...).
    #      - If the user cancels, do nothing.
    # 5. Handle all potential errors (file not found, slicer exe not found, etc.) with show_error_popup().
    ```

3.  **Web Dashboard Integration**:
    *   The "Open File" button in the dashboard generates the `3dprint://` link dynamically using `job.file_path`.
    ```html
    <a href="3dprint://open?path={{ job.file_path|urlencode }}">Open in Slicer</a>
    ```

### 4.4 SlicerOpener.py Protocol Handler: Functions, Security, and Integration
- **Purpose and User Story:** Enables staff to open 3D print job files directly from the web dashboard in their local slicer software with a single click.
- **Security Validation:**
  - Only files within the `AUTHORITATIVE_STORAGE_BASE_PATH` defined in `config.ini` are permitted.
  - The handler resolves all paths to absolute form and checks that they are descendants of the allowed directories.
  - Path traversal attempts (e.g., ..\, ../) and symbolic link exploits are blocked.
  - All security validation failures are logged and result in a clear GUI error dialog.
- **File Existence and Slicer Detection:**
  - The handler checks that the requested file exists before attempting to open it.
  - It determines which slicers are compatible by reading a list of slicer applications and their supported file types from an external `config.ini` file.
  - If only one compatible slicer is found, it is launched automatically.
  - If multiple compatible slicers are found, the user is presented with a GUI dialog to choose which one to use.
  - If no compatible slicer is configured or a slicer's executable is not found, a clear GUI error dialog is displayed.
- **Logging and Audit Trail:**
  - All file access attempts (successes and failures) are logged to a rotating log file whose path is defined in `config.ini`.
  - Log entries include timestamp, requested URL, resolved file path, validation result, and action taken.
  - Security violations, file errors, and slicer launch results are all recorded for audit and troubleshooting.
- **Error Handling:**
  - The script **must** use a GUI library (e.g., `tkinter`) to display user-friendly dialogs for all error and success conditions, ensuring staff receive clear feedback even outside the console.
- **Integration with Web Dashboard:**
  - The dashboard generates a `3dprint://open?path=<urlencoded_path>` link for each job's authoritative file.
  - The "Open File" button is shown for jobs in appropriate statuses (e.g., ReadyToPrint, Printing).
  - Clicking the button launches the protocol handler, which validates and opens the file in the slicer.
  - Fallback instructions are provided if the protocol handler is not installed.
- **Protocol Registration and Deployment:**
  - A Windows registry file and/or batch installer is provided to register the `3dprint://` protocol on staff computers.
  - The protocol handler deployment includes the executable and a documented `config.ini` file that must be correctly configured on each staff machine.
- **Testing and Validation:**
  - Automated and manual tests cover all security validation, file existence, and slicer detection scenarios.
  - All access attempts are verified in the log file for auditability.
  - End-to-end workflow is tested from dashboard to slicer launch.
- **Future Enhancements:**
  - Implement GUI error dialogs for all error and success conditions.
  - Add cross-platform support (e.g., macOS/Linux) if needed.
  - Enhance error handling for edge cases and improve timeout behavior.
  - Integrate with advanced dashboard features (e.g., job detail modals, admin overrides).

## 5. Operational Considerations

### 5.1 System Components & Architecture

**Backend Components:**
- **Flask API Application**: RESTful API with Blueprint organization, PostgreSQL database integration, and comprehensive job/event models
- **Clerk Authentication Integration**: JWT validation middleware, user context management, and secure API endpoint protection
- **File Management Services**: Robust file handling, cost calculation algorithms, and resilient `metadata.json` generation
- **Asynchronous Task Processing**: RQ integration for email delivery and thumbnail generation
- **Custom Protocol Handler**: `SlicerOpener.py` application with security validation and slicer integration

**Frontend Components:**
- **Next.js Application**: Modern App Router architecture with TypeScript, Tailwind CSS, and comprehensive shadcn/ui component library
- **Authentication Flow**: Seamless Clerk integration with automatic session management and protected route handling  
- **Dashboard Interface**: Real-time updating dashboard with sound notifications, visual alerts, job age tracking, and advanced filtering
- **Interactive Workflows**: Sophisticated approval/rejection modals, inline notes editing, and comprehensive form validation
- **Student Submission Interface**: Dynamic form with contextual validation, progressive disclosure, and educational content

**Integration Components:**
- **API Communication Layer**: Robust frontend-backend integration with comprehensive error handling and retry logic
- **File Protocol System**: Custom `3dprint://` protocol with security validation and cross-application file opening
- **Email Notification System**: Automated email workflows with template management and delivery tracking
- **Audit & Logging System**: Comprehensive event logging with individual user attribution and compliance-ready audit trails


### 5.2 Security Architecture & Considerations

#### 5.2.1 Authentication Security (Clerk Integration)
- **Enterprise-Grade Authentication**: Clerk provides industry-standard OAuth, JWT validation, and session management
- **Individual Staff Accountability**: Each staff member has unique credentials with full audit trail capability
- **Multi-Factor Authentication**: Optional MFA support for enhanced security based on institutional requirements
- **Session Management**: Automatic token refresh, secure cookie handling, and proper session lifecycle management
- **No Shared Credentials**: Eliminates security risks associated with shared passwords or single-point authentication failures

#### 5.2.2 Application Security
- **Secure File Upload Handling**: Comprehensive validation including file type verification, size limits, and content scanning
- **Student Confirmation Security**: Time-limited, cryptographically signed tokens using itsdangerous library with proper expiration handling
- **Path Traversal Prevention**: Strict validation of all file paths with absolute path resolution and base directory containment checks
- **API Endpoint Protection**: All state-changing requests require valid Clerk JWT authentication with proper role validation
- **Content Security Policy**: Comprehensive CSP headers to prevent XSS and other injection attacks

#### 5.2.3 System-Level Security
- **Network Share Permissions**: Properly configured read/write access for application server with restricted general user access
- **Protocol Handler Security**: `SlicerOpener.py` includes robust security validation, logging, and safe file path handling
- **Database Security**: PostgreSQL with proper connection encryption, user permissions, and regular security updates
- **Dependency Management**: Regular security updates for all dependencies with vulnerability scanning
- **Environment Variable Protection**: All sensitive configuration stored in secure environment variables, never in code

#### Logging and Retention:
- All application logs, including protocol handler access logs and error logs, should be stored with rotation enabled (e.g., using `RotatingFileHandler`).
- Logs should be retained for at least 90 days, or according to university data policies.

### 5.3 Deployment Considerations
The entire application stack is designed to be deployed using Docker and Docker Compose, which dramatically simplifies setup and ensures consistency between development and production environments.

1.  **Dockerized Services**: The `docker-compose.yml` file defines all necessary services:
    *   `backend`: The Flask API application, served by Gunicorn.
    *   `frontend`: The Next.js application. For production, this container will run `npm start` to serve the application with server-side rendering.
    *   `db`: A PostgreSQL database service, with its data persisted in a Docker volume to prevent data loss on container restart.
    *   `worker`: The RQ background worker for handling asynchronous tasks.
    *   `redis`: The message broker (Redis) for the background worker queue.

2.  **Deployment Process**:
    *   **Host Machine Setup**: One of the lab computers (or a dedicated server) will act as the host for the Docker containers. Docker and Docker Compose must be installed on this machine.
    *   **Configuration**: All environment-specific variables (database passwords, secret keys, API URLs) are managed in `.env` files that are read by Docker Compose.
    *   **Launch**: The entire application is launched with a single command: `docker-compose up -d`. This builds the necessary images and starts all services in the correct order.

3.  **Accessing the System**:
    *   Staff will access the Next.js frontend by navigating to the IP address of the host machine in their web browser (e.g., `http://192.168.1.50`).
    *   The Next.js application is pre-configured in its Docker environment to communicate with the `backend` service via Docker's internal networking.

4.  **External Components**:
    *   **Network Storage**: The shared `storage/` directory must be mounted on the Docker host machine. This path is then passed into the `backend` container as a volume mount, allowing the Flask API to read and write job files.
    *   **SlicerOpener Protocol Handler**: The `SlicerOpener.exe` and its `config.ini` must be installed locally on **each** staff computer. The `config.ini` on each machine must point to the correct path for the shared network storage.

5. **CORS Configuration**: In production, the Flask API's CORS settings must be restricted to allow requests only from the domain (or IP address) where the Next.js frontend is hosted. This is configured via environment variables.

### 5.4 University Network Considerations
- Firewalls: May block custom protocols or outgoing connections for the helper app. Liaise with IT.
- Server Restrictions: University IT may have policies against running persistent servers or specific ports.
- Admin Rights: Registering protocol handlers or installing software might require admin rights. The helper app can be deployed to user-space if packaged correctly.
- Storage Quotas: Be mindful of file sizes and implement cleanup if quotas are restrictive.
- Alternative File Access: If custom protocol is unfeasible, a fallback could be instructing staff to copy a displayed network path, or a less ideal "download and open".
- **Email Deliverability**: To minimize the risk of emails being marked as spam, the outgoing mail server must be correctly configured with SPF and DKIM records. This should be coordinated with university IT.

### 5.5 Cost Matrix & Calculation
- Filament Print Cost: $0.10 per gram.
- Resin Print Cost: $0.20 per gram.
- $3.00 minimum charge for all print jobs.
- The system enforces the minimum charge and calculates cost based on material and weight.

### 5.6 Metrics & Reporting
- Usage statistics: submission counts, trends, printer utilization.
- Reporting interface: (future) CSV/Excel export, filterable views, basic charts.

### 5.7 Data Retention and Archival Policy
The system implements a two-stage process for data lifecycle management to ensure both data availability for a reasonable period and eventual cleanup.

- **Stage 1: Archival (Semi-Automated)**
  - **Retention Period**: Job data and associated files for jobs in a final state (`PaidPickedUp` or `Rejected`) will be retained in an active state for 90 days.
  - **Archival Process**: After 90 days, these jobs become eligible for archival. An admin-triggered process (`POST /api/v1/admin/archive`) moves the job status to `ARCHIVED` and relocates the associated files to a `storage/Archived/` directory. This keeps the database record for historical purposes while cleaning up the active file storage. This action is fully logged in the `Event` table.

- **Stage 2: Permanent Deletion (Manual Trigger)**
  - **Deletion Policy**: Jobs in the `ARCHIVED` state will be retained for 1 year. After this period, they are eligible for permanent deletion.
  - **Deletion Process**: A separate, deliberate admin-triggered process (`POST /api/v1/admin/prune`) permanently deletes the job's database record and its archived files. This is a destructive, non-recoverable action that requires explicit confirmation and is fully logged.

- **Active Jobs**: Jobs in `Uploaded`, `Pending`, `ReadyToPrint`, `Printing`, or `Completed` statuses are considered active and are not subject to this policy until they reach a final state.

### 5.8 Backup and Disaster Recovery
A comprehensive, automated backup strategy is critical for business continuity. This strategy covers both the PostgreSQL database and the shared file storage, with a clear recovery plan to minimize downtime and ensure data integrity.

**1. Automated Backup Strategy**
- **Automation & Synchronization**: A single, automated backup script will run daily during off-peak hours (e.g., 3:00 AM). The script will first execute the database dump and, immediately upon its completion, begin the file system backup. This sequential process minimizes the time window between the two snapshots, ensuring they are closely synchronized.
- **Database Backup**: The script will use `pg_dump` to create a complete SQL dump of the PostgreSQL database.
- **File Storage Backup**: The script will use a versioning backup tool like `rsync` to create an incremental backup of the entire `storage/` directory.
- **Secure Off-Site Storage**: Backups **must** be pushed to a secure, remote location that is physically separate from the application host (e.g., a university-provided secure network drive or a designated cloud storage bucket). This protects against data loss from local hardware failure or disaster.
- **Retention Policy**:
    - Daily backups are retained for 14 days.
    - A weekly backup (e.g., from Sunday) is retained for 2 months.
    - A monthly backup is retained for 1 year.
- **Monitoring & Alerts**: The backup script will log its execution and send an email alert to a designated admin address upon success or failure.

**2. Recovery Plan & Procedure**
This plan outlines the steps to restore the system to a functional state from a chosen backup set (a matching pair of database and file system backups).
- **Responsibility**: Lab staff are responsible for initiating and overseeing the recovery process.
- **Step-by-Step Restore Procedure**:
    1.  **Halt the System**: Stop all running application services using the `docker-compose down` command.
    2.  **Prepare for Restore**: Clear the current (corrupted or empty) Docker volumes for the database and the contents of the `storage/` directory on the host machine.
    3.  **Restore File System**: Copy the contents of the chosen file storage backup into the host's `storage/` directory.
    4.  **Restore Database**: Restore the database from the corresponding `pg_dump` backup file. This involves starting the `db` service, copying the SQL dump file into the container, and using the `psql` utility to load the data.
    5.  **Restart System**: Start all application services with `docker-compose up -d`.
    6.  **Verify Integrity**: Once the system is running, an administrator **must** immediately trigger a **System Health and Integrity Audit** (as defined in Section 5.9). This crucial final step identifies and allows for the correction of any minor inconsistencies between the restored database and file system that may have occurred if a job was being processed during the backup window.

**3. Backup Validation**
- To ensure backups are viable, lab staff are responsible for performing a test restore to a non-production environment on a quarterly basis. This validates both the integrity of the backups and the accuracy of the recovery plan.

### 5.9 System Health and Integrity Auditing
To ensure long-term data resilience, the system will include an admin-triggered integrity audit tool to identify and resolve discrepancies between the database and the file storage. This process is crucial for preventing orphaned files and broken database links, and serves as the recovery mechanism for incomplete file transactions.

- **Three-Way Integrity Scan**: The tool will perform a comprehensive scan:
    1.  **Filesystem to Database (Orphaned Files)**: It scans all `storage/` directories and verifies that each job file has a corresponding, active entry in the database. Files without a database entry are flagged as "Orphaned."
    2.  **Database to Filesystem (Broken Links)**: It iterates through all job records in the database and confirms that the `file_path` and `metadata_path` point to existing files on the disk. Entries with missing files are flagged as having a "Broken Link."
    3.  **Database to Filesystem (Stale Files)**: It checks for files that share a job ID with a database record but are located in a directory that does *not* match the status recorded in the database. This specifically identifies remnants of incomplete "copy-then-delete" operations, flagging them as "Stale" and safe for deletion.

- **Admin-Driven Resolution**: The audit tool will **not** automatically delete or modify any data. Instead, it will:
    -   Generate a detailed report listing all identified orphans, broken links, and stale files.
    -   Present this report to the administrator in a dedicated "System Health" section of the dashboard.
    -   Provide the administrator with the tools to safely resolve issues (e.g., a button to delete selected orphaned or stale files, or to flag a job with a broken link for manual review). All resolution actions will be logged in the `Event` table.

### 5.10 Professional UI Design Patterns (PROVEN SUCCESSFUL)
- Card-style dashboard interface, anti-redundancy principles, time display and management, display name formatting system, template filters, and all other proven UI/UX patterns as detailed in section 6.

### 5.11 Development Implementation Lessons
- PowerShell compatibility, path handling, Flask-WTF integration, template management, JavaScript implementation patterns, form UX requirements, database migration best practices, and all other lessons learned as detailed in section 6.

**UI/UX Lessons:**
- Always implement form validation with real-time feedback
- Use proper error scrolling to guide users
- Implement loading states for all async operations
- Follow modern accessibility guidelines strictly
- Test all UI components across different screen sizes
- Ensure proper keyboard navigation support

**Technical Lessons:**
- Verify file operations with explicit success checks
- Log all file system operations for debugging
- Handle network share disconnections gracefully
- Implement proper error handling for email operations
- Use atomic file operations where possible
- Always validate file paths before operations

**Process Lessons:**
- Document all configuration changes in version control
- Maintain a separate development environment
- Test email templates with various email clients
- Verify protocol handler registration after system updates
- Keep comprehensive logs of all system changes
- Document all custom UI components and their usage

### 5.12 Critical Success Factors
1. **File System Integrity:**
   - Regular validation of file locations
   - Automated metadata.json consistency checks
   - Proper error handling for file operations
   - Regular backup verification

2. **User Experience:**
   - Strict adherence to modern UI/UX design principles
   - Consistent feedback for all operations
   - Clear error messages and recovery paths
   - Proper form validation and guidance

3. **System Reliability:**
   - Regular health checks for all components
   - Proper logging of all operations
   - Graceful handling of network issues
   - Regular backup procedures

4. **Staff Efficiency:**
   - Streamlined workflow processes
   - Clear status indicators
   - Easy access to file operations
   - Proper error recovery procedures

### 5.13 Known Issues and Workarounds
1. **Network Share Access:**
   - Implement retry logic for file operations
   - Cache file metadata when possible
   - Provide clear error messages for access issues
   - Document recovery procedures

2. **Protocol Handler:**
   - Regular verification of registry entries
   - Fallback procedures for failed operations
   - Clear documentation for reinstallation
   - Logging of all handler operations

3. **Email Delivery:**
   - Implement retry logic for failed sends
   - Queue messages for later delivery
   - Monitor delivery success rates
   - Document SPF/DKIM requirements

4. **UI Components:**
   - Test across different browsers
   - Verify mobile responsiveness
   - Document accessibility features
   - Maintain consistent styling

### 5.14 Event Log Management and Data Retention

**Event Log Rotation Policy:**
- The `Event` table will implement automatic cleanup to prevent unlimited growth
- Events older than 180 days will be archived to flat files or deleted based on operational needs
- Critical events (job creation, status changes, admin overrides) will be retained longer than routine events
- Database indexes on `job_id`, `timestamp`, and `event_type` for optimal query performance
- Weekly automated cleanup jobs to maintain database performance

**Event Storage Strategy:**
- High-priority events: Retain for 1 year (job creation, approvals, rejections, completions)
- Medium-priority events: Retain for 180 days (status changes, email sends, file operations)
- Low-priority events: Retain for 90 days (dashboard views, search queries, routine operations)
- Archive format: JSON files organized by date for potential future analysis

### 5.15 Student Resubmission Workflow

**Rejected Job Resubmission:**
- Students can submit new jobs after rejection - no automatic resubmission linking required
- Original rejected jobs remain in system for staff reference and learning
- Staff notes from rejected jobs can inform future submissions
- Optional: Future enhancement to link related submissions via `related_job_id` field

**Handling Lab-Caused Print Failures:**
- If a print fails due to an issue under the lab's control (e.g., machine error), staff will use an administrative action to mark the job as failed from the `PRINTING` status.
- This action logs the failure and its reason, and returns the job to the `READYTOPRINT` status to be printed again.
- There is no cost adjustment needed as the original cost is retained, and no new student confirmation is required. This action is fully logged for auditing.

**Resubmission Tracking (Future Enhancement):**
- Optional `parent_job_id` field to link resubmissions to original jobs
- Dashboard view to see submission history per student
- Analytics on common rejection reasons to improve student guidance

### 5.16 System Health and Service Monitoring
To ensure high availability and prevent silent failures of critical backend components, the system will include a dedicated health monitoring endpoint. This is distinct from the data integrity audit and focuses on the operational status of the services themselves.

- **Health Check Endpoint**: A public, unauthenticated API endpoint (`GET /api/v1/health`) will be implemented. This endpoint will allow automated monitoring tools (e.g., UptimeRobot, university IT monitoring) to check the system's status without requiring credentials.
- **Component Status Checks**: The health check will verify the status of all critical infrastructure components:
    1.  **API Service**: The endpoint responding with a `200 OK` status confirms the Flask API is running.
    2.  **Database Connectivity**: The endpoint will attempt a simple, non-locking query (e.g., `SELECT 1`) to confirm the database is reachable and responsive.
    3.  **Background Worker Connectivity**: The endpoint will check the connection to the message broker (e.g., Redis) used by RQ to ensure background tasks can be queued and processed.
- **Alerting**: If the health check endpoint fails to respond or reports a failure in any component, an external monitoring service is expected to automatically trigger alerts (e.g., email, SMS) to designated system administrators (lab staff), enabling rapid response to outages.

### 5.17 Concurrency Control and Data Integrity
To ensure data consistency and prevent race conditions in a multi-user, multi-computer environment, the system will implement the following safeguards:

- **API-Level Job Locking**: To prevent two staff members from simultaneously performing conflicting state-changing actions on the same job, the system will use a robust, stateful, API-level locking mechanism.
    - **Acquiring a Lock**: Before initiating a critical action (e.g., opening an approval modal), the frontend will first request a lock from the backend. The API will set a `locked_by_user` field and a `locked_until` timestamp (e.g., 5 minutes in the future) on the job.
    - **Lock Heartbeat**: While a user has a job locked for an extended UI interaction (like an open modal), the frontend will automatically send a periodic "heartbeat" request to extend the lock's duration. This prevents the lock from expiring during legitimate use.
    - **Releasing a Lock**: When the user completes or cancels the action, the frontend will explicitly release the lock. Critical state-changing API endpoints will also automatically release the lock upon successful completion.
    - **Handling Conflicts & UI Feedback**: If a user attempts to lock an already-locked job, the API will return a `409 Conflict` error, including who holds the lock. The UI must handle this gracefully by displaying a notification (e.g., "This job is being edited by Jane Doe") and disabling editing controls.
    - **Surfacing Lock Status**: The `GET /jobs` and `GET /jobs/<job_id>` endpoints will include the current lock status in their responses, allowing the UI to proactively show if a job is locked.
    - **Automatic Expiration & Admin Override**: The automatic expiration serves as a fallback for abandoned sessions. For truly "stuck" locks, an administrator will have a dedicated API endpoint to forcibly release them, with the action being fully audited.

- **Transactional File Operations**: All workflows that involve both database updates and file system modifications (e.g., approving a job) must be designed for resilience against unexpected failures (e.g., a server crash). The strategy is to ensure the database remains the "source of truth" and that inconsistencies can be detected and corrected.
    - **Resilient Workflow ("Copy, Update, then Delete")**: Instead of a simple "move" operation, the sequence will be:
        1.  **Copy**: The authoritative file is first *copied* to the destination directory (e.g., from `/Uploaded` to `/Pending`).
        2.  **Update Database**: Within a database transaction, the job's status and file path are updated to reflect the new location.
        3.  **Commit**: The database transaction is committed. At this point, the system's "source of truth" now correctly points to the new file.
        4.  **Delete Original**: The original file in the source directory is deleted.
    - **Recovery Path**: If a crash occurs between steps 3 and 4, the system is left in a consistent state from the database's perspective, but a stale, duplicate file now exists in the old directory. This is not an error that affects live operations but is a cleanup task. The **System Health and Integrity Audit** is designed to detect and resolve exactly this scenario by identifying files that exist in storage but do not match the authoritative path in the database.

### 5.18 Staff-Level Error Correction
To handle common human errors gracefully without requiring administrator intervention, the system will provide a "revert" capability for certain status changes. This empowers staff to correct their own mistakes quickly and cleanly.

- **Contextual Revert Actions**: After a staff member changes a job's status, a contextual "Revert" button will appear in the UI.
- **Supported Reversions**: This functionality will be available for specific, non-destructive transitions, such as:
    - Reverting a job from `COMPLETED` back to `PRINTING`.
    - Reverting a job from `PAIDPICKEDUP` back to `COMPLETED`.
- **Workflow**:
    - The revert action is a dedicated API endpoint (e.g., `POST /jobs/<job_id>/revert-completion`).
    - The backend validates that the revert action is valid for the job's current state.
    - The action is transactional, ensuring both the database status and file location are correctly rolled back.
    - A `StatusReverted` event is logged in the job's audit trail, including which staff member triggered the reversion.
- **Scope**: This is not a general "undo" feature. It does not apply to destructive actions or actions that trigger external communications (like sending a student approval email). For more complex corrections, the Admin Override workflow is still required.

### 5.19 Duplicate Submission Handling
To prevent accidental or redundant job submissions, the system will implement content-based deduplication at the API level.

- **File Content Hashing**: Upon every file upload via the `POST /api/submit` endpoint, the backend will calculate a SHA-256 hash of the file's contents.
- **Deduplication Logic**: Before creating a new job, the API will query the database to see if an "active" job already exists with the same file hash and the same student email address.
    - An "active" job is defined as being in any status *before* printing has begun (e.g., `UPLOADED`, `PENDING`, `READYTOPRINT`).
- **Collision Handling**:
    - If an identical active job is found, the submission will be rejected with a `409 Conflict` error. The API response will inform the user that a duplicate job already exists.
    - If no identical active job is found, the new job is created, and the calculated `file_hash` is stored in the database.
- **Allowing Reprints**: This logic explicitly allows a student to submit the same file again if their previous job is already `PRINTING`, `COMPLETED`, or in another post-active state, as this is considered a legitimate request for a reprint.

### 5.20 Direct Job Deletion
To provide staff with an efficient way to remove erroneous, unwanted, or duplicate submissions, the system will include a direct, permanent deletion capability.

- **Purpose**: This workflow is intended for immediate cleanup of the active queue and is not part of the standard job lifecycle (like archival).
- **Scope**: Deletion is a destructive action and is therefore only permitted for jobs in `UPLOADED` or `PENDING` statuses. It cannot be performed on jobs that have been confirmed by a student or have entered the production queue.
- **Confirmation Required**: Because this action is irreversible, it **must** be protected by a confirmation modal in the frontend. The modal will clearly state that the job and all its associated files will be permanently deleted.
- **Workflow**:
    1.  A staff member clicks a "Delete" button on an eligible job.
    2.  The confirmation modal appears. Upon confirmation, the frontend sends a `DELETE /api/v1/jobs/<job_id>` request.
    3.  The backend API validates that the job is in a deletable status.
    4.  The API executes the deletion as a transaction: it permanently deletes the job's files from the network storage, then deletes the job's record and all associated event logs from the database.
- **Auditing**: All delete actions will be logged to a separate, secure, system-level audit log, recording the job ID, student details, and the staff member who performed the deletion.

## 6. API Specification 

All endpoints will be prefixed with `/api/v1`. All responses will be in JSON format. Timestamps are in UTC ISO 8601 format.

---
**Authentication (Clerk Integration)**

*Note: Authentication is handled entirely by Clerk. The Flask backend validates Clerk-issued JWTs.*

*   **JWT Validation Middleware**: All protected endpoints validate Clerk JWTs in the `Authorization: Bearer <token>` header
*   **User Context**: Clerk user ID and profile information extracted from validated JWTs
*   **No Custom Login Endpoint**: Authentication handled by Clerk's hosted UI and SDK
*   **Automatic Token Refresh**: Clerk SDK handles token refresh automatically on the frontend
*   **Session Management**: Clerk manages all session lifecycle, logout, and security features

**Authentication Headers for Protected Endpoints:**
*   `Authorization: Bearer <clerk_jwt_token>`
*   **Success**: Request proceeds with user context available
*   **Error (401)**: `{ "message": "Invalid or expired token" }`
*   **Error (403)**: `{ "message": "Insufficient permissions" }`

---
**Public System Health**

*   `GET /health`
    *   **Description**: Provides a simple health check of the backend services. Does not require authentication. Intended for use by automated monitoring tools.
    *   **Success (200)**: Returns the operational status of key components. Example: `{ "status": "ok", "timestamp": "...", "components": { "database": "ok", "workers": "ok" } }`
    *   **Error (503 Service Unavailable)**: Returns if a critical component is down. Example: `{ "status": "error", "timestamp": "...", "components": { "database": "ok", "workers": "error", "details": "Could not connect to message broker." } }`

---
**Student Submission**

*   `POST /submit`
    *   **Body**: `multipart/form-data` with fields for `student_name`, `student_email`, `file`, etc.
    *   **Success (201)**: Returns the newly created job object.
    *   **Error (400)**: Returns validation errors.
    *   **Error (409)**: `{ "message": "An identical active job has already been submitted.", "existing_job_id": "..." }`
    *   **Error (429)**: `{ "message": "Submission limit exceeded. Please try again later." }`

*   `POST /confirm/<token>`
    *   **Body**: (Empty)
    *   **Success (200)**: Returns the updated job object.
    *   **Error (404/400)**: If token is invalid or expired.
    *   **Error (410)**: `{ "message": "Confirmation link expired", "reason": "expired", "job_id": "abc123" }`

*   `GET /confirm/expired`
    *   **Query Params**: `?job_id=abc123`
    *   **Success (200)**: Returns job details and instructions for expired confirmation

*   `POST /submit/resend-confirmation`
    *   **Description**: Allows a student to request a new confirmation email for an unconfirmed job. This is a public but rate-limited endpoint.
    *   **Body**: `{ "job_id": "..." }`
    *   **Success (200)**: `{ "message": "A new confirmation email has been sent." }`
    *   **Error (404)**: If job ID is not found or job is already confirmed/rejected.
    *   **Error (429)**: `{ "message": "You can request a new email in X minutes." }`

---
**Staff Dashboard**

*   `GET /jobs`
    *   **Query Params**: `?status=UPLOADED&search=student_name&printer=prusa_mk4s&discipline=Engineering&confirmation_expired=true` (all optional)
    *   **Auth**: Required (Clerk JWT)
    *   **Success (200)**: `{ "jobs": [job_object_1, job_object_2, ...], "total": 25, "filtered": 10 }`

*   `GET /jobs/<job_id>`
    *   **Auth**: Required (Clerk JWT)
    *   **Success (200)**: Returns the full `job_object`, including its event history.

*   `DELETE /jobs/<job_id>`
    *   **Auth**: Required (Clerk JWT)
    *   **Description**: Permanently deletes a job and its associated files. This action is irreversible and only permitted for jobs in 'UPLOADED' or 'PENDING' status. The requesting user must hold the lock on the job.
    *   **Success (204 No Content)**: The job was successfully deleted.
    *   **Error (403 Forbidden)**: If the user tries to delete a job that is not in a deletable status, or if the user does not hold the lock.
    *   **Error (404 Not Found)**: If the job doesn't exist.

*   `POST /jobs/<job_id>/lock`
    *   **Auth**: Required (Clerk JWT)
    *   **Description**: Acquires an exclusive lock on a job to prevent concurrent edits.
    *   **Success (200)**: `{ "message": "Job locked successfully", "locked_until": "timestamp" }`
    *   **Error (409 Conflict)**: `{ "message": "Job is currently locked by another user.", "locked_by": "Jane Doe", "locked_until": "timestamp" }`

*   `POST /jobs/<job_id>/unlock`
    *   **Auth**: Required (Clerk JWT)
    *   **Description**: Releases an exclusive lock on a job.
    *   **Success (200)**: `{ "message": "Job unlocked successfully." }`

*   `POST /jobs/<job_id>/lock/extend`
    *   **Auth**: Required (Clerk JWT)
    *   **Description**: Extends the duration of an existing lock (heartbeat).
    *   **Success (200)**: `{ "message": "Lock extended successfully", "locked_until": "timestamp" }`
    *   **Error (403 Forbidden)**: If the user does not hold the lock.

*   `POST /jobs/<job_id>/approve`
    *   **Auth**: Required (Clerk JWT)
    *   **Description**: Approves a job. The requesting user must hold the lock. The lock is released upon success.
    *   **Body**: `{ "weight_g": 25.5, "time_hours": 3.5, "material": "Filament", "printer": "prusa_mk4s" }`
    *   **Success (200)**: Returns the updated job object. Logs approval with Clerk user attribution.
    *   **Error (403 Forbidden)**: `{ "message": "You do not hold the lock for this job." }`

*   `POST /jobs/<job_id>/reject`
    *   **Auth**: Required (Clerk JWT)
    *   **Description**: Rejects a job. The requesting user must hold the lock. The lock is released upon success.
    *   **Body**: `{ "reasons": ["Model is not manifold", "Other"], "custom_reason": "The model is too thin to print." }`
    *   **Success (200)**: Returns the updated job object. Logs rejection with Clerk user attribution.
    *   **Error (403 Forbidden)**: `{ "message": "You do not hold the lock for this job." }`

*   `POST /jobs/<job_id>/mark-printing`
    *   **Auth**: Required (Clerk JWT)
    *   **Description**: Marks a job as printing. The requesting user must hold the lock. The lock is released upon success.
    *   **Success (200)**: Returns the updated job object. Logs status change with Clerk user attribution.
    *   **Error (403 Forbidden)**: `{ "message": "You do not hold the lock for this job." }`

*   `POST /jobs/<job_id>/mark-complete`
    *   **Auth**: Required (Clerk JWT)
    *   **Description**: Marks a job as complete. The requesting user must hold the lock. The lock is released upon success.
    *   **Success (200)**: Returns the updated job object. Logs completion with Clerk user attribution.
    *   **Error (403 Forbidden)**: `{ "message": "You do not hold the lock for this job." }`

*   `POST /jobs/<job_id>/mark-picked-up`
    *   **Auth**: Required (Clerk JWT)
    *   **Description**: Marks a job as picked up. The requesting user must hold the lock. The lock is released upon success.
    *   **Success (200)**: Returns the updated job object. Logs pickup with Clerk user attribution.
    *   **Error (403 Forbidden)**: `{ "message": "You do not hold the lock for this job." }`

*   `POST /jobs/<job_id>/review`
    *   **Auth**: Required (Clerk JWT)
    *   **Body**: `{ "reviewed": true }` (or `false` to mark as unreviewed)
    *   **Success (200)**: Returns the updated job object. Updates `staff_viewed_at` with Clerk user attribution.

*   `PATCH /jobs/<job_id>/notes`
    *   **Auth**: Required (Clerk JWT)
    *   **Description**: Updates the notes for a job. The requesting user must hold the lock.
    *   **Body**: `{ "notes": "Staff notes go here." }`
    *   **Success (200)**: Returns the updated job object. Logs notes update with Clerk user attribution.
    *   **Error (403 Forbidden)**: `{ "message": "You do not hold the lock for this job." }`

*   `POST /jobs/<job_id>/revert-completion`
    *   **Auth**: Required (Clerk JWT)
    *   **Description**: Reverts a job from `COMPLETED` back to `PRINTING`.
    *   **Success (200)**: Returns the updated job object. Logs `StatusReverted` event.

*   `POST /jobs/<job_id>/revert-pickup`
    *   **Auth**: Required (Clerk JWT)
    *   **Description**: Reverts a job from `PAIDPICKEDUP` back to `COMPLETED`.
    *   **Success (200)**: Returns the updated job object. Logs `StatusReverted` event.

---
**Admin Override Endpoints**

*   `POST /jobs/<job_id>/admin/force-unlock`
    *   **Auth**: Required (Clerk JWT, Admin role)
    *   **Description**: Forcibly releases a lock on a job.
    *   **Body**: `{ "reason": "User browser crashed, releasing stuck lock." }`
    *   **Success (200)**: `{ "message": "Lock has been forcibly released." }`. Logs an `AdminAction` event.

*   `POST /jobs/<job_id>/admin/force-confirm`
    *   **Auth**: Required (Clerk JWT)
    *   **Body**: `{ "reason": "Student confirmed verbally", "bypass_email": true }`
    *   **Success (200)**: Returns the updated job object. Logs admin override event with Clerk user attribution.

*   `POST /jobs/<job_id>/admin/change-status`
    *   **Auth**: Required (Clerk JWT)
    *   **Body**: `{ "new_status": "READYTOPRINT", "reason": "Debugging workflow issue" }`
    *   **Success (200)**: Returns the updated job object. Logs admin override event with Clerk user attribution.

*   `POST /jobs/<job_id>/admin/mark-failed`
    *   **Auth**: Required (Clerk JWT)
    *   **Description**: Marks a job in the `PRINTING` status as failed due to lab error and returns it to the `READYTOPRINT` queue.
    *   **Body**: `{ "reason": "Filament tangle detected on printer." }`
    *   **Success (200)**: Returns the updated job object. Logs a `PrintFailed` event with the provided reason and an `AdminAction` event.

*   `POST /jobs/<job_id>/admin/resend-email`
    *   **Auth**: Required (Clerk JWT)
    *   **Description**: Allows staff to resend a notification email. This action is rate-limited.
    *   **Body**: `{ "email_type": "approval" }` (options: "approval", "rejection", "completion")
    *   **Success (200)**: `{ "message": "Email resent successfully", "new_token": "abc123" }`. Logs email resend with Clerk user attribution.
    *   **Error (429)**: `{ "message": "An email was sent recently. Please wait before resending." }`
    *   **Error (409)**: `{ "message": "Job is currently locked by another user." }`

---
**Admin System Health**

*   `POST /admin/audit/start`
    *   **Description**: Triggers a new system health and integrity scan. This will be an asynchronous task.
    *   **Auth**: Required (Clerk JWT, Admin role)
    *   **Success (202)**: `{ "message": "System audit started successfully.", "task_id": "some-async-task-id" }`. Logs the `AdminAction` event.

*   `GET /admin/audit/report`
    *   **Description**: Retrieves the report from the last completed system health scan.
    *   **Auth**: Required (Clerk JWT, Admin role)
    *   **Success (200)**: `{ "report_generated_at": "timestamp", "orphaned_files": ["path/to/orphan1.stl"], "broken_links": [{"job_id": "abc", "missing_path": "path/to/missing.stl"}] }`.

*   `DELETE /admin/audit/orphaned-file`
    *   **Description**: Deletes a specific orphaned file from the storage. This action is logged.
    *   **Auth**: Required (Clerk JWT, Admin role)
    *   **Body**: `{ "file_path": "path/to/orphan1.stl" }`
    *   **Success (200)**: `{ "message": "Orphaned file deleted successfully." }`. Logs the `FileDeleted` event with admin attribution.

---
**Admin Data Management**

*   `POST /admin/archive`
    *   **Description**: Triggers the archival of all jobs in a final state (`PaidPickedUp`, `Rejected`) that are older than the specified retention period.
    *   **Auth**: Required (Clerk JWT, Admin role)
    *   **Body**: `{ "retention_days": 90 }` (Optional, defaults to 90)
    *   **Success (200)**: `{ "message": "Archival process completed", "jobs_archived": 12 }`. Logs a single `AdminAction` event for the batch operation, and individual `JobArchived` events for each job.

*   `POST /admin/prune`
    *   **Description**: Permanently deletes all jobs in the `ARCHIVED` state that are older than the specified retention period. This is a destructive action.
    *   **Auth**: Required (Clerk JWT, Admin role)
    *   **Body**: `{ "retention_days": 365 }` (Optional, defaults to 365)
    *   **Success (200)**: `{ "message": "Pruning process completed", "jobs_deleted": 5 }`. Logs an `AdminAction` event and individual `JobDeleted` events for each job that is pruned.

---
**Dashboard Stats & Analytics**

*   `GET /stats`
    *   **Auth**: Required (Clerk JWT)
    *   **Success (200)**: `{ "uploaded": 10, "pending": 5, "readyToPrint": 3, "storage_usage_mb": 1024, "storage_limit_mb": 10240 }`

*   `GET /stats/detailed`
    *   **Auth**: Required (Clerk JWT) 
    *   **Query Params**: `?days=30&printer=all&discipline=all` (optional)
    *   **Success (200)**: Detailed analytics including submission trends, printer utilization, common rejection reasons, and staff activity metrics

**API Response Standards:**
- All timestamps in UTC ISO 8601 format
- All file sizes in bytes unless otherwise specified
- All monetary amounts in USD cents (e.g., 300 = $3.00)
- Consistent error response format: `{ "error": "error_code", "message": "Human readable message", "details": {...} }`
- All list endpoints support pagination via `?page=1&limit=50` parameters
- All protected endpoints log access attempts for security auditing
