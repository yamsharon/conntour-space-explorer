# Submission README
## Conntour Space Explorer - Implementation Decisions & Future Improvements

This document outlines the key architectural and implementation decisions made during the development of the Conntour Space Explorer project, along with areas identified for future improvement.

---

## Backend Implementation Decisions

### 1. Clean Architecture Pattern

**Decision:** Implemented a 3-layer clean architecture for the backend:
- **API Layer** (`api/`): Controllers handle HTTP requests/responses
- **Domain Layer** (`domain/`): Business logic and models
- **Infrastructure Layer** (`infra/`): Data access and external services

**Rationale:**
- Separation of concerns makes the codebase maintainable and testable
- Easy to swap implementations (e.g., replace in-memory DB with PostgreSQL)


### 2. Dependency Injection

**Decision:** Used FastAPI's `Depends()` with `@lru_cache()` for singleton management.

**Rationale:**
- Ensures expensive resources (CLIP model, database) are initialized once
- Improves testability by allowing easy mocking
- Follows FastAPI best practices
- Prevents multiple instances of heavy objects

### 3. Semantic Search with CLIP

**Decision:** Implemented real semantic search using OpenAI's CLIP model.

**Rationale:**
- CLIP is specifically designed for image-text matching, making it ideal for this use case

**Implementation Details:**
- Uses `openai/clip-vit-base-patch32` model
- Generates embeddings for both images and text queries
- Calculates cosine similarity between embeddings
- Normalizes confidence scores to [0.2, 1.0] range for better UX

**Possible Improvements**
- Test more models or train model for a specific field of data (e.g. space images)
- Combine several models - may cause slower performance


### 4. Embedding Caching Strategy

**Decision:** Cache image embeddings to disk (`embeddings_cache.pkl`) to avoid regenerating them on every startup.

**Rationale:**
- Generating embeddings for all images takes significant time (minutes)
- Embeddings don't change unless the source data changes
- Dramatically improves startup time after first run

**Implementation:**
- Cache stored as pickle file with embeddings dictionary
- Cache invalidated if `mock_data.json` is modified

**Trade-offs:**
- Cache file can be large (depends on number of images)
- Requires disk I/O on startup
- **Verdict:** Essential for good developer experience


### 5. Comprehensive Logging

**Decision:** Implemented structured logging with file rotation.

**Rationale:**
- Essential for debugging in production
- Logs include filename, line number, and function name
- File rotation prevents disk space issues
- Configurable log levels via environment variables

**Implementation:**
- Rotating file handler (5MB max, 3 backups)
- Console and file output
- Configurable via `LOG_LEVEL` and `LOG_FILE` env vars

---

## Frontend Implementation Decisions

### 1. Frontend Architecture & Organization

**Decision:** Implemented a feature-based architecture with clear separation of concerns:
- **API Layer** (`api/`): Domain-specific API clients with shared utilities 
- **Components** (`components/`): Reusable UI components 
- **Pages** (`pages/`): Route-level page components
- **Utils** (`utils/`): Shared utility functions

**Rationale:**
- Clear separation between API communication, UI components, and page-level logic

### 2. React Query for State Management

**Decision:** Used TanStack React Query for server state management.

**Rationale:**
- React Query is purpose-built for server state
- Automatic caching, background refetching, and error handling
- Built-in loading and error states
- Automatic request deduplication


### 3. URL Search Queries

**Decision:** Store search queries in URL parameters for shareability and browser history.

**Rationale:**
- Users can bookmark search results
- Browser back/forward buttons work correctly
- Shareable URLs
- State persists across page refreshes

**Trade-offs:**
- More complex state synchronization
- **Verdict:** Better UX is worth the complexity

### 4. NPM Vulnerabilities

**Decision:** Focused on fixing 1 critical.

---

## Feature Implementation Decisions

### 1. History Pagination

**Decision:** Implemented server-side pagination (10 items per page).

**Rationale:**
- Server-side pagination is more efficient for large datasets
- Reduces initial load time
- Better user experience for large histories

**Implementation:**
- Backend: `GET /api/history?startIndex=0&limit=10`
- Frontend: React Query with page-based query keys
- Pagination controls with Previous/Next buttons

### 2. History Results Retrieval & Skip History Flag

**Decision:** When a user clicks a history item, the backend retrieves the stored search results without performing a new search, and uses the `skipHistory` flag to prevent duplicate history entries.

**Rationale:**
- When navigating from history page, we don't want to create a new history entry
- No new calculation - faster than re-running the search
- Ensures users see the exact same results they saw originally, even if the dataset or search algorithm changes

---
