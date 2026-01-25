# Demo Data Population

This document describes how to populate the database with demo data for testing and presentations.

## Usage

### Populate Demo Data

Run this command to create demo users and recipes:

```bash
docker exec backend-django python3 manage.py populate_demo_data
```

This creates:
- **4 demo users** (3 regular users + 1 admin)
- **8 demo recipes** with realistic data including:
  - Tags (Vegan, Vegetarian, Gluten-free, etc.)
  - Ingredients with FDC IDs (for nutrition calculation)
  - Instructions and cooking times
  - Likes and saves from various users

### Clear and Repopulate

To clear existing demo data and start fresh:

```bash
docker exec backend-django python3 manage.py populate_demo_data --clear
```

## Demo User Accounts

All demo users have the password: **`demo123`**

| Email | Username | Role | Description |
|-------|----------|------|-------------|
| demo@example.com | demo_user | User | Regular user account |
| chef@example.com | chef_john | User | Regular user account |
| foodie@example.com | foodie_sarah | User | Regular user account |
| admin@example.com | admin_demo | Admin | Admin account with staff privileges |

## Demo Recipes

The command creates 8 diverse recipes:

1. **Classic Chicken Caesar Salad** - High-protein
2. **Vegan Buddha Bowl** - Vegan, Vegetarian, High-protein
3. **Spaghetti Carbonara** - Quick & Easy
4. **Greek Yogurt Parfait** - Vegetarian, High-protein, Quick & Easy
5. **Grilled Salmon with Asparagus** - High-protein, Low-carb
6. **Vegetarian Stir-Fry** - Vegan, Vegetarian, Quick & Easy
7. **Avocado Toast with Poached Egg** - Vegetarian, High-protein, Quick & Easy
8. **Lentil Soup** - Vegan, Vegetarian, High-protein

Each recipe includes:
- Beautiful food images from Unsplash
- Realistic ingredients with FDC IDs for nutrition calculation
- Preparation and cooking times
- Serving sizes
- Step-by-step instructions
- Multiple tags for filtering

## Features Tested

The demo data allows you to test:
- ✅ Multiple users and recipes
- ✅ Recipe images (hosted on Unsplash)
- ✅ Tag filtering (OR/AND logic)
- ✅ Nutrition data display
- ✅ Recipe likes and saves
- ✅ Recipe search
- ✅ User-specific content (owner vs other users)
- ✅ Admin privileges (edit/delete any recipe)
- ✅ Sorting by likes

## Notes

- The command is **idempotent** - it won't create duplicates if run multiple times
- All recipes have valid FDC IDs so nutrition data will be calculated automatically
- Recipe images are hosted on Unsplash (external URLs) - no local storage needed for demo
- Recipes are distributed among users to simulate a multi-user environment
- Each user has liked and saved random recipes for realistic interactions
