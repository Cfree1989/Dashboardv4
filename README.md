# 3D Print Management System

A beginner-friendly Flask API + Next.js dashboard system for managing 3D print jobs in academic/makerspace environments.

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd Dashboardv4
   ```

2. **Docker Development**
   ```bash
   docker-compose up -d
   ```

3. **Access the System**
   - Student Submission: `http://localhost:3000/submit`
   - Staff Dashboard: `http://localhost:3000/dashboard`
   - API Documentation: `http://localhost:5000/api/v1/health`

## System Overview

- **Backend**: Flask API-only with PostgreSQL database
- **Frontend**: Next.js with TypeScript and Tailwind CSS
- **Authentication**: Workstation-based with per-action staff attribution
- **File Management**: Network-mounted storage with status-based directories
- **Background Tasks**: RQ for email notifications and thumbnail generation

## Key Features

- Student 3D model submission with email confirmation
- Staff approval workflow with cost calculation
- Direct file opening in slicer software via custom protocol
- Real-time dashboard with sound notifications
- Comprehensive audit trail and event logging
- Payment tracking and financial reporting

## Documentation Structure

- `/docs/requirements/` - User stories and workflow specifications
- `/docs/context/` - Glossary and style guidelines
- `/docs/examples/` - Code patterns and samples
- `/docs/api/` - API endpoint documentation
- `/diagrams/` - System architecture and workflow diagrams

## Development

See `CURSOR.md` for AI coding assistant tips and common commands.

For detailed implementation guidance, refer to `project-info.md`.