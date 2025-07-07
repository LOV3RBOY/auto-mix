# Dockerfile for services/frontend-react/

# --- Stage 1: Build ---
# Use a Node.js image to build the React application
FROM node:18-alpine AS build

WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker cache
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application source code
COPY . .

# Build the static files for production
RUN npm run build

# --- Stage 2: Production ---
# Use a lightweight Nginx image to serve the static content
FROM nginx:stable-alpine

# Copy the built static files from the build stage to the Nginx server directory
COPY --from=build /app/build /usr/share/nginx/html

# Optional: Copy a custom Nginx configuration if needed
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 for the Nginx server
EXPOSE 80

# The default Nginx command starts the server.
# We make it explicit here for clarity.
CMD ["nginx", "-g", "daemon off;"]