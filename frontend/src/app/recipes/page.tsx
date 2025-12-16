"use client";

import { useState } from "react";
import { Search, Heart, Bookmark, ChefHat } from "lucide-react";

interface Recipe {
  id: number;
  title: string;
  date: string;
  likes: number;
  tag: string;
}

export default function RecipesPage() {
  const [favorites, setFavorites] = useState<Record<number, boolean>>({});

  const recipes: Recipe[] = [
    { id: 1, title: "Recipe Title", date: "Date & time", likes: 0, tag: "Vegetarian" },
    { id: 2, title: "Recipe Title", date: "Date & time", likes: 0, tag: "Gluten-Free" },
    { id: 3, title: "Recipe Title", date: "Date & time", likes: 0, tag: "Cacantac" },
    { id: 4, title: "Recipe Title", date: "Date & time", likes: 0, tag: "Italian-Free" },
    { id: 5, title: "Recipe Title", date: "Date & time", likes: 0, tag: "Vegetarian" },
    { id: 6, title: "Recipe Title", date: "Date & time", likes: 0, tag: "Sieburglc" },
  ];

  const toggleFavorite = (id: number) => {
    setFavorites((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6" dir="rtl">
      {/* Header */}
      <div className="max-w-5xl mx-auto mb-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <ChefHat className="w-10 h-10 text-black" />
            <h1 className="text-3xl font-bold text-black">Recipes</h1>
          </div>
          <div className="flex gap-3">
            <button className="px-4 py-2 border border-black rounded hover:bg-gray-100 text-black">
              Admin points
            </button>
            <button className="px-4 py-2 border border-black rounded hover:bg-gray-100 text-black">
              Add Recipe
            </button>
            <button className="px-4 py-2 border border-black rounded hover:bg-gray-100 text-black">
              Filters
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-black" />
          <input
            type="text"
            placeholder="Search recipes"
            className="w-full pr-10 pl-4 py-2 border border-black rounded text-black"
          />
        </div>
      </div>

      {/* Recipe Grid */}
      <div className="max-w-5xl mx-auto grid grid-cols-2 gap-6">
        {recipes.map((recipe) => (
          <div
            key={recipe.id}
            className="bg-white border-2 border-black rounded-lg overflow-hidden"
          >
            {/* Header with date and icons */}
            <div className="flex items-center justify-between px-3 py-2 border-b border-black">
              <span className="text-sm text-black">{recipe.date}</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => toggleFavorite(recipe.id)}
                  className="flex items-center gap-1"
                >
                  <Heart
                    className={`w-4 h-4 text-black stroke-black ${
                      favorites[recipe.id] ? "fill-black" : ""
                    }`}
                  />
                  <span className="text-sm text-black">{recipe.likes}</span>
                </button>
                <Bookmark className="w-4 h-4 text-black stroke-black" />
              </div>
            </div>

            {/* Image placeholder */}
            <div className="h-40 bg-white border-b border-black"></div>

            {/* Tag */}
            <div className="px-3 py-2 border-b border-black">
              <span className="inline-block px-2 py-1 border border-black rounded text-sm text-black">
                {recipe.tag}
              </span>
            </div>

            {/* Title */}
            <div className="px-3 py-3 border-b border-black">
              <h3 className="text-xl font-bold text-black">{recipe.title}</h3>
              <div className="mt-2 space-y-1">

              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2 p-3">
              <button className="p-2 border border-black rounded hover:bg-gray-100">
                <Bookmark className="w-5 h-5 text-black stroke-black" />
              </button>
              <button className="flex-1 py-2 border border-black rounded hover:bg-gray-100 font-medium text-black">
                Read More
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
