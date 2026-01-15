import { useState, useRef, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/app/recipe_configure/components/ui/dialog";
import { Button } from "@/app/recipe_configure/components/ui/button";
import { Input } from "@/app/recipe_configure/components/ui/input";
import { Label } from "@/app/recipe_configure/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/app/recipe_configure/components/ui/select";
import { X, Plus, Upload, Trash2, Image as ImageIcon } from "lucide-react";
import {FoodSearch} from "./searchIngredients"

interface Ingredient {
  id: string;
  name: string;
  amount: string;
}

interface Recipe {
  id?: string;
  name: string;
  type: string;
  dateCreated?: string;
  dateUpdated?: string;
  image?: string;
  ingredients: Ingredient[];
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
    dateCreated: recipe?.dateCreated || new Date().toISOString().split('T')[0],
    dateUpdated: new Date().toISOString().split('T')[0],
    image: recipe?.image || "",
    ingredients: recipe?.ingredients || [],
  });

  const [newIngredientName, setNewIngredientName] = useState("");
  const [newIngredientAmount, setNewIngredientAmount] = useState("");
  const [searchIngredient, setSearchIngredient] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  const handleInputChange = (field: keyof Recipe, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleAddIngredient = () => {
    if (newIngredientName.trim() && newIngredientAmount.trim()) {
      const newIngredient: Ingredient = {
        id: Date.now().toString(),
        name: newIngredientName,
        amount: newIngredientAmount,
      };
      setFormData((prev) => ({
        ...prev,
        ingredients: [...prev.ingredients, newIngredient],
      }));
      setNewIngredientName("");
      setNewIngredientAmount("");
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

  const handleSubmit = () => {
    onSave(formData);
    onClose();
  };

  const handleCancel = () => {
    onClose();
  };

  const filteredIngredients = formData.ingredients.filter((ing) =>
    ing.name.toLowerCase().includes(searchIngredient.toLowerCase())
  );

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

            {/* Recipe Type */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-black">Recipe Type</label>
              <Select value={formData.type} onValueChange={(value) => handleInputChange("type", value)}>
                <SelectTrigger className="border-black">
                  <SelectValue placeholder="Select recipe type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="breakfast">Breakfast</SelectItem>
                  <SelectItem value="lunch">Lunch</SelectItem>
                  <SelectItem value="dinner">Dinner</SelectItem>
                  <SelectItem value="dessert">Dessert</SelectItem>
                  <SelectItem value="snack">Snack</SelectItem>
                  <SelectItem value="appetizer">Appetizer</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Dates */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-black">Date Created</label>
                <input
                  type="date"
                  value={formData.dateCreated}
                  onChange={(e) => handleInputChange("dateCreated", e.target.value)}
                  disabled={mode === "edit"}
                  className="w-full px-3 py-2 border border-black rounded text-black disabled:bg-gray-100"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-black">Date Updated</label>
                <input
                  type="date"
                  value={formData.dateUpdated}
                  onChange={(e) => handleInputChange("dateUpdated", e.target.value)}
                  className="w-full px-3 py-2 border border-black rounded text-black"
                />
              </div>
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
              
              {/* Search Ingredients */}
              <input
                value={searchIngredient}
                onChange={(e) => setSearchIngredient(e.target.value)}
                placeholder="Search ingredients..."
                className="w-full px-3 py-2 border border-black rounded text-black"
              />

              {/* Add New Ingredient */}
              <div className="flex gap-2">
                <input
                  value={newIngredientName}
                  onChange={(e) => setNewIngredientName(e.target.value)}
                  placeholder="Ingredient name"
                  className="flex-1 px-3 py-2 border border-black rounded text-black"
                />
                <input
                  value={newIngredientAmount}
                  onChange={(e) => setNewIngredientAmount(e.target.value)}
                  placeholder="Amount"
                  className="w-32 px-3 py-2 border border-black rounded text-black"
                />
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
                {filteredIngredients.length === 0 ? (
                  <p className="text-sm text-gray-500 text-center py-4">
                    No ingredients added yet
                  </p>
                ) : (
                  filteredIngredients.map((ingredient) => (
                    <div
                      key={ingredient.id}
                      className="flex items-center justify-between p-3 border border-black rounded-lg"
                    >
                      <div className="flex-1">
                        <p className="font-medium text-black">{ingredient.name}</p>
                        <p className="text-sm text-gray-600">Amount: {ingredient.amount}</p>
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

        {/* Modal Footer */}
        <div className="flex justify-end gap-3 border-t-2 border-black px-5 py-3">
          <button
            type="button"
            onClick={handleCancel}
            className="px-5 py-2 border border-black rounded hover:bg-gray-100 text-black font-medium"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            className="px-5 py-2 bg-black text-white rounded hover:bg-gray-800 font-medium"
          >
            {mode === "create" ? "Create Recipe" : "Update Recipe"}
          </button>
        </div>
      </div>
    </div>
  );
}