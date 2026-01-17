"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Search, Heart, Bookmark, ChefHat, LogOut, User } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { ingredientsAPI, recipesAPI, type Ingredient, type NutritionData, type BackendRecipe } from "@/lib/api";
import { RecipeGrid } from "@/app/recipe_configure/components/RecipeGrid";
import { EditRecipeModal } from "@/app/recipe_configure/components/EditRecipeModal";
import { RecipeModal } from "@/app/recipe_configure/components/RecipeModal";
import { ViewRecipeModal } from "@/app/recipe_configure/components/ViewRecipeModal";
import { RecipeActionsDropdown } from "@/app/recipe_configure/components/RecipeActionsDropdown";
import { FiltersDropdown } from "@/app/recipe_configure/components/FiltersDropdown";

export default function App() {
  const [favorites, setFavorites] = useState<Record<number, boolean>>({});
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [activeFilter, setActiveFilter] = useState<string | null>(null);
  const [checkedTypes, setCheckedTypes] = useState<string[]>([]);
  const [checkedNutrition, setCheckedNutrition] = useState(false);
  const [checkedTopLiked, setCheckedTopLiked] = useState(false);
  const [checkedSaved, setCheckedSaved] = useState(false);
  const [allRecipes, setAllRecipes] = useState<any[]>([]);
  const [selectedIngredient, setSelectedIngredient] = useState<Ingredient | null>(null);
  const [nutritionData, setNutritionData] = useState<NutritionData | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loadingNutrition, setLoadingNutrition] = useState(false);
  const [recipes, setRecipes] = useState<any[]>([]);
  const [loadingRecipes, setLoadingRecipes] = useState(false);
  const [recipeLikes, setRecipeLikes] = useState<Record<string, boolean>>({});
  const [recipeSaves, setRecipeSaves] = useState<Record<string, boolean>>({});
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isRecipeEditModalOpen, setIsRecipeEditModalOpen] = useState(false);
  const [selectedRecipeForEdit, setSelectedRecipeForEdit] = useState<any>(null);
  const [isRecipeCreateModalOpen, setIsRecipeCreateModalOpen] = useState(false);
  const [isViewRecipeModalOpen, setIsViewRecipeModalOpen] = useState(false);
  const [selectedRecipeForView, setSelectedRecipeForView] = useState<any>(null);

  const toggleFavorite = (id: number) => {
    setFavorites((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  const transformBackendToFrontend = (backendRecipes: BackendRecipe[]) => {
    return backendRecipes.map((recipe: BackendRecipe) => ({
      id: recipe.id?.toString(),
      name: recipe.title,
      type: recipe.description,
      instructions: recipe.instructions,
      image: "",
      dateCreated: recipe.created_at ? new Date(recipe.created_at).toISOString().split('T')[0] : undefined,
      dateUpdated: recipe.updated_at ? new Date(recipe.updated_at).toISOString().split('T')[0] : undefined,
      ingredients: recipe.ingredients?.map((ing, idx) => ({
        id: idx.toString(),
        name: ing.ingredient_name || '',
        amount: ing.quantity || '',
      })) || [],
      isLiked: recipe.is_liked || false,
      isSaved: recipe.is_saved || false,
      likesCount: recipe.likes_count || 0,
    }));
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setHasSearched(false);
      setActiveFilter(null);
      // Don't clear filters when clearing search - let them remain
      return;
    }

    setIsSearching(true);
    setHasSearched(true);
    setActiveFilter(null);
    // Don't clear filter checkboxes, but search results will be shown instead
    try {
      const backendRecipes = await recipesAPI.searchRecipes(searchQuery);
      const frontendRecipes = transformBackendToFrontend(backendRecipes);
      setSearchResults(frontendRecipes);
    } catch (error) {
      console.error("Search error:", error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  const handleReadMore = async (ingredient: Ingredient) => {
    // Prevent any navigation
  //  window.history.pushState(null, '', window.location.href);
    
    setSelectedIngredient(ingredient);
    setIsModalOpen(true);
    setLoadingNutrition(true);
    setNutritionData(null);

    try {
      const nutrition = await ingredientsAPI.getNutritionData(ingredient.id);
      setNutritionData(nutrition);
    } catch (error) {
      console.error("Error fetching nutrition data:", error);
    } finally {
      setLoadingNutrition(false);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedIngredient(null);
    setNutritionData(null);
  };

  // Fetch all recipes on mount
  useEffect(() => {
    const fetchRecipes = async () => {
      if (!user) return; // Only fetch if user is logged in
      
      setLoadingRecipes(true);
      try {
        const backendRecipes = await recipesAPI.getMyRecipes();
        // Transform backend format to frontend format
        const frontendRecipes = transformBackendToFrontend(backendRecipes);
        setAllRecipes(frontendRecipes);
        setRecipes(frontendRecipes);
      } catch (error) {
        console.error("Error fetching recipes:", error);
        setAllRecipes([]);
        setRecipes([]);
      } finally {
        setLoadingRecipes(false);
      }
    };

    fetchRecipes();
  }, [user]);

  // Apply filters whenever filter states change
  useEffect(() => {
    if (!user || hasSearched) return; // Don't apply filters if searching
    
    let filtered = [...allRecipes];

    // Filter by types
    if (checkedTypes.length > 0) {
      filtered = filtered.filter(recipe => 
        checkedTypes.some(type => 
          recipe.type?.toLowerCase().includes(type.toLowerCase())
        )
      );
    }

    // Filter by top liked
    if (checkedTopLiked) {
      // Sort by created_at desc and take top 10
      filtered = filtered.sort((a, b) => {
        const dateA = new Date(a.dateUpdated || a.dateCreated || 0).getTime();
        const dateB = new Date(b.dateUpdated || b.dateCreated || 0).getTime();
        return dateB - dateA;
      }).slice(0, 10);
    }

    // Filter by saved
    if (checkedSaved) {
      filtered = filtered.filter(recipe => recipe.isSaved || recipe.status === 'published');
    }

    // Filter by nutrition (placeholder - can be enhanced)
    if (checkedNutrition) {
      // For now, just pass through - can be enhanced with actual nutrition filtering
    }

    setRecipes(filtered);
  }, [checkedTypes, checkedNutrition, checkedTopLiked, checkedSaved, allRecipes, user, hasSearched]);

  // Update recipes when likes/saves change
  useEffect(() => {
    setRecipes((prevRecipes) =>
      prevRecipes.map((recipe) => ({
        ...recipe,
        isLiked: recipeLikes[recipe.id || ''] || false,
        isSaved: recipeSaves[recipe.id || ''] || false,
      }))
    );
  }, [recipeLikes, recipeSaves]);

  // Lock body scroll when modal is open
  useEffect(() => {
    if (isModalOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    // Cleanup on unmount
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isModalOpen]);

  const handleToggleLike = async (recipeId: string) => {
    try {
      const response = await recipesAPI.toggleLike(recipeId);
      // Update the recipe in the list with new like status and count
      setAllRecipes(prevRecipes =>
        prevRecipes.map(r => 
          r.id === recipeId 
            ? { ...r, isLiked: response.liked, likesCount: response.likes_count }
            : r
        )
      );
      setRecipeLikes((prev) => ({ ...prev, [recipeId]: response.liked }));
    } catch (error) {
      console.error("Error toggling like:", error);
    }
  };

  const handleToggleSave = async (recipeId: string) => {
    try {
      const response = await recipesAPI.toggleSave(recipeId);
      // Update the recipe in the list with new save status
      setAllRecipes(prevRecipes =>
        prevRecipes.map(r => 
          r.id === recipeId 
            ? { ...r, isSaved: response.saved }
            : r
        )
      );
      setRecipeSaves((prev) => ({ ...prev, [recipeId]: response.saved }));
    } catch (error) {
      console.error("Error toggling save:", error);
    }
  };

  const handleEditRecipe = (recipe: any) => {
    // TODO: Implement edit functionality
    console.log("Edit recipe:", recipe);
  };

  const handleViewDetails = (recipe: any) => {
    setSelectedRecipeForView(recipe);
    setIsViewRecipeModalOpen(true);
  };

  const handleOpenEditModal = () => {
    setIsEditModalOpen(true);
  };

  const handleOpenCreateModal = () => {
    setIsRecipeCreateModalOpen(true);
  };

  const handleSelectRecipeFromTable = (recipe: any) => {
    setSelectedRecipeForEdit(recipe);
    setIsEditModalOpen(false);
    setIsRecipeEditModalOpen(true);
  };

  const handleDeleteRecipes = async (recipeIds: string[]) => {
    try {
      // Delete each recipe from backend
      await Promise.all(recipeIds.map(id => recipesAPI.deleteRecipe(id)));
      
      // Remove deleted recipes from state
      setAllRecipes(prevRecipes => prevRecipes.filter(r => !recipeIds.includes(r.id || '')));
      
      // Refresh recipes to ensure consistency
      await refreshRecipes();
    } catch (error) {
      console.error("Error deleting recipes:", error);
      alert("Failed to delete recipes. Please try again.");
    }
  };

  const refreshRecipes = async () => {
    if (user) {
      try {
        const backendRecipes = await recipesAPI.getMyRecipes();
        const frontendRecipes = transformBackendToFrontend(backendRecipes);
        setAllRecipes(frontendRecipes);
        // Filters will be applied via useEffect
      } catch (error) {
        console.error("Error refreshing recipes:", error);
      }
    }
  };

  const handleSaveEditedRecipe = async (recipe: any) => {
    setIsRecipeEditModalOpen(false);
    setSelectedRecipeForEdit(null);
    await refreshRecipes();
  };

  const handleSaveCreatedRecipe = async (recipe: any) => {
    setIsRecipeCreateModalOpen(false);
    await refreshRecipes();
  };

  const handleTypeToggle = (type: string) => {
    setHasSearched(false);
    setSearchQuery("");
    setSearchResults([]);
    setCheckedTypes(prev => 
      prev.includes(type) 
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  const handleNutritionToggle = () => {
    setHasSearched(false);
    setSearchQuery("");
    setSearchResults([]);
    setCheckedNutrition(prev => !prev);
  };

  const handleTopLikedToggle = () => {
    setHasSearched(false);
    setSearchQuery("");
    setSearchResults([]);
    setCheckedTopLiked(prev => !prev);
  };

  const handleSavedToggle = () => {
    setHasSearched(false);
    setSearchQuery("");
    setSearchResults([]);
    setCheckedSaved(prev => !prev);
  };

  const handleClearFilters = () => {
    setCheckedTypes([]);
    setCheckedNutrition(false);
    setCheckedTopLiked(false);
    setCheckedSaved(false);
    setActiveFilter(null);
    setHasSearched(false);
    setSearchQuery("");
    setSearchResults([]);
  };

  const hasAnyNutrition =
      !!nutritionData?.calories ||
      !!nutritionData?.protein ||
      !!nutritionData?.fat ||
      !!nutritionData?.carbohydrates ||
      !!nutritionData?.fiber ||
      !!nutritionData?.sugars;


  return (
    <div className="min-h-screen bg-gray-50 p-6" dir="ltr">
      {/* Header */}
      <div className="max-w-5xl mx-auto mb-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <ChefHat className="w-10 h-10 text-black" />
            <h1 className="text-3xl font-bold text-black">Recipes</h1>
          </div>
          <div className="flex items-center gap-3">
            <button className="px-4 py-2 border border-black rounded hover:bg-gray-100 text-black whitespace-nowrap">
              Admin points
            </button>
            <RecipeActionsDropdown 
              onAddRecipe={handleOpenCreateModal}
              onEditRecipe={handleOpenEditModal}
            />
            <FiltersDropdown
              checkedTypes={checkedTypes}
              checkedNutrition={checkedNutrition}
              checkedTopLiked={checkedTopLiked}
              checkedSaved={checkedSaved}
              onTypeToggle={handleTypeToggle}
              onNutritionToggle={handleNutritionToggle}
              onTopLikedToggle={handleTopLikedToggle}
              onSavedToggle={handleSavedToggle}
              onClearFilters={handleClearFilters}
            />
            
            
            {/* User Info & Logout */}
            <div className="flex items-center gap-2 pl-3 border-l-2 border-gray-300">
              {loading ? (
                <div className="text-sm text-gray-600">Loading...</div>
              ) : user ? (
                <>
                  <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded">
                    <User className="w-4 h-4 text-black" />
                    <span className="text-sm font-medium text-black">{user.email}</span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 px-4 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors"
                    title="Logout"
                  >
                    <LogOut className="w-4 h-4" />
                    <span className="text-sm">Logout</span>
                  </button>
                </>
              ) : (
                <button
                  onClick={() => router.push("/login")}
                  className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800"
                >
                  Login
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-black" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Search recipes..."
            className="w-full pl-10 pr-24 py-2 border border-black rounded text-black"
          />
          <button
            onClick={handleSearch}
            disabled={isSearching}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 px-4 py-1 bg-black text-white rounded hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          >
            {isSearching ? "Searching..." : "Search"}
          </button>
        </div>
      </div>

      {/* Content Area - Recipes or Search Results */}
      <div className="max-w-5xl mx-auto">
        {isSearching ? (
          <div className="text-center py-12">
            <p className="text-lg text-gray-600">Searching recipes...</p>
          </div>
        ) : hasSearched ? (
          searchResults.length > 0 ? (
            <RecipeGrid
              recipes={searchResults}
              onEdit={handleEditRecipe}
              onViewDetails={handleViewDetails}
              onToggleLike={handleToggleLike}
              onToggleSave={handleToggleSave}
              isAdmin={user?.is_staff || user?.is_superuser || false}
            />
          ) : (
            <div className="text-center py-12">
              <p className="text-lg text-gray-600 mb-2">No recipes found for "{searchQuery}"</p>
              <p className="text-sm text-gray-500">Try searching for something else</p>
            </div>
          )
        ) : loadingRecipes ? (
          <div className="text-center py-12">
            <p className="text-lg text-gray-600">Loading recipes...</p>
          </div>
        ) : (
          <RecipeGrid
            recipes={recipes}
            onEdit={handleEditRecipe}
            onViewDetails={handleViewDetails}
            onToggleLike={handleToggleLike}
            onToggleSave={handleToggleSave}
            isAdmin={user?.is_staff || user?.is_superuser || false}
          />
        )}
      </div>

       

      {/* Nutrition Modal */}
      {isModalOpen && (
          <div
              className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 p-4"
              onClick={closeModal}
          >
            <div
                className="relative z-[10000] w-full max-w-md rounded-xl border-2 border-black bg-white shadow-xl"
                onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between border-b-2 border-black px-5 py-4">
                <h2 className="text-xl font-bold text-black">
                  {selectedIngredient?.name || "Nutrition Information"}
                </h2>
                <button
                    type="button"
                    onClick={closeModal}
                    className="text-2xl font-bold text-black hover:text-gray-600"
                >
                  ×
                </button>
              </div>

              {/* Modal Content */}
              <div className="max-h-[60vh] overflow-y-auto px-5 py-4">
                {loadingNutrition ? (
                    <div className="text-center py-6">
                      <p className="text-gray-600">Loading nutrition data...</p>
                    </div>
                ) : nutritionData && hasAnyNutrition ? (
                    <div className="space-y-3">
                      <h3 className="text-lg font-bold text-black mb-2">Nutrition Facts</h3>

                      {nutritionData.calories && (
                          <div className="flex items-center justify-between border-b py-2">
                            <span className="font-medium text-black">Calories (Energy)</span>
                            <span className="text-black">{nutritionData.calories.value}</span>
                          </div>
                      )}

                      {nutritionData.protein && (
                          <div className="flex items-center justify-between border-b py-2">
                            <span className="font-medium text-black">Protein</span>
                            <span className="text-black">{nutritionData.protein.value}</span>
                          </div>
                      )}

                      {nutritionData.fat && (
                          <div className="flex items-center justify-between border-b py-2">
                            <span className="font-medium text-black">Total Fat</span>
                            <span className="text-black">{nutritionData.fat.value} {nutritionData.fat.unit}</span>
                          </div>
                      )}


                      {nutritionData.carbohydrates && (
                          <div className="flex items-center justify-between border-b py-2">
                            <span className="font-medium text-black">Carbohydrates</span>
                            <span className="text-black">{nutritionData.carbohydrates.value} {nutritionData.carbohydrates.unit}</span>
                          </div>
                      )}

                      {nutritionData.fiber && (
                          <div className="flex items-center justify-between border-b py-2">
                            <span className="font-medium text-black">Fiber</span>
                            <span className="text-black">{nutritionData.fiber.value} {nutritionData.fiber.unit}</span>
                          </div>
                      )}

                      {nutritionData.sugars && (
                          <div className="flex items-center justify-between border-b py-2">
                            <span className="font-medium text-black">Sugars</span>
                            <span className="text-black">{nutritionData.sugars.value} {nutritionData.sugars.unit}</span>
                          </div>
                      )}
                    </div>
                ) : (
                    <div className="text-center py-6">
                      <p className="text-gray-600">No nutrition data available</p>
                    </div>
                )}
              </div>

              {/* Modal Footer */}
              <div className="flex justify-end border-t-2 border-black px-5 py-3">
                <button
                    type="button"
                    onClick={closeModal}
                    className="rounded bg-black px-5 py-2 text-white hover:bg-gray-800 font-medium"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
      )}

      {/* Edit Recipe Modal - Table of Recipes */}
      <EditRecipeModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        recipes={recipes}
        onSelectRecipe={handleSelectRecipeFromTable}
        onDeleteRecipes={handleDeleteRecipes}
      />

      {/* Recipe Edit Modal */}
      <RecipeModal
        isOpen={isRecipeEditModalOpen}
        onClose={() => {
          setIsRecipeEditModalOpen(false);
          setSelectedRecipeForEdit(null);
        }}
        onSave={handleSaveEditedRecipe}
        recipe={selectedRecipeForEdit}
        mode="edit"
      />

      {/* Recipe Create Modal */}
      <RecipeModal
        isOpen={isRecipeCreateModalOpen}
        onClose={() => setIsRecipeCreateModalOpen(false)}
        onSave={handleSaveCreatedRecipe}
        recipe={null}
        mode="create"
      />

      {/* View Recipe Modal */}
      <ViewRecipeModal
        isOpen={isViewRecipeModalOpen}
        onClose={() => {
          setIsViewRecipeModalOpen(false);
          setSelectedRecipeForView(null);
        }}
        recipe={selectedRecipeForView}
      />

    </div>
  );
}
