# Recipme

A full-stack recipe management application with user authentication, recipe search, and external food data integration.

## Tech Stack

**Backend:**
- Django 5.2.8 + Django REST Framework
- PostgreSQL 16 (database)
- Redis 7 (caching)
- JWT authentication (httpOnly cookies)
- USDA FoodData Central API integration

**Frontend:**
- Next.js 16 + React 19
- TypeScript
- Tailwind CSS + Radix UI
- Server-side rendering

**Infrastructure:**
- Docker Compose orchestration
- MailPit (email testing)
- PgAdmin (database management)

## Django Apps

### auth_api
Handles user authentication and account management:
- Registration, login, logout
- JWT token management with httpOnly cookies
- Password reset via email
- Token refresh mechanism
- Custom cookie-based authentication class

### recipes
Core recipe management system:
- CRUD operations for recipes
- Search and filter by tags
- Like/favorite functionality
- Pagination (20 items per page)
- Permission-based access control
- Image and nutrition tracking

### api_management
External food data integration:
- USDA FoodData Central API client
- HTTP/2 with retry logic and exponential backoff
- Redis caching for API responses
- Ingredient search and nutrition extraction

### contact_api
User support/feedback system:
- Contact message submission
- Admin response capability
- Status tracking (pending/responded)

## Key Features

### Authentication
- Secure JWT tokens stored in httpOnly cookies (XSS protection)
- Automatic token refresh on expiration
- Email-based password reset
- Access tokens: 15-minute lifetime
- Refresh tokens: 7-day lifetime

### Recipe Management
- Users can create, edit, and delete their own recipes
- Search by title/description
- Filter by tags (AND/OR modes)
- Like and save recipes
- View other users' recipes (read-only)
- Admin full access via Django admin panel

### Django Admin Panel
Access at `http://localhost:8000/admin` with superuser credentials.

**Features:**
- User management (view all users, set permissions)
- Recipe moderation (edit/delete any recipe)
- Contact message management (view submissions, mark as responded)
- Tag and ingredient management
- Full CRUD for all models

**Superuser Creation:**
- Auto-created on startup from env vars (`DJANGO_SUPERUSER_*`)
- Command: `python manage.py create_superuser_if_missing`

## Testing

Backend tests cover:
- Recipe CRUD operations and permissions
- Search/filter functionality
- API authentication flows
- USDA API integration with caching
- HTTP/2 client retry logic
- Concurrent request handling

Run tests:
```bash
docker compose exec backend python manage.py test
```

## Demo Data

Populate demo recipes and users:
```bash
docker compose exec backend python manage.py populate_demo_data
```

Creates:
- 4 demo users (demo@example.com, chef@example.com, foodie@example.com, admin@example.com)
- Multiple recipes with tags, ingredients, and nutrition data
- Sample likes and saves
- Password for all users: `demo123`

Use `--clear` flag to reset demo data before populating.

## Quick Start

1. Copy `.env.template` to `.env` and configure
2. Start services:
   ```bash
   docker compose up -d
   ```
3. Access:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Django Admin: http://localhost:8000/admin
   - MailPit: http://localhost:8025
   - PgAdmin: http://localhost:5050

## Project Structure

```
Recipme/
├── backend/src/
│   ├── auth_api/          # Authentication
│   ├── recipes/           # Recipe management
│   ├── api_management/    # External API integration
│   └── contact_api/       # Contact messages
├── frontend/src/
│   ├── app/               # Next.js pages
│   ├── components/        # Reusable UI components
│   ├── hooks/             # Custom React hooks (useAuth)
│   ├── lib/               # API clients
│   └── types/             # TypeScript interfaces
└── docker-compose.yml     # Service orchestration
```

## Architecture Highlights

- **httpOnly Cookies:** JWT tokens stored securely, not accessible to JavaScript
- **Automatic Token Refresh:** Transparent handling of expired tokens
- **Permission-Based Access:** Users can only modify their own content
- **Redis Caching:** API responses cached for 1-24 hours based on data type
- **Pagination:** 20 items per page across all list endpoints
- **N+1 Prevention:** Optimized queries with Django ORM prefetching
- **HTTP/2 + Retry Logic:** Resilient external API calls with exponential backoff
