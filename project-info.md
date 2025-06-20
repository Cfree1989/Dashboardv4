# Project Information

## Project Goals

This project builds a Flask-based 3D print job management system specifically designed for beginners. The system is tailored for an academic/makerspace setting with up to two staff members operating concurrently on separate computers. It uses a workstation-based login system with per-action staff attribution and is designed with safeguards to prevent data conflicts and race conditions inherent in a multi-user environment.

### Key Design Principles

- **Beginner-friendly implementation** with clear, step-by-step guidance and minimal complexity
- **API-driven architecture** with Flask backend and Next.js frontend
- **Multi-user support** for up to two staff computers
- **Comprehensive job tracking** from submission to completion
- **File integrity** throughout the entire workflow
- **Staff accountability** through attribution and event logging

## Domain Glossary

| Term | Definition |
|------|------------|
| **Workstation** | A physical computer terminal in the lab with its own shared, long-lived password |
| **Staff Attribution** | The practice of requiring staff to select their name for every state-changing action |
| **Job** | A 3D print request submitted by a student |
| **Event Log** | Immutable audit trail for all system actions |
| **Protocol Handler** | Custom `3dprint://` URL scheme to open files in local slicer software |
| **Slicer** | Software used to prepare 3D models for printing |
| **metadata.json** | File containing essential job details stored alongside the 3D model file |
| **Authoritative File** | The specific file version that should be used for printing |

### Job Statuses

| Status | Description | Directory |
|--------|-------------|-----------|
| **UPLOADED** | Initial submission by student | `storage/Uploaded/` |
| **PENDING** | Approved by staff, awaiting student confirmation | `storage/Pending/` |
| **READYTOPRINT** | Confirmed by student, ready for printing | `storage/ReadyToPrint/` |
| **PRINTING** | Currently being printed | `storage/Printing/` |
| **COMPLETED** | Print finished, waiting for pickup | `storage/Completed/` |
| **PAIDPICKEDUP** | Paid for and picked up by student | `storage/PaidPickedUp/` |
| **REJECTED** | Rejected by staff | `storage/Archived/` (eventually) |
| **ARCHIVED** | Final storage for completed jobs | `storage/Archived/` |

## Coding Conventions

### Status Name Standardization

- **Internal Identifiers (API, Code, Database):** UPPERCASE
  - Example: `UPLOADED`, `PENDING`, `READYTOPRINT`
  - Used in: API endpoints, TypeScript types, database values, conditional logic

- **Directory Names:** PascalCase
  - Example: `Uploaded/`, `Pending/`, `ReadyToPrint/`
  - Used in: File system organization

- **User Interface:** Title Case with spaces
  - Example: "Uploaded", "Pending", "Ready to Print"
  - Used in: Dashboard displays, modals, status indicators

### File Naming Convention

Standardized file naming: `FirstAndLastName_PrintMethod_Color_SimpleJobID.original_extension`

Example: `JaneDoe_Filament_Blue_123.stl`

### Backend (Flask API-Only)

- RESTful API with Blueprint organization
- API-only endpoints - no HTML templates or server-side rendering
- PostgreSQL with SQLAlchemy ORM
- RQ for background jobs (emails, thumbnail generation)
- Flask-Mail with Office 365 SMTP
- Comprehensive error handling and logging
- File operations use resilient "copy, update, then delete" pattern

### Frontend (Next.js App Router)

- Next.js 14+ with App Router and TypeScript
- Tailwind CSS for styling
- shadcn/ui component library (Radix UI primitives)
- React Context for dashboard state management
- Browser Audio API for sound notifications
- Comprehensive client-side validation
- Mobile-first responsive design 