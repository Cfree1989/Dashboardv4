# Dashboard v4 Codebase Visualization

```mermaid
graph TB
    %% Entry Point
    A[🚀 Next.js Application - Project Information/v0/] --> B[⚙️ App Router - Modern React Framework]
    
    %% Core Application Structure
    B --> C[🏛️ Dashboard v4 Application Instance]
    
    subgraph "Configuration Layer"
        C --> D[📋 Configuration Management]
        D --> D1[🔧 next.config.mjs - Next.js Settings]
        D --> D2[🌍 Environment Variables - .env files]
        D --> D3[📁 TypeScript Configuration - tsconfig.json]
        D --> D4[🎨 Tailwind Config - tailwind.config.ts]
        D --> D5[🔗 Component Library - components.json]
    end
    
    subgraph "React Ecosystem"
        C --> E[🔌 Framework Integration]
        E --> E1[⚛️ React Components - components/]
        E1 --> E2[🎯 TypeScript Types - types/]
        E1 --> E3[🪝 Custom Hooks - hooks/]
        E1 --> E4[🛠️ Utilities - lib/]
    end
    
    subgraph "TypeScript Types Layer"
        C --> F[📊 Type Definitions]
        F --> F1[💼 types/job.ts - Core Job Interface]
        F --> F2[📝 Component Prop Types]
        F1 --> F3[🎯 Job Interface - String ID]
        F2 --> F4[📋 Component Props - React Types]
        F3 -.->|Used in Components| F4
        
        F3 --> F31[👤 Student Information Fields]
        F3 --> F32[📄 File Metadata Fields]
        F3 --> F33[🔄 Status Workflow Fields]
        F3 --> F34[🖨️ Printer Configuration Fields]
        F3 --> F35[💰 Cost Calculation Fields]
        F3 --> F36[✅ Staff Review Fields]
    end
    
    subgraph "Route Handlers - Controllers"
        C --> G[🛣️ HTTP Route Management]
        G --> G1[📤 routes/main.py - Student Portal]
        G --> G2[📊 routes/dashboard.py - Staff Interface]
        
        G1 --> G11[📋 Student Submission Form]
        G1 --> G12[✅ Email Confirmation Handler]
        G1 --> G13[👀 Student Job Status View]
        
        G2 --> G21[📈 Staff Dashboard Overview]
        G2 --> G22[🔄 Job Status Update Actions]
        G2 --> G23[📁 File Management Operations]
        G2 --> G24[💰 Cost Calculation Interface]
        G2 --> G25[🏷️ Job Tagging and Notes]
    end
    
    subgraph "Business Logic Services"
        C --> H[⚡ Service Layer]
        H --> H1[📁 services/file_service.py - File Operations]
        
        H1 --> H11[📤 File Upload Processing]
        H1 --> H12[🔍 File Validation and Parsing]
        H1 --> H13[📏 Metadata Extraction STL/3MF]
        H1 --> H14[🖼️ Thumbnail Generation]
        H1 --> H15[📦 File Storage Management]
        H1 --> H16[🔄 File Movement Between Stages]
        H1 --> H17[🗑️ File Cleanup Operations]
    end
    
    subgraph "User Interface Templates"
        C --> I[🎨 Template System]
        I --> I1[🏗️ base/ - Layout Foundation]
        I --> I2[🔗 shared/ - Reusable Components]
        I --> I3[👨‍🎓 student/ - Student Interface]
        I --> I4[👩‍💼 staff/ - Staff Interface]
        
        I3 --> I31[📝 submission/ - File Upload Forms]
        I3 --> I32[📊 status/ - Job Tracking Views]
        
        I4 --> I41[📈 dashboard/ - Management Console]
        I4 --> I42[🔐 auth/ - Authentication Views]
        I4 --> I43[⚙️ settings/ - Configuration Interface]
    end
    
    subgraph "Static Assets"
        C --> J[📦 Static Resources]
        J --> J1[🎨 static/css/ - Tailwind Styles]
        J --> J2[🔊 static/sounds/ - Audio Notifications]
        J --> J3[🖼️ static/images/ - UI Graphics]
        J --> J4[📱 static/js/ - Frontend Scripts]
    end
    
    subgraph "File Storage Workflow System"
        C --> K[🗂️ Storage Management System]
        K --> K1[📤 storage/Uploaded/ - Initial Upload]
        K --> K2[⏳ storage/Pending/ - Awaiting Review]
        K --> K3[✅ storage/ReadyToPrint/ - Approved Jobs]
        K --> K4[🖨️ storage/Printing/ - In Progress]
        K --> K5[✔️ storage/Completed/ - Finished Jobs]
        K --> K6[💰 storage/PaidPickedUp/ - Final State]
        K --> K7[🖼️ storage/thumbnails/ - Preview Images]
        K --> K8[📋 metadata.json files - Job Details]
    end
    
    subgraph "Utility Functions"
        C --> U[🛠️ Utility Helpers]
        U --> U1[🎭 Template Filters Registry]
        U1 --> U2[🖨️ format_printer_name - Display Formatting]
        U1 --> U3[🎨 format_color_name - Material Colors]
        U1 --> U4[🏫 format_discipline_name - Academic Departments]
        U1 --> U5[🕐 format_local_datetime - Time Display]
        U1 --> U6[📅 detailed_local_datetime - Extended Time]
    end
    
    %% Data Flow Connections
    G11 -.->|File Upload Request| H11
    H11 -.->|Store Uploaded File| K1
    H11 -.->|Create Job Record| F3
    F3 -.->|Log Status Change| F4
    G22 -.->|Update Job Status| F3
    G23 -.->|Move Files Between Stages| H16
    H16 -.->|Update Storage Location| K2
    K2 -.->|Workflow Progression| K3
    K3 -.->|Workflow Progression| K4
    K4 -.->|Workflow Progression| K5
    K5 -.->|Workflow Progression| K6
    
    %% External Dependencies
    subgraph "External Systems"
        EXT1[🗄️ SQLite/PostgreSQL Database]
        EXT2[💾 Local File System Storage]
        EXT3[🎨 Tailwind CSS Framework]
        EXT4[📧 Email System SMTP]
        EXT5[🌐 Web Browser Clients]
    end
    
    EXT1 -.->|Database Operations| E2
    EXT2 -.->|File Operations| K
    EXT3 -.->|CSS Styling| J1
    EXT4 -.->|Email Notifications| G12
    EXT5 -.->|HTTP Requests| G
    
    %% Job Lifecycle Visualization
    subgraph "📋 Job Status Workflow Pipeline"
        S1[📤 UPLOADED - File Received] --> S2[⏳ PENDING - Awaiting Staff Review]
        S2 --> S3[✅ READY_TO_PRINT - Approved and Queued]
        S3 --> S4[🖨️ PRINTING - Currently Being Printed]
        S4 --> S5[✔️ COMPLETED - Print Finished]
        S5 --> S6[💰 PAID_PICKED_UP - Transaction Complete]
    end
    
    %% User Interface Access Patterns
    subgraph "👥 User Access Patterns"
        UI1[👨‍🎓 Student Users - Submit and Track]
        UI2[👩‍💼 Staff Users - Manage and Process]
        UI3[👔 Admin Users - System Configuration]
    end
    
    UI1 -.->|Access Student Interface| I3
    UI2 -.->|Access Staff Dashboard| I4
    UI3 -.->|System Administration| I4
    I3 -.->|Submit New Jobs| G11
    I4 -.->|Manage Job Pipeline| G22
    
    %% Styling for Visual Hierarchy
    style A fill:#ff6b6b,stroke:#d63031,stroke-width:3px
    style F3 fill:#74b9ff,stroke:#0984e3,stroke-width:2px
    style K fill:#55a3ff,stroke:#2d3436,stroke-width:2px
    style G fill:#fdcb6e,stroke:#e17055,stroke-width:2px
    style H fill:#a29bfe,stroke:#6c5ce7,stroke-width:2px
    style I fill:#fd79a8,stroke:#e84393,stroke-width:2px
    style U fill:#00b894,stroke:#00a085,stroke-width:2px
```

## Architecture Overview

### Core Components:

1. **Entry Point**: Next.js App Router bootstraps the React application
2. **Types**: Define TypeScript interfaces for Jobs and Component Props
3. **Components**: Handle UI rendering for dashboard and job management
4. **State Management**: React Context for global state and local component state
5. **Mock Data System**: UI prototypes with test data for development
6. **Testing Infrastructure**: Comprehensive testing with Jest and React Testing Library

### Key Features:

- **Component-Based Architecture**: Reusable React components with TypeScript
- **Mock UI Development**: v0.dev generated components for rapid prototyping
- **Testing Framework**: Unit, integration, and E2E testing infrastructure
- **Type Safety**: Full TypeScript coverage for development confidence
- **Documentation System**: Structured docs, diagrams, and semantic knowledge layer
- **AI Agent Optimization**: Clear structure and naming for AI code generation

### Current State:

1. **Frontend Only**: UI components and mockups without backend integration
2. **Testing Infrastructure**: Comprehensive test setup with working unit tests
3. **Documentation**: Complete project documentation and visual diagrams
4. **Type Definitions**: Full TypeScript interfaces for future backend integration
5. **Development Tools**: Scripts, CI/CD setup, and development workflow 