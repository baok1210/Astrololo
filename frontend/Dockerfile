FROM node:20-alpine

WORKDIR /app

# Install dependencies for building
RUN apk add --no-cache git

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY frontend/ ./

# Build the application
RUN npm run build

# Install serve for production (optional)
RUN npm install -g serve

# Expose port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:5173/ || exit 1

# Serve the application
CMD ["serve", "-s", "dist", "-l", "5173", "--single"]
