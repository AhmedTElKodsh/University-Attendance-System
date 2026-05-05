# Multi-stage build for React frontend
# Stage 1: Build
FROM node:18-alpine as build

WORKDIR /app

# Build argument for API URL
ARG REACT_APP_API_URL=""

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Set environment variable for build
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

# Build the React app
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy built files from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]