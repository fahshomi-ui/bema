FROM node:22-alpine

WORKDIR /app

# Copy only the server directory
COPY server/ ./

# Install dependencies
RUN npm install --production

# Expose port
EXPOSE 3001

# Start the server
CMD ["node", "index.js"]
