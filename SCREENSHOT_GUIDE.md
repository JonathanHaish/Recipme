# Screenshot Guide for Profile Component PR

This guide will help you capture all the necessary screenshots for the Profile Component PR.

## Required Screenshots

### 1. Profile Page - Empty State
**File:** `screenshots/profile-page-empty.png`
- Navigate to `/profile`
- Show the profile page with no goals selected and "No Specific Diet" selected
- Should show the circular grey avatar with user's initial

### 2. Profile Page - With Goals Selected
**File:** `screenshots/profile-page-goals.png`
- Select multiple goals (e.g., Weight Loss, Muscle Gain, Improve Health)
- Show the checkboxes checked
- Keep diet as "No Specific Diet"

### 3. Profile Page - With Diet Selected
**File:** `screenshots/profile-page-diet.png`
- Select a diet type from dropdown (e.g., Vegan, Keto)
- Show the dropdown with the selected value
- Can have goals selected or not

### 4. Profile Page - Complete Profile
**File:** `screenshots/profile-page-complete.png`
- Show profile with:
  - Multiple goals selected
  - Diet type selected
  - Description filled in
  - Profile image uploaded (if possible)

### 5. Profile Avatar - Default State
**File:** `screenshots/profile-avatar-default.png`
- Close-up of the circular grey avatar
- Should show the user's initial (e.g., "J") in white on grey background
- No profile image uploaded

### 6. Profile Avatar - With Image
**File:** `screenshots/profile-avatar-image.png`
- Close-up of the avatar with uploaded profile image
- Should show the circular image

### 7. Django Admin - Goals List
**File:** `screenshots/admin-goals.png`
- Navigate to Django admin: `http://localhost:8000/admin/profiles/goal/`
- Show the list of goals with columns: Name, Code, Is Active, Display Order
- Should show all 18 goals

### 8. Django Admin - Goal Edit
**File:** `screenshots/admin-goal-edit.png`
- Click on a goal to edit
- Show the edit form with fields: Name, Code, Description, Is Active, Display Order

### 9. Django Admin - Diet Types List
**File:** `screenshots/admin-diet-types.png`
- Navigate to Django admin: `http://localhost:8000/admin/profiles/diettype/`
- Show the list of diet types with all 25 options

### 10. Django Admin - Diet Type Edit
**File:** `screenshots/admin-diet-type-edit.png`
- Click on a diet type to edit
- Show the edit form

### 11. Django Admin - User Profile
**File:** `screenshots/admin-user-profile.png`
- Navigate to Django admin: `http://localhost:8000/admin/profiles/userprofile/`
- Click on a user profile
- Show the profile with selected goals (filter_horizontal widget) and diet dropdown

### 12. Profile Page - Success Toast
**File:** `screenshots/profile-save-success.png`
- After saving profile changes
- Show the success toast notification

### 13. Profile Page - Error State
**File:** `screenshots/profile-error.png`
- Show error handling (if possible to trigger)
- Or show validation errors

## How to Take Screenshots

### Using Browser DevTools
1. Open the page you want to screenshot
2. Press `F12` or `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac)
3. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
4. Type "screenshot" and select:
   - "Capture area screenshot" for specific area
   - "Capture full size screenshot" for entire page
   - "Capture node screenshot" for specific element

### Using Browser Extensions
- **Firefox**: Use built-in screenshot tool or "Firefox Screenshots" extension
- **Chrome**: Use "Full Page Screen Capture" extension
- **Edge**: Use built-in screenshot tool

### Using System Tools
- **Windows**: `Win + Shift + S` for Snipping Tool
- **Mac**: `Cmd + Shift + 4` for screenshot tool
- **Linux**: Use `gnome-screenshot` or `scrot`

## Screenshot Best Practices

1. **Resolution**: Use at least 1920x1080 or higher
2. **Format**: Save as PNG for best quality
3. **Naming**: Use descriptive, kebab-case filenames
4. **Cropping**: Crop to show relevant content, remove unnecessary browser UI
5. **Annotations**: Consider adding arrows or highlights for important features
6. **Consistency**: Use same browser and zoom level for all screenshots

## Creating the Screenshots Folder

```bash
mkdir -p screenshots
```

## Example Screenshot Workflow

1. Start the application:
   ```bash
   docker-compose up
   ```

2. Navigate to profile page:
   - Open `http://localhost:3000/profile`
   - Login if needed

3. Take screenshots in order:
   - Empty state
   - Select goals
   - Select diet
   - Upload image
   - Save and show success

4. Access Django admin:
   - Open `http://localhost:8000/admin`
   - Login as admin
   - Navigate to Goals, Diet Types, User Profiles

5. Take admin screenshots

6. Organize files:
   - All screenshots should be in `screenshots/` folder
   - Use descriptive names
   - Update PR document with correct paths

## Quick Screenshot Checklist

- [ ] Profile page empty state
- [ ] Profile page with goals selected
- [ ] Profile page with diet selected
- [ ] Profile page complete
- [ ] Default avatar (grey circle with initial)
- [ ] Avatar with uploaded image
- [ ] Admin goals list
- [ ] Admin goal edit
- [ ] Admin diet types list
- [ ] Admin diet type edit
- [ ] Admin user profile
- [ ] Success toast notification
- [ ] Error state (if applicable)

## Adding Screenshots to PR

After taking screenshots:

1. Create `screenshots/` folder in project root
2. Add all PNG files to the folder
3. Update `PR_PROFILE_COMPONENT.md` with correct image paths
4. Commit screenshots to repository:
   ```bash
   git add screenshots/
   git commit -m "Add screenshots for profile component PR"
   ```

## Alternative: Using Markdown Image Placeholders

If you prefer to add screenshots later, you can use placeholders:

```markdown
![Profile Page](./screenshots/profile-page.png)
*Description of what the screenshot shows*
```

The images will be added when you're ready to include them in the PR.
