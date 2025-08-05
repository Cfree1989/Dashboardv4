# Next.js Frontend Dockerfile for 3D Print Management System
# Development-focused build

FROM node:18-alpine

# Install system dependencies
RUN apk add --no-cache libc6-compat curl

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Create next user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Change ownership of the app directory
RUN chown -R nextjs:nodejs /app

# Switch to nextjs user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start development server
CMD ["npm", "run", "dev"]