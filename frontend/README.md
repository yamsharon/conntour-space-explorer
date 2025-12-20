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
- Typed interfaces for API responses (`ImageSource`, `SearchResult`, `SearchResultHistoryResponse`, `HistoryResponse`)
- API functions:
  - `getImages()` - Fetch all NASA image sources
  - `searchImages(query, skipHistory)` - Perform semantic search
  - `getHistory(startIndex, limit)` - Get paginated search history
  - `getHistoryResults(historyId)` - Get full results for a specific history item
  - `deleteHistoryItem(id)` - Delete a history item
- Normalized error handling
- Axios instance configuration

### Component Architecture

- **Layout Component**: Provides global header, navigation, and sticky positioning
- **Page Components**: Route-specific components (Browse, Search, History)
- **Reusable Components**: Components for app-wide use


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
- Automatic history saving when results are loaded (unless `skipHistory=true` is in URL)
- URL query parameter support:
  - `/search?q=query` - Standard search (saves to history)
  - `/search?q=query&skipHistory=true` - Search without saving to history (used when navigating from history page)
  - `/search?q=query&historyId=<id>&skipHistory=true` - Display pre-calculated results from history (fetches results via API call to `/api/history/{id}/results`)
- When `historyId` is present, the page fetches the original search results from the backend instead of performing a new search

### History Page
- Server-side pagination (10 items per page)
- Fetches only the current page's data from the API
- Each history item shows:
  - Search query and timestamp
  - Top 3 result thumbnails with rounded corners (positioned on the right)
  - Delete button for individual items (far right)
- Clicking a history item navigates to search page with:
  - The original query: `q=<query>`
  - The history ID: `historyId=<id>`
  - Skip history flag: `skipHistory=true`
  - The SearchPage then fetches the pre-calculated results via API call to `/api/history/{id}/results`
  - This prevents creating duplicate history entries and shows the exact original results
- Pagination controls (Previous/Next buttons)
- Loading and error states
- Empty state when no history exists

### Global Navigation
- Sticky header with title and navigation bar
- Active route highlighting
- Smooth navigation between pages

### API Proxy

The frontend is configured to proxy API requests to the backend:
- Development: `http://localhost:5000` (configured in `package.json`)
- Production: Update API base URL in `src/api/client.ts` if needed
