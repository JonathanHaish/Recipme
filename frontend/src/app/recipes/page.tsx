"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Search, Heart, Bookmark, ChefHat, LogOut, User } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { ingredientsAPI, type Ingredient, type NutritionData } from "@/lib/api";

export default function RecipesPage() {
  const [favorites, setFavorites] = useState<Record<number, boolean>>({});
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Ingredient[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedIngredient, setSelectedIngredient] = useState<Ingredient | null>(null);
  const [nutritionData, setNutritionData] = useState<NutritionData | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loadingNutrition, setLoadingNutrition] = useState(false);

  const toggleFavorite = (id: number) => {
    setFavorites((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setHasSearched(false);
      return;
    }

    setIsSearching(true);
    setHasSearched(true);
    try {
      const results = await ingredientsAPI.searchIngredients(searchQuery);
      setSearchResults(results);
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
            <button className="px-4 py-2 border border-black rounded hover:bg-gray-100 text-black">
              Admin points
            </button>
            <button className="px-4 py-2 border border-black rounded hover:bg-gray-100 text-black">
              Add Recipe
            </button>
            <button className="px-4 py-2 border border-black rounded hover:bg-gray-100 text-black">
              Filters
            </button>
            
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
            placeholder="Search ingredients..."
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

      {/* Content Area - Search Results or Empty State */}
      <div className="max-w-5xl mx-auto">
        {isSearching ? (
          <div className="text-center py-12">
            <p className="text-lg text-gray-600">Searching ingredients...</p>
          </div>
        ) : hasSearched ? (
          searchResults.length > 0 ? (
            <div>
              <h2 className="text-xl font-bold mb-6">Search Results ({searchResults.length}):</h2>
              <div className="grid grid-cols-2 gap-6">
                {searchResults.map((item, index) => (
                  <div
                    key={index}
                    className="bg-white border-2 border-black rounded-lg overflow-hidden"
                  >
                    {/* Header with ID and icons */}
                    <div className="flex items-center justify-between px-3 py-2 border-b border-black">
                      <span className="text-sm text-black">ID: {item.id}</span>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => toggleFavorite(item.id)}
                          className="flex items-center gap-1"
                        >
                          <Heart
                            className={`w-4 h-4 text-black stroke-black ${
                              favorites[item.id] ? "fill-black" : ""
                            }`}
                          />
                        </button>
                        <Bookmark className="w-4 h-4 text-black stroke-black" />
                      </div>
                    </div>

                    {/* Image placeholder */}
                    <div className="h-40 bg-white border-b border-black"></div>

                    {/* Category Tag */}
                    {item.category && (
                      <div className="px-3 py-2 border-b border-black">
                        <span className="inline-block px-2 py-1 border border-black rounded text-sm text-black">
                          {item.category}
                        </span>
                      </div>
                    )}

                    {/* Name/Title */}
                    <div className="px-3 py-3 border-b border-black">
                      <h3 className="text-xl font-bold text-black">{item.name}</h3>
                      {item.description && (
                        <p className="text-sm text-gray-600 mt-2">{item.description}</p>
                      )}
                      {item.fat_str && (
                        <p className="text-sm text-gray-600 mt-1">
                          <span className="font-medium">Fat:</span> {item.fat_str}
                        </p>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 p-3" onClick={(e) => e.stopPropagation()}>
                      <button 
                        type="button"
                        className="p-2 border border-black rounded hover:bg-gray-100"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                        }}
                      >
                        <Bookmark className="w-5 h-5 text-black stroke-black" />
                      </button>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          handleReadMore(item);
                        }}
                        className="flex-1 py-2 border border-black rounded hover:bg-gray-100 font-medium text-black"
                      >
                        Read More
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-lg text-gray-600 mb-2">No ingredients found for "{searchQuery}"</p>
              <p className="text-sm text-gray-500">Try searching for something else</p>
            </div>
          )
        ) : (
          <div className="text-center py-12">
            <p className="text-lg text-gray-600 mb-2">Search for ingredients to get started</p>
            <p className="text-sm text-gray-500">Enter a food name in the search bar above</p>
          </div>
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

    </div>
  );
}
