import { useState, useRef, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/app/recipe_configure/components/ui/dialog";
import { Button } from "@/app/recipe_configure/components/ui/button";
import { Input } from "@/app/recipe_configure/components/ui/input";
import { Label } from "@/app/recipe_configure/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/app/recipe_configure/components/ui/select";
import { X, Plus, Upload, Trash2, Image as ImageIcon } from "lucide-react";
import {FoodSearch} from "./searchIngredients"
import { recipesAPI, tagsAPI, Tag } from "@/lib/api";

interface Ingredient {
  id: string;
  name: string;
  amount: string;
  unit?: string; // Unit of measurement (cups, grams, tablespoons, etc.)
  fdc_id?: number; // Food Data Central API ID
}

interface Recipe {
  id?: string;
  name: string;
  type: string;
  instructions?: string;
  image?: string;
  ingredients: Ingredient[];
  tags?: Tag[];
}

interface RecipeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (recipe: Recipe) => void;
  recipe?: Recipe | null;
  mode: "create" | "edit";
}

export function RecipeModal({ isOpen, onClose, onSave, recipe, mode }: RecipeModalProps) {
  const [formData, setFormData] = useState<Recipe>({
    name: recipe?.name || "",
    type: recipe?.type || "",
    instructions: recipe?.instructions || "",
    image: recipe?.image || "",
    ingredients: recipe?.ingredients || [],
    tags: recipe?.tags || [],
  });

  const [availableTags, setAvailableTags] = useState<Tag[]>([]);
  const [isLoadingTags, setIsLoadingTags] = useState(false);
  const [newIngredientName, setNewIngredientName] = useState("");
  const [newIngredientAmount, setNewIngredientAmount] = useState("");
  const [isIngredientValid, setIsIngredientValid] = useState(false);
  const [selectedIngredientData, setSelectedIngredientData] = useState<any>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load available tags on mount
  useEffect(() => {
    const loadTags = async () => {
      setIsLoadingTags(true);
      try {
        const tags = await tagsAPI.getAllTags();
        setAvailableTags(tags);
      } catch (error) {
        console.error('Error loading tags:', error);
      } finally {
        setIsLoadingTags(false);
      }
    };
    loadTags();
  }, []);

  // Reset form when modal opens in create mode
  useEffect(() => {
    if (isOpen && mode === "create" && !recipe) {
      // Reset form to initial state when opening in create mode
      setFormData({
        name: "",
        type: "",
        instructions: "",
        image: "",
        ingredients: [],
        tags: [],
      });
      setNewIngredientName("");
      setNewIngredientAmount("");
      setNewIngredientUnit("");
      setIsIngredientValid(false);
      setSelectedIngredientData(null);
      setSubmitError(null);
    } else if (isOpen && recipe) {
      // Load recipe data when in edit mode
      setFormData({
        name: recipe.name || "",
        type: recipe.type || "",
        instructions: recipe.instructions || "",
        image: recipe.image || "",
        ingredients: recipe.ingredients || [],
        tags: recipe.tags || [],
      });
    }
  }, [isOpen, mode, recipe]);

  // Lock body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const resetForm = () => {
    setFormData({
      name: "",
      type: "",
      instructions: "",
      image: "",
      ingredients: [],
      tags: [],
    });
    setNewIngredientName("");
    setNewIngredientAmount("");
    setNewIngredientUnit("");
    setIsIngredientValid(false);
    setSubmitError(null);
    // Reset file input if it exists
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleInputChange = (field: keyof Recipe, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleTagSelect = (tag: Tag) => {
    const isSelected = formData.tags?.some(t => t.id === tag.id);
    if (isSelected) {
      // Remove tag
      setFormData(prev => ({
        ...prev,
        tags: prev.tags?.filter(t => t.id !== tag.id) || []
      }));
    } else {
      // Add tag
      setFormData(prev => ({
        ...prev,
        tags: [...(prev.tags || []), tag]
      }));
    }
  };

  const handleTagRemove = (tagId: number) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags?.filter(t => t.id !== tagId) || []
    }));
  };

  const handleAddIngredient = () => {
    if (!isIngredientValid) {
      alert("Please select an ingredient from the search results");
      return;
    }
    if (newIngredientName.trim() && newIngredientAmount.trim()) {
      const newIngredient: Ingredient = {
        id: Date.now().toString(),
        name: newIngredientName,
        amount: newIngredientAmount,
        unit: "g", // Always use grams
        fdc_id: selectedIngredientData?.id, // Store the fdc_id from selected ingredient
      };
      setFormData((prev) => ({
        ...prev,
        ingredients: [...prev.ingredients, newIngredient],
      }));
      setNewIngredientName("");
      setNewIngredientAmount("");
      setIsIngredientValid(false);
      setSelectedIngredientData(null);
    }
  };

  const handleRemoveIngredient = (id: string) => {
    setFormData((prev) => ({
      ...prev,
      ingredients: prev.ingredients.filter((ing) => ing.id !== id),
    }));
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData((prev) => ({ ...prev, image: reader.result as string }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    // Validate required fields
    if (!formData.name.trim()) {
      setSubmitError("Recipe name is required");
      return;
    }

    if (formData.ingredients.length === 0) {
      setSubmitError("Please add at least one ingredient");
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      // Set type field from tags for backward compatibility
      const recipeData = {
        ...formData,
        type: formData.tags?.map(t => t.name).join(', ') || ''
      };

      if (mode === "create") {
        // Create new recipe via API
        const createdRecipe = await recipesAPI.createRecipe(recipeData);
        
        // Transform backend response to frontend format for the callback
        const frontendRecipe: Recipe = {
          id: createdRecipe.id?.toString(),
          name: createdRecipe.title,
          type: createdRecipe.description,
          instructions: createdRecipe.instructions,
          ingredients: formData.ingredients,
          image: formData.image,
        };
        
        // Call the parent callback to update local state
        onSave(frontendRecipe);
        // Reset form after successful creation
        resetForm();
        onClose();
      } else {
        // Update existing recipe
        if (recipe?.id) {
          const updatedRecipe = await recipesAPI.updateRecipe(recipe.id, recipeData);
          const frontendRecipe: Recipe = {
            id: updatedRecipe.id?.toString(),
            name: updatedRecipe.title,
            type: updatedRecipe.description,
            instructions: updatedRecipe.instructions,
            ingredients: formData.ingredients,
            image: formData.image,
          };
          onSave(frontendRecipe);
          onClose();
        }
      }
    } catch (error) {
      console.error("Error saving recipe:", error);
      setSubmitError(error instanceof Error ? error.message : "Failed to save recipe. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    onClose();
  };


  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="relative z-[10000] w-full max-w-2xl rounded-xl border-2 border-black bg-white shadow-xl max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b-2 border-black px-5 py-4">
          <h2 className="text-xl font-bold text-black">
            {mode === "create" ? "Create Recipe" : "Update Recipe"}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="text-2xl font-bold text-black hover:text-gray-600"
          >
            ×
          </button>
        </div>

        {/* Modal Content */}
        <div className="overflow-y-auto px-5 py-4 flex-1">
          <div className="space-y-6">
            {/* Recipe Name */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-black">Recipe Name</label>
              <input
                value={formData.name}
                onChange={(e) => handleInputChange("name", e.target.value)}
                placeholder="Enter recipe name"
                className="w-full px-3 py-2 border border-black rounded text-black"
              />
            </div>

            {/* Recipe Tags */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-black">Recipe Tags (Optional)</label>

              {/* Selected Tags */}
              {formData.tags && formData.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 p-3 border-2 border-black rounded-lg bg-gray-50">
                  {formData.tags.map((tag) => (
                    <span
                      key={tag.id}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-black text-white rounded-full text-sm font-medium"
                    >
                      {tag.name}
                      <button
                        type="button"
                        onClick={() => handleTagRemove(tag.id)}
                        className="hover:bg-gray-800 rounded-full p-0.5"
                      >
                        <X className="size-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}

              {/* Tag Limit Warning */}
              {formData.tags && formData.tags.length > 5 && (
                <div className="text-sm text-amber-600 bg-amber-50 border border-amber-200 rounded p-2">
                  ⚠️ You have selected more than 5 tags. Consider using fewer tags for better organization.
                </div>
              )}

              {/* Available Tags */}
              <div>
                <p className="text-xs text-gray-600 mb-2">Available tags:</p>
                <div className="flex flex-wrap gap-2">
                  {isLoadingTags ? (
                    <p className="text-sm text-gray-500">Loading tags...</p>
                  ) : availableTags.length === 0 ? (
                    <p className="text-sm text-gray-500">No tags available</p>
                  ) : (
                    availableTags.map((tag) => {
                      const isSelected = formData.tags?.some(t => t.id === tag.id);
                      return (
                        <button
                          key={tag.id}
                          type="button"
                          onClick={() => handleTagSelect(tag)}
                          className={`px-3 py-1 rounded-full text-sm font-medium border-2 transition-colors ${
                            isSelected
                              ? 'bg-black text-white border-black'
                              : 'bg-white text-black border-black hover:bg-gray-100'
                          }`}
                        >
                          {tag.name}
                        </button>
                      );
                    })
                  )}
                </div>
              </div>
            </div>

            {/* Instructions */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-black">Instructions</label>
              <textarea
                value={formData.instructions || ""}
                onChange={(e) => handleInputChange("instructions", e.target.value)}
                placeholder="Enter recipe instructions..."
                rows={6}
                className="w-full px-3 py-2 border border-black rounded text-black resize-y"
              />
            </div>

            {/* Image Upload */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-black">Recipe Image</label>
              <div className="flex gap-3 items-start">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="px-4 py-2 border border-black rounded hover:bg-gray-100 text-black flex items-center gap-2"
                >
                  <Upload className="size-4" />
                  Upload Image
                </button>
                {formData.image && (
                  <div className="relative w-24 h-24 border-2 border-black rounded-lg overflow-hidden">
                    <img
                      src={formData.image}
                      alt="Recipe preview"
                      className="w-full h-full object-cover"
                    />
                    <button
                      type="button"
                      className="absolute top-1 right-1 bg-black text-white rounded size-6 flex items-center justify-center hover:bg-gray-800"
                      onClick={() => setFormData((prev) => ({ ...prev, image: "" }))}
                    >
                      <X className="size-3" />
                    </button>
                  </div>
                )}
                {!formData.image && (
                  <div className="w-24 h-24 border-2 border-dashed border-black rounded-lg flex items-center justify-center bg-gray-50">
                    <ImageIcon className="size-8 text-gray-400" />
                  </div>
                )}
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleImageUpload}
              />
            </div>

            {/* Ingredients Section */}
            <div className="space-y-3">
              <label className="text-sm font-medium text-black">Ingredients</label>

              {/* Add New Ingredient */}
              <div className="flex gap-2">
                <div className="flex-1">
                  <FoodSearch
                    value={newIngredientName}
                    onChange={(value) => setNewIngredientName(value)}
                    onSelect={(ingredient) => {
                      setNewIngredientName(ingredient.name);
                      setSelectedIngredientData(ingredient); // Store full ingredient object
                      setIsIngredientValid(true);
                    }}
                    onValidSelection={(isValid) => setIsIngredientValid(isValid)}
                    placeholder="Search and select ingredient name"
                    className="w-full"
                  />
                </div>
                <div className="flex flex-col w-32">
                  <input
                    type="number"
                    value={newIngredientAmount}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewIngredientAmount(e.target.value)}
                    placeholder="Amount"
                    className="w-full px-3 py-2 border border-black rounded text-black"
                  />
                  <span className="text-xs text-gray-600 mt-1 text-center">grams (g)</span>
                </div>
                <button
                  type="button"
                  onClick={handleAddIngredient}
                  className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800 flex items-center gap-2"
                >
                  <Plus className="size-4" />
                  Add
                </button>
              </div>

              {/* Ingredients List */}
              <div className="space-y-2 max-h-64 overflow-y-auto border-2 border-black rounded-lg p-3">
                {formData.ingredients.length === 0 ? (
                  <p className="text-sm text-gray-500 text-center py-4">
                    No ingredients added yet
                  </p>
                ) : (
                  formData.ingredients.map((ingredient) => (
                    <div
                      key={ingredient.id}
                      className="flex items-center justify-between p-3 border border-black rounded-lg"
                    >
                      <div className="flex-1">
                        <p className="font-medium text-black">{ingredient.name}</p>
                        <p className="text-sm text-gray-600">
                          Amount: {ingredient.amount} g
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveIngredient(ingredient.id)}
                        className="p-2 text-black hover:bg-gray-100 rounded"
                      >
                        <Trash2 className="size-4" />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {submitError && (
          <div className="px-5 py-2 border-t-2 border-black">
            <div className="text-red-600 text-sm bg-red-50 border border-red-200 rounded p-2">
              {submitError}
            </div>
          </div>
        )}

        {/* Modal Footer */}
        <div className="flex justify-end gap-3 border-t-2 border-black px-5 py-3">
          <button
            type="button"
            onClick={handleCancel}
            disabled={isSubmitting}
            className="px-5 py-2 border border-black rounded hover:bg-gray-100 text-black font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="px-5 py-2 bg-black text-white rounded hover:bg-gray-800 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting 
              ? (mode === "create" ? "Creating..." : "Updating...") 
              : (mode === "create" ? "Create Recipe" : "Update Recipe")
            }
          </button>
        </div>
      </div>
    </div>
  );
}