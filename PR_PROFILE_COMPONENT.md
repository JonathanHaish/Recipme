# Profile Component - Pull Request

## Overview
This PR adds a comprehensive user profile management system that allows users to manage their profile information, goals, and dietary preferences. The system includes dynamic goals and diet types that can be managed by administrators through Django admin.

## Features Implemented

### User Profile Management
- ✅ Profile image upload with preview
- ✅ Circular grey avatar with user's initial as fallback
- ✅ Dynamic goals selection (multiple checkboxes)
- ✅ Dynamic diet type selection (dropdown)
- ✅ Profile description text area
- ✅ Back button to return to previous page
- ✅ Real-time form validation and error handling

### Admin Management
- ✅ Goals can be added, edited, and disabled by admins
- ✅ Diet types can be added, edited, and disabled by admins
- ✅ Display order control for both goals and diet types
- ✅ Active/inactive status for filtering options

### Database Models
- ✅ `Goal` model - Stores user goals (weight loss, muscle gain, etc.)
- ✅ `DietType` model - Stores diet types (vegan, vegetarian, etc.)
- ✅ Updated `UserProfile` model with:
  - `ManyToManyField` relationship to `Goal`
  - `ForeignKey` relationship to `DietType`
  - Profile image support
  - Description field

## Backend Changes

### Models (`backend/src/profiles/models.py`)
- Created `Goal` model with fields:
  - `code` (unique identifier)
  - `name` (display name)
  - `description` (optional)
  - `is_active` (enable/disable)
  - `display_order` (sorting)
- Created `DietType` model with same structure
- Updated `UserProfile` to use relationships instead of JSON fields

### API Endpoints (`backend/src/profiles/views.py`)
- `GET /api/profiles/me` - Get current user's profile
- `PUT /api/profiles/me` - Update current user's profile
- `GET /api/profiles/username/<username>` - Get profile by username (own profile only)
- `GET /api/profiles/goals/` - Get all active goals (public)
- `GET /api/profiles/diet-types/` - Get all active diet types (public)

### Serializers (`backend/src/profiles/serializers.py`)
- `GoalSerializer` - Serializes goal data
- `DietTypeSerializer` - Serializes diet type data
- `UserProfileSerializer` - Full profile with nested goals and diet
- `UserProfileUpdateSerializer` - Handles profile updates with `goal_ids` and `diet_id`

### Admin Interface (`backend/src/profiles/admin.py`)
- `GoalAdmin` - Manage goals with list display, filtering, and editing
- `DietTypeAdmin` - Manage diet types with same features
- `UserProfileAdmin` - View and manage user profiles with filter_horizontal for goals

### Migrations
- `0002_goals_diettypes.py` - Creates Goal and DietType models, updates UserProfile
- `0003_populate_goals_diettypes.py` - Populates initial data:
  - 18 goals (Weight Loss, Muscle Gain, Heart Health, etc.)
  - 25 diet types (Vegan, Vegetarian, Keto, Gluten-Free, etc.)

## Frontend Changes

### Profile Page (`frontend/src/app/profile/page.tsx`)
- Complete profile management UI
- Image upload with preview
- Dynamic goals loading from API
- Dynamic diet types loading from API
- Form state management
- Error handling and toast notifications
- Responsive design

### API Client (`frontend/src/lib/api.ts`)
- `profileAPI.getGoals()` - Fetch all active goals
- `profileAPI.getDietTypes()` - Fetch all active diet types
- `profileAPI.getProfile()` - Fetch user profile
- `profileAPI.updateProfile()` - Update user profile with FormData support

### TypeScript Interfaces
- `Goal` - Goal data structure
- `DietType` - Diet type data structure
- `UserProfile` - Full profile structure
- `UpdateProfileRequest` - Profile update payload

## Database Schema

### Goals Table
```sql
- id (Primary Key)
- code (Unique, e.g., 'weight_loss')
- name (Display name, e.g., 'Weight Loss')
- description (Optional)
- is_active (Boolean)
- display_order (Integer)
- created_at, updated_at
```

### Diet Types Table
```sql
- id (Primary Key)
- code (Unique, e.g., 'vegan')
- name (Display name, e.g., 'Vegan')
- description (Optional)
- is_active (Boolean)
- display_order (Integer)
- created_at, updated_at
```

### User Profiles Table (Updated)
```sql
- user_id (Primary Key, Foreign Key to User)
- profile_image (ImageField)
- diet_id (Foreign Key to DietType, nullable)
- description (TextField)
- created_at, updated_at
- goals (ManyToMany to Goal)
```

## Initial Data

### Goals (18 total)
1. Weight Loss
2. Weight Gain
3. Muscle Gain
4. Maintain Weight
5. Improve Health
6. Increase Energy
7. Better Nutrition
8. Meal Prep
9. Healthy Eating
10. Build Strength
11. Improve Digestion
12. Heart Health
13. Diabetes Management
14. Reduce Inflammation
15. Boost Immunity
16. Improve Skin Health
17. Better Sleep
18. Sports Performance

### Diet Types (25 total)
1. No Specific Diet
2. Vegan
3. Vegetarian
4. Pescatarian
5. Keto
6. Paleo
7. Mediterranean
8. Gluten-Free
9. Lactose-Free
10. Dairy-Free
11. Low Carb
12. Low Fat
13. Low Sodium
14. High Protein
15. Whole30
16. DASH Diet
17. Low FODMAP
18. Raw Food
19. Intermittent Fasting
20. Flexitarian
21. Nut-Free
22. Egg-Free
23. Soy-Free
24. Halal
25. Kosher

## Testing

### Manual Testing Steps
1. **Access Profile Page**
   - Navigate to `/profile`
   - Verify profile page loads with user data

2. **Test Goals Selection**
   - Check multiple goals
   - Verify goals are saved correctly
   - Verify goals persist after page refresh

3. **Test Diet Selection**
   - Select a diet type from dropdown
   - Verify diet is saved correctly
   - Change diet and verify update

4. **Test Image Upload**
   - Upload a profile image
   - Verify image preview appears
   - Verify image is saved and displayed

5. **Test Admin Management**
   - Access Django admin
   - Add/edit/disable goals
   - Add/edit/disable diet types
   - Verify changes reflect on profile page

### API Testing
```bash
# Get goals
curl http://localhost:8000/api/profiles/goals/

# Get diet types
curl http://localhost:8000/api/profiles/diet-types/

# Get profile (requires authentication)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/profiles/me
```

## Migration Instructions

1. **Run Migrations**
   ```bash
   docker-compose exec backend python3 manage.py migrate profiles
   ```

2. **Verify Data**
   ```bash
   docker-compose exec backend python3 manage.py shell
   >>> from profiles.models import Goal, DietType
   >>> Goal.objects.count()  # Should be 18
   >>> DietType.objects.count()  # Should be 25
   ```

## UI/UX Features

- **Circular Avatar**: Grey background with white initial when no image
- **Image Preview**: Shows uploaded image before saving
- **Dynamic Options**: Goals and diets load from database
- **Form Validation**: Client-side validation with error messages
- **Loading States**: Shows loading indicators during API calls
- **Toast Notifications**: Success/error messages for user actions
- **Responsive Design**: Works on mobile and desktop

## Security

- ✅ Authentication required to view/edit profile
- ✅ Users can only view/edit their own profile
- ✅ Profile image upload validation (file type, size)
- ✅ API endpoints protected with authentication
- ✅ CSRF protection for form submissions

## Files Changed

### Backend
- `backend/src/profiles/models.py` - Added Goal, DietType models
- `backend/src/profiles/views.py` - Added API endpoints
- `backend/src/profiles/serializers.py` - Added serializers
- `backend/src/profiles/admin.py` - Added admin interfaces
- `backend/src/profiles/urls.py` - Added URL routes
- `backend/src/profiles/migrations/0002_goals_diettypes.py` - Schema migration
- `backend/src/profiles/migrations/0003_populate_goals_diettypes.py` - Data migration

### Frontend
- `frontend/src/app/profile/page.tsx` - Profile page component
- `frontend/src/lib/api.ts` - API client methods

## Breaking Changes
None - This is a new feature addition.

## Future Enhancements
- [ ] Profile image cropping/editing
- [ ] Multiple profile images
- [ ] Profile visibility settings
- [ ] Social sharing of profile
- [ ] Profile completion percentage
- [ ] Achievement badges based on goals

## Screenshots

### Profile Page
![Profile Page](./screenshots/profile-page.png)
*User profile page showing avatar, goals selection, diet preference, and description fields*

### Profile Page with Goals Selected
![Profile Page with Goals](./screenshots/profile-page-goals.png)
*Profile page displaying selected goals (Weight Loss, Muscle Gain, etc.)*

### Profile Page with Diet Selected
![Profile Page with Diet](./screenshots/profile-page-diet.png)
*Profile page showing selected diet type (Vegan, Vegetarian, etc.)*

### Profile Avatar (Default)
![Default Avatar](./screenshots/profile-avatar-default.png)
*Circular grey avatar with user's initial when no profile image is uploaded*

### Profile Avatar (With Image)
![Avatar with Image](./screenshots/profile-avatar-image.png)
*Profile avatar displaying uploaded user image*

### Django Admin - Goals Management
![Admin Goals](./screenshots/admin-goals.png)
*Django admin interface for managing goals (add, edit, disable)*

### Django Admin - Diet Types Management
![Admin Diet Types](./screenshots/admin-diet-types.png)
*Django admin interface for managing diet types*

### Django Admin - User Profile
![Admin User Profile](./screenshots/admin-user-profile.png)
*Django admin showing user profile with selected goals and diet*

---

**Note:** To add screenshots:
1. Take screenshots of the profile page in different states
2. Take screenshots of the Django admin interface
3. Save them in a `screenshots/` folder in the project root
4. Update the image paths above to match your screenshot filenames

## Related Issues
- Closes #[issue-number]

## Checklist
- [x] Code follows project style guidelines
- [x] Tests added/updated
- [x] Documentation updated
- [x] Migrations created and tested
- [x] Admin interface configured
- [x] Initial data populated
- [x] API endpoints tested
- [x] Frontend components tested
- [x] Error handling implemented
- [x] Loading states implemented
- [x] Responsive design verified
