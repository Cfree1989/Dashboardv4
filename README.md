# 3D Print System

A Flask-based 3D print job management system with a Next.js frontend, designed for academic/makerspace settings.

## Quick Start Guide

1. **Prerequisites**
   - Docker and Docker Compose
   - Network shared storage accessible by all staff computers
   - Staff computers must have SlicerOpener protocol handler installed

2. **Setup**
   - Clone this repository
   - Configure environment variables in `.env` files
   - Run `docker-compose up -d` to start all services
   - Access the dashboard at `http://<host-ip>`

## Documentation Index

- [Project Information](project-info.md) - Project goals, glossary, and conventions
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute to this project

### Technical Documentation
- [System Architecture](docs/architecture/system-architecture.md)
- [API Specification](docs/api-specs/api-specification.md)
- [Database Schema](docs/architecture/database-schema.md)
- [Authentication Guide](docs/architecture/authentication.md)
- [File Management](docs/architecture/file-management.md)

### User Documentation
- [Staff Dashboard Guide](docs/user-guides/staff-dashboard.md)
- [Student Submission Guide](docs/user-guides/student-submission.md)
- [Job Workflow Guide](docs/user-guides/job-workflow.md)

### Development
- [Development Setup](docs/development/setup.md)
- [Testing Guide](docs/development/testing.md)
- [Deployment Guide](docs/development/deployment.md) 