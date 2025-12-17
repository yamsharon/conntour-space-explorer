# Conntour Space Explorer - Frontend

## Overview

A modern React application for browsing and searching NASA space images. The frontend provides an intuitive interface for exploring space imagery with semantic search capabilities, featuring a clean, responsive design built with React, TypeScript, and Tailwind CSS.

## Prerequisites

- **Node.js 14+**
- **npm** or **yarn**
- Backend API running on `http://localhost:5000` (see backend README)

## Setup Instructions

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

   The application will open in your browser at `http://localhost:3000`

   The page will reload automatically when you make changes.

## Project Structure

```
frontend/
├── public/              # Static assets
│   ├── index.html      # HTML template
│   └── ...
├── src/
│   ├── api/            # API client layer
│   ├── components/     # Reusable React components
│   ├── pages/          # Page components (routes)
│   ├── utils/          # Utility functions
│   ├── App.tsx         # Main app component with routing
│   ├── index.tsx       # Application entry point
│   └── index.css       # Global styles
├── package.json        # Dependencies and scripts
├── tsconfig.json       # TypeScript configuration
└── tailwind.config.js  # Tailwind CSS configuration
```

## Architecture

### API Client Layer (`src/api/client.ts`)

Centralized API client that provides:
- Typed interfaces for API responses (`ImageSource`, `SearchResult`)
- Normalized error handling
- Axios instance configuration
- API functions: `getImages()`, `searchImages()`

### Component Architecture

- **Layout Component**: Provides global header, navigation, and sticky positioning
- **Page Components**: Route-specific components (Browse, Search, History)
- **Reusable Components**: `SourceCard` for displaying image cards with confidence badges


## Key Features

### Browse Page
- Displays all NASA images in a responsive grid
- Image cards show title, description, launch date, and full image link
- Loading and error states

### Search Page
- Natural language search interface
- Centered search bar with AI-style design
- Results displayed with confidence scores (color-coded: green >75%, orange 50-75%, red <50%)
- Loading spinners and error messages
- Empty state handling

### Global Navigation
- Sticky header with title and navigation bar
- Active route highlighting
- Smooth navigation between pages

## Configuration

### API Proxy

The frontend is configured to proxy API requests to the backend:
- Development: `http://localhost:5000` (configured in `package.json`)
- Production: Update API base URL in `src/api/client.ts` if needed
