# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source files
COPY . .

# Build the application
RUN npm run build

# Runtime stage
FROM node:18-alpine

WORKDIR /app

# Create non-root user
RUN addgroup --system app && adduser --system --group app

# Copy built application
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
COPY --from=builder /app/public ./public

# Change ownership
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 3000

# Set environment
ENV NODE_ENV=production

# Start the application
CMD ["npm", "start"]
