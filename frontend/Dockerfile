# Use a Node.js image to build the React app
FROM node:16-alpine AS build

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the app files and build the app
COPY . .
RUN npm run build

# Use an Nginx server to serve the built files
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80 for the app
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
