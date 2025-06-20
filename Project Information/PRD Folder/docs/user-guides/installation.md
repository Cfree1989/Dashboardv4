# Installation Guide

This guide provides comprehensive instructions for setting up the 3D Print Dashboard system.

## System Architecture Overview

The 3D Print Dashboard consists of several components:

1. **Backend API**: A Flask-based RESTful API that handles business logic
2. **Frontend Dashboard**: A Next.js application that provides the user interface
3. **Database**: PostgreSQL database for storing job and event data
4. **Background Worker**: RQ worker for handling asynchronous tasks
5. **Redis**: Message broker for the background worker queue
6. **Shared Storage**: Network-mounted storage for job files
7. **SlicerOpener**: Custom protocol handler on staff computers

## Prerequisites

### Hardware Requirements

- One server/computer to host the application stack
- At least 4GB RAM, 2 CPU cores
- Minimum 100GB storage for the application and database
- Separate network storage volume for job files (recommended 1TB+)

### Software Requirements

- Docker and Docker Compose
- Windows, macOS, or Linux OS on host
- Network file sharing capability (SMB/CIFS recommended)
- Internet connectivity for email sending
- Web browser on client computers

### Network Requirements

- Internal network connectivity between all components
- Port 80/443 open on the host for web access
- File sharing ports open between the host and client computers
- SMTP port access (typically 587 or 25) for email functionality

## Deployment Steps

### 1. Prepare the Host Machine

1. Install Docker and Docker Compose
   ```bash
   # Ubuntu example
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo systemctl enable docker
   sudo systemctl start docker
   sudo usermod -aG docker $USER
   ```

2. Create the project directory structure
   ```bash
   mkdir -p /opt/3d-print-system
   cd /opt/3d-print-system
   ```

3. Clone the repository (if using version control)
   ```bash
   git clone [repository-url] .
   ```

### 2. Configure Network Storage

1. Create the storage directory structure
   ```bash
   mkdir -p /mnt/3dprint_storage
   mkdir -p /mnt/3dprint_storage/{Uploaded,Pending,ReadyToPrint,Printing,Completed,PaidPickedUp,Archived}
   ```

2. Mount the network storage (example for Ubuntu with NFS)
   ```bash
   # Add to /etc/fstab for persistence
   echo "192.168.1.100:/path/to/storage /mnt/3dprint_storage nfs defaults 0 0" | sudo tee -a /etc/fstab
   sudo mount -a
   ```

3. Set appropriate permissions
   ```bash
   sudo chown -R nobody:nogroup /mnt/3dprint_storage
   sudo chmod -R 775 /mnt/3dprint_storage
   ```

### 3. Configure Environment Variables

Create the backend `.env` file:

```bash
cd /opt/3d-print-system
cp .env.example .env
```

Edit the `.env` file with your specific configuration:

```
# Database Configuration
DATABASE_URL=postgresql://user:password@db:5432/3dprint_dashboard
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=3dprint_dashboard

# Storage Paths
STORAGE_BASE_PATH=/mnt/3dprint_storage

# Email Configuration
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=3d-print-system@example.com

# Authentication
SECRET_KEY=generate-a-secure-random-key
JWT_SECRET_KEY=generate-a-different-secure-random-key
JWT_ACCESS_TOKEN_EXPIRES=43200  # 12 hours in seconds

# Application Settings
FLASK_APP=run.py
FLASK_ENV=production
```

### 4. Configure Docker Compose

Create or edit the `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    depends_on:
      - db
      - redis
    volumes:
      - /mnt/3dprint_storage:/mnt/3dprint_storage
      - ./backend:/app
    env_file:
      - .env
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:3000"
    depends_on:
      - backend
    env_file:
      - .env
    restart: unless-stopped

  db:
    image: postgres:14-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    restart: unless-stopped

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: python -m rq.cli run
    depends_on:
      - db
      - redis
    volumes:
      - /mnt/3dprint_storage:/mnt/3dprint_storage
      - ./backend:/app
    env_file:
      - .env
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:
```

### 5. First-time Setup and Database Migration

1. Build the Docker images
   ```bash
   cd /opt/3d-print-system
   docker-compose build
   ```

2. Start the database container
   ```bash
   docker-compose up -d db
   ```

3. Run database migrations
   ```bash
   docker-compose run --rm backend flask db upgrade
   ```

4. Start all services
   ```bash
   docker-compose up -d
   ```

### 6. Initial Configuration

1. Add workstation credentials
   ```bash
   docker-compose exec backend flask add-workstation --name "Front-Desk" --password "secure-password"
   docker-compose exec backend flask add-workstation --name "Lab-Station" --password "different-secure-password"
   ```

2. Add initial staff members
   ```bash
   docker-compose exec backend flask add-staff --name "Jane Doe"
   docker-compose exec backend flask add-staff --name "John Smith"
   ```

### 7. Client Computer Setup

For each staff computer that needs access to the dashboard:

1. Mount the shared storage at the exact same path as on the server
   - Windows example: Map network drive Z: to `\\server-ip\3dprint_storage`
   - macOS example: Connect to Server `smb://server-ip/3dprint_storage`

2. Install the SlicerOpener protocol handler
   - Follow instructions in `docs/user-guides/slicer-opener.md`
   - Ensure the `AUTHORITATIVE_STORAGE_BASE_PATH` in the config.ini matches the exact mount path

3. Install slicer software
   - Install appropriate 3D printing slicer applications
   - Configure SlicerOpener to recognize the installed software

### 8. Testing the Setup

1. Access the Dashboard
   - Open a web browser and navigate to `http://server-ip`
   - Log in with one of the workstation credentials

2. Test File Submission
   - Submit a test job through the submission form
   - Verify the file appears in the `/mnt/3dprint_storage/Uploaded` directory

3. Test Protocol Handler
   - Click "Open in Slicer" on a job card
   - Verify the file opens in the configured slicer software

4. Test Email Functionality
   - Approve a test job and verify the approval email is sent

## Backup and Recovery

### Database Backup

Set up a cron job for regular backups:

```bash
# Add to crontab
echo "0 3 * * * docker-compose exec -T db pg_dump -U user 3dprint_dashboard | gzip > /backup/db_backup_\$(date +\%Y\%m\%d).sql.gz" | sudo tee -a /etc/crontab
```

### File Storage Backup

Set up regular file storage backups:

```bash
# Add to crontab
echo "0 4 * * * rsync -avz /mnt/3dprint_storage/ /backup/file_storage/" | sudo tee -a /etc/crontab
```

## System Health Monitoring

### Setting Up Basic Monitoring

1. Create a simple health check script
   ```bash
   cat > /opt/3d-print-system/health_check.sh << 'EOL'
   #!/bin/bash
   curl -s http://localhost/api/health | grep -q '"status":"ok"'
   if [ $? -eq 0 ]; then
       echo "System healthy"
       exit 0
   else
       echo "System unhealthy"
       exit 1
   fi
   EOL
   chmod +x /opt/3d-print-system/health_check.sh
   ```

2. Add to crontab for notifications
   ```bash
   echo "*/15 * * * * /opt/3d-print-system/health_check.sh || mail -s 'ALERT: 3D Print System Unhealthy' admin@example.com" | sudo tee -a /etc/crontab
   ```

## Troubleshooting

### Common Issues

#### Container Startup Failures

Check container logs:
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs worker
```

#### Database Connection Issues

Verify database is running and credentials are correct:
```bash
docker-compose exec db psql -U user -d 3dprint_dashboard -c "SELECT 1;"
```

#### Storage Access Problems

Check mounting and permissions:
```bash
ls -la /mnt/3dprint_storage/
docker-compose exec backend ls -la /mnt/3dprint_storage/
```

#### Email Sending Failures

Test email configuration:
```bash
docker-compose exec backend flask test-mail --recipient test@example.com
```

## Upgrading the System

### Standard Update Procedure

1. Pull latest code (if using version control)
   ```bash
   cd /opt/3d-print-system
   git pull
   ```

2. Rebuild containers
   ```bash
   docker-compose build
   ```

3. Run database migrations (if needed)
   ```bash
   docker-compose run --rm backend flask db upgrade
   ```

4. Restart services
   ```bash
   docker-compose down
   docker-compose up -d
   ```

5. Verify system health
   ```bash
   ./health_check.sh
   ```

## Security Recommendations

1. **Use HTTPS**: Configure a reverse proxy (nginx, traefik) with SSL/TLS
2. **Secure Passwords**: Use strong passwords for workstations, database, and email
3. **Firewall Rules**: Restrict access to the application server to only lab networks
4. **Regular Updates**: Keep all components updated with security patches
5. **Access Logging**: Enable access logs for security monitoring

## Appendix: System Architecture Diagram

```
┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │
│  Staff Computer │      │  Staff Computer │
│  with Browser   │      │  with Browser   │
│  & SlicerOpener │      │  & SlicerOpener │
│                 │      │                 │
└────────┬────────┘      └────────┬────────┘
         │                        │
         │                        │
         │                        │
         ▼                        ▼
┌─────────────────────────────────────────┐
│                                         │
│            Local Network                │
│                                         │
└───────────────────┬─────────────────────┘
                    │
                    │
                    ▼
┌───────────────────────────────────────────────────────┐
│ Docker Compose Stack                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌────────────┐ │
│  │             │    │             │    │            │ │
│  │   Backend   │◄───┤  Frontend   │◄───┤  Browser   │ │
│  │   (Flask)   │    │  (Next.js)  │    │  Client    │ │
│  │             │    │             │    │            │ │
│  └──────┬──────┘    └─────────────┘    └────────────┘ │
│         │                                             │
│         │                                             │
│  ┌──────▼──────┐    ┌─────────────┐    ┌────────────┐ │
│  │             │    │             │    │            │ │
│  │ PostgreSQL  │    │    Redis    │◄───┤   Worker   │ │
│  │  Database   │    │             │    │            │ │
│  │             │    │             │    │            │ │
│  └─────────────┘    └─────────────┘    └────────────┘ │
└───────────────────────────────────────────────────────┘
                    │
                    │
                    ▼
┌───────────────────────────────────────┐
│                                       │
│  Network Attached Storage             │
│  /mnt/3dprint_storage/                │
│   ├── Uploaded/                       │
│   ├── Pending/                        │
│   ├── ReadyToPrint/                   │
│   ├── Printing/                       │
│   ├── Completed/                      │
│   ├── PaidPickedUp/                   │
│   └── Archived/                       │
│                                       │
└───────────────────────────────────────┘
``` 