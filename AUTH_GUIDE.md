# JWT Authentication System Guide

This project uses JWT (JSON Web Token) authentication with Django REST Framework on the backend and TypeScript on the frontend.

## Architecture Overview

- **Backend**: Django REST Framework + Simple JWT
- **Frontend**: Next.js with TypeScript
- **Token Storage**: httpOnly cookies (secure, XSS-proof)
- **Token Lifetime**: Access tokens expire in 15 minutes, refresh tokens in 7 days

## API Endpoints

### Base URL
```
http://localhost:8000/api/auth/
```

### 1. Register User
**POST** `/register`

Request:
```json
{
  "username": "testuser",
  "password": "strongpassword123",
  "password2": "strongpassword123",
  "email": "user@example.com"
}
```

Response (201):
```json
{
  "message": "User created successfully"
}
```

### 2. Login
**POST** `/login`

Request:
```json
{
  "username": "testuser",
  "password": "strongpassword123"
}
```

Response (200):
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "user@example.com"
  }
}
```

**Note**: Access and refresh tokens are set as httpOnly cookies automatically.

### 3. Get Current User
**GET** `/me`

**Note**: Cookies are sent automatically with the request.

Response (200):
```json
{
  "id": 1,
  "username": "testuser",
  "email": "user@example.com"
}
```

### 4. Refresh Token
**POST** `/refresh`

**Note**: Refresh token is read from cookies automatically.

Response (200):
```json
{
  "message": "Token refreshed successfully"
}
```

**Note**: New access token cookie is set automatically.

### 5. Logout
**POST** `/logout`

**Note**: Both access and refresh tokens are read from cookies automatically.

Response (205):
```json
{
  "message": "Logged out successfully"
}
```

**Note**: Cookies are cleared automatically by the server.

## Frontend Usage

### Import the Auth Service

```typescript
import { authAPI } from '@/lib/auth';
```

### Register a New User

```typescript
try {
  const response = await authAPI.register({
    username: 'newuser',
    password: 'password123',
    password2: 'password123',
    email: 'user@example.com'
  });
  console.log(response.message); // "User created successfully"
} catch (error) {
  console.error('Registration failed:', error);
}
```

### Login

```typescript
try {
  const response = await authAPI.login({
    username: 'testuser',
    password: 'password123'
  });
  console.log('Logged in:', response.user);
  // Tokens are automatically stored in httpOnly cookies by the server
} catch (error) {
  console.error('Login failed:', error);
}
```

### Get Current User

```typescript
try {
  const user = await authAPI.getMe();
  console.log('Current user:', user);
} catch (error) {
  console.error('Failed to get user:', error);
}
```

### Logout

```typescript
await authAPI.logout();
// Cookies are automatically cleared by the server
```

### Check Authentication Status

```typescript
const isLoggedIn = await authAPI.isAuthenticated();
if (isLoggedIn) {
  console.log('User is logged in');
} else {
  console.log('User is not logged in');
}
```

## Features

### 1. Automatic Token Refresh
The frontend API client automatically refreshes expired access tokens when it receives a 401 response. This happens transparently without user intervention.

### 2. Token Blacklisting
When a user logs out, their refresh token is added to a blacklist in the database, preventing it from being used again even if it hasn't expired.

### 3. Secure Token Storage (httpOnly Cookies)
Tokens are stored in **httpOnly cookies**, which provides maximum security:
- ✅ **XSS Protection**: JavaScript cannot access the cookies
- ✅ **CSRF Protection**: SameSite=Lax prevents cross-site attacks
- ✅ **Automatic**: Cookies are sent with every request, no manual handling needed
- ✅ **Production Ready**: Secure flag enabled in production (HTTPS only)

### 4. CORS Configuration
The backend is configured to accept requests from `localhost:3000` with credentials.

## Testing with cURL

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123456","password2":"demo123456","email":"demo@example.com"}'

# Login (saves cookies to file)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123456"}' \
  -c cookies.txt

# Get user info (uses cookies from file)
curl http://localhost:8000/api/auth/me \
  -b cookies.txt

# Refresh token (cookies sent automatically)
curl -X POST http://localhost:8000/api/auth/refresh \
  -b cookies.txt \
  -c cookies.txt

# Logout (cookies sent automatically and cleared)
curl -X POST http://localhost:8000/api/auth/logout \
  -b cookies.txt
```

## Database Tables

The token blacklist feature creates these tables:
- `token_blacklist_outstandingtoken` - Stores all issued refresh tokens
- `token_blacklist_blacklistedtoken` - Stores blacklisted tokens

## Security Notes

1. **Change SECRET_KEY in production** - The current Django secret key is for development only
2. **Use HTTPS in production** - JWT tokens should only be transmitted over HTTPS (secure flag enforced automatically)
3. **httpOnly cookies enabled** - Maximum security against XSS attacks
4. **SameSite=Lax** - Protection against CSRF attacks
5. **Password validation** - Django's built-in validators are enabled (min length, common passwords, etc.)

## Dependencies Added

Backend (`requirements.txt`):
- `djangorestframework==3.15.2`
- `djangorestframework-simplejwt==5.3.1`

No additional frontend dependencies were needed (using native fetch API).

## Next Steps for Team Members

When creating the login/register UI pages:
1. Import the auth functions from `@/lib/auth`
2. Import types from `@/types/auth`
3. Use the pre-built API functions instead of writing fetch calls
4. Handle errors with try/catch blocks
5. Redirect users after successful login/logout

Example component structure:
```typescript
'use client';
import { useState } from 'react';
import { authAPI } from '@/lib/auth';
import type { LoginRequest } from '@/types/auth';

export default function LoginForm() {
  const [formData, setFormData] = useState<LoginRequest>({
    username: '',
    password: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await authAPI.login(formData);
      // Redirect to dashboard or home
      window.location.href = '/dashboard';
    } catch (error) {
      alert('Login failed: ' + error);
    }
  };

  return (
    // Your form JSX here
  );
}
```

