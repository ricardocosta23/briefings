# PDF File Sharing Application

## Overview

This is a serverless web application built with Python Flask that allows users to upload, share, and manage PDF files. The application provides a simple interface for uploading PDFs and generates shareable links for file access. Optimized for Vercel deployment with no external dependencies.

## System Architecture

### Application Architecture
- **Framework**: Python Flask (serverless-ready)
- **Frontend**: Pure HTML/CSS/JavaScript with Tailwind CSS CDN
- **File Upload**: Flask file handling with Werkzeug
- **Database**: SQLite with base64 file storage
- **Deployment**: Vercel Python runtime
- **Storage**: In-memory SQLite perfect for serverless functions

## Key Components

### Database Schema
- **Users Table**: User authentication and management
  - id (serial primary key)
  - username (unique text)
  - password (text)
  
- **Uploaded Files Table**: File metadata and management
  - id (serial primary key)
  - originalName (text)
  - fileName (text)
  - filePath (text)
  - fileSize (integer)
  - mimeType (text)
  - uploadTime (timestamp)

### File Storage
- **Database Storage**: Files stored as base64-encoded data in PostgreSQL
- **File Naming**: Timestamp-prefixed sanitized filenames for unique identification
- **File Validation**: PDF files only, 10MB size limit
- **Permanent Storage**: Files persist permanently in database, perfect for Vercel deployment

### API Endpoints
- `GET /api/files` - Retrieve all uploaded files
- `POST /api/files/upload` - Upload new PDF files
- `GET /api/files/:id` - Get specific file metadata
- `DELETE /api/files/:id` - Delete uploaded files

### Storage Layer
- **Interface**: IStorage for database operations abstraction
- **Implementation**: MemStorage for in-memory development storage
- **Future**: Database-backed storage implementation ready

## Data Flow

1. **File Upload Process**:
   - User selects PDF file through drag-and-drop or file picker
   - Client validates file type and size
   - File is sent to server via multipart form data
   - Server validates file and saves to `/Briefings` directory
   - File metadata is stored in database
   - Client receives confirmation and file metadata

2. **File Management**:
   - Client queries server for file list
   - Server retrieves file metadata from storage
   - Client displays files with actions (view, copy link, delete)
   - File operations update both filesystem and database

3. **Error Handling**:
   - Client-side validation prevents invalid uploads
   - Server-side validation provides backup security
   - Toast notifications inform users of operation results

## External Dependencies

### Core Dependencies
- **@neondatabase/serverless**: PostgreSQL database connectivity
- **drizzle-orm**: Type-safe database operations
- **multer**: File upload handling
- **express**: Web server framework
- **@tanstack/react-query**: Server state management

### UI Dependencies
- **@radix-ui/***: Accessible UI primitive components
- **tailwindcss**: Utility-first CSS framework
- **lucide-react**: Icon library
- **react-hook-form**: Form state management
- **wouter**: Lightweight routing

### Development Dependencies
- **vite**: Build tool and development server
- **tsx**: TypeScript execution
- **drizzle-kit**: Database schema management

## Deployment Strategy

### Build Process
1. **Frontend Build**: Vite builds React application to `/dist/public`
2. **Backend Build**: esbuild bundles Express server to `/dist/index.js`
3. **Database Migration**: Drizzle Kit handles schema migrations

### Environment Configuration
- **DATABASE_URL**: PostgreSQL connection string (required)
- **NODE_ENV**: Environment mode (development/production)
- **PORT**: Server port (defaults to appropriate port)

### Production Deployment
- Static files served from `/dist/public`
- Express server runs from `/dist/index.js`
- Database migrations applied via `npm run db:push`

## Deployment Configuration

### Vercel Deployment Files
- **vercel.json**: Vercel deployment configuration with proper routing and build settings
- **README.md**: Comprehensive deployment guide with production considerations
- **.env.example**: Environment variables template for production deployment

### Important Production Notes
- **Database Storage**: Files are now stored permanently in the database as base64 data
- **Vercel Compatible**: No file system dependencies, works perfectly with serverless
- **Automatic Persistence**: Files are backed up with your database, no additional storage needed

### Deployment Process
1. Build frontend with `vite build`
2. Deploy with `vercel --prod`
3. Configure environment variables in Vercel dashboard
4. Consider cloud storage for production file persistence

## Changelog

```
Changelog:
- July 07, 2025. Initial setup with React/Node.js
- July 07, 2025. Added Vercel deployment configuration 
- July 07, 2025. Updated storage system to use database storage (base64)
- July 07, 2025. Recreated application in Python Flask for better Vercel serverless compatibility
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```