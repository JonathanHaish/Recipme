import { useEffect, useState } from "react";
import { X, ChevronDown } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "./ui/dropdown-menu";
import { tagsAPI, Tag } from "@/lib/api";

interface NutritionFilter {
  calories_kcal?: { min?: number; max?: number };
  protein_g?: { min?: number; max?: number };
  fat_g?: { min?: number; max?: number };
  carbs_g?: { min?: number; max?: number };
  fiber_g?: { min?: number; max?: number };
  sugars_g?: { min?: number; max?: number };
}

interface FilterBarProps {
  checkedTagIds: number[];
  tagMatchMode: 'any' | 'all';
  nutritionFilters: NutritionFilter;
  likesSortOrder: 'none' | 'asc' | 'desc';
  showSavedOnly: boolean;
  onTagToggle: (tagId: number) => void;
  onTagsClear: () => void;
  onTagMatchModeChange: (mode: 'any' | 'all') => void;
  onNutritionFilterChange: (filters: NutritionFilter) => void;
  onLikesSortChange: (order: 'none' | 'asc' | 'desc') => void;
  onSavedOnlyToggle: () => void;
}

export function FilterBar({
  checkedTagIds,
  tagMatchMode,
  nutritionFilters,
  likesSortOrder,
  showSavedOnly,
  onTagToggle,
  onTagsClear,
  onTagMatchModeChange,
  onNutritionFilterChange,
  onLikesSortChange,
  onSavedOnlyToggle,
}: FilterBarProps) {
  const [availableTags, setAvailableTags] = useState<Tag[]>([]);
  const [isLoadingTags, setIsLoadingTags] = useState(false);
  const [localNutritionFilters, setLocalNutritionFilters] = useState<NutritionFilter>(nutritionFilters);
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false);

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

  const handleNutritionInputChange = (field: keyof NutritionFilter, type: 'min' | 'max', value: string) => {
    const numValue = value === '' ? undefined : Number(value);
    const updatedFilters = {
      ...localNutritionFilters,
      [field]: {
        ...localNutritionFilters[field],
        [type]: numValue,
      },
    };
    setLocalNutritionFilters(updatedFilters);
  };

  const applyNutritionFilters = () => {
    onNutritionFilterChange(localNutritionFilters);
  };

  const clearNutritionFilters = () => {
    const emptyFilters: NutritionFilter = {};
    setLocalNutritionFilters(emptyFilters);
    onNutritionFilterChange(emptyFilters);
  };

  const hasActiveNutritionFilters = Object.keys(localNutritionFilters).some(
    key => localNutritionFilters[key as keyof NutritionFilter]?.min !== undefined ||
           localNutritionFilters[key as keyof NutritionFilter]?.max !== undefined
  );

  return (
    <div className="bg-gray-50 border-2 border-black rounded-lg mb-4">
      {/* Mobile Filter Toggle - Hidden on desktop */}
      <button
        onClick={() => setIsMobileFilterOpen(!isMobileFilterOpen)}
        className="lg:hidden w-full flex items-center justify-between p-4 text-sm font-medium text-black"
      >
        <span>Filters {(checkedTagIds.length > 0 || hasActiveNutritionFilters || showSavedOnly) && `(Active)`}</span>
        <ChevronDown className={`w-5 h-5 transition-transform ${isMobileFilterOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Filter Content - Collapsed on mobile, always visible on desktop */}
      <div className={`${isMobileFilterOpen ? 'flex' : 'hidden'} lg:flex flex-wrap items-center gap-3 p-4 ${isMobileFilterOpen ? 'border-t-2 border-black' : ''}`}>
        {/* Tags Filter */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-black">Tags:</span>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="px-3 py-1.5 text-sm border-2 border-black rounded bg-white hover:bg-gray-100 text-black min-w-[120px] text-left">
              {checkedTagIds.length > 0 ? `${checkedTagIds.length} selected` : 'Select tags'}
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="bg-white border-2 border-black text-black max-h-[300px] overflow-y-auto">
            {isLoadingTags ? (
              <div className="px-3 py-2 text-sm text-gray-500">Loading tags...</div>
            ) : availableTags.length === 0 ? (
              <div className="px-3 py-2 text-sm text-gray-500">No tags available</div>
            ) : (
              <>
                {availableTags.map((tag) => (
                  <DropdownMenuCheckboxItem
                    key={tag.id}
                    checked={checkedTagIds.includes(tag.id)}
                    onCheckedChange={() => onTagToggle(tag.id)}
                    className="cursor-pointer focus:bg-gray-100 text-black"
                  >
                    {tag.name}
                  </DropdownMenuCheckboxItem>
                ))}
                {checkedTagIds.length > 0 && (
                  <>
                    <DropdownMenuSeparator className="bg-gray-300" />
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        onTagsClear();
                      }}
                      className="w-full px-2 py-1.5 text-sm text-red-600 hover:bg-red-50 text-left"
                    >
                      Clear all tags
                    </button>
                  </>
                )}
              </>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
        {checkedTagIds.length > 1 && (
          <div className="flex items-center gap-1">
            <button
              onClick={() => onTagMatchModeChange('any')}
              className={`px-2 py-1 text-xs border-2 border-black rounded-l transition-colors ${
                tagMatchMode === 'any'
                  ? 'bg-black text-white'
                  : 'bg-white text-black hover:bg-gray-100'
              }`}
            >
              OR
            </button>
            <button
              onClick={() => onTagMatchModeChange('all')}
              className={`px-2 py-1 text-xs border-2 border-l-0 border-black rounded-r transition-colors ${
                tagMatchMode === 'all'
                  ? 'bg-black text-white'
                  : 'bg-white text-black hover:bg-gray-100'
              }`}
            >
              AND
            </button>
          </div>
        )}
      </div>

      {/* Nutrition Filters */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-black">Nutrition:</span>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="px-3 py-1.5 text-sm border-2 border-black rounded bg-white hover:bg-gray-100 text-black">
              {hasActiveNutritionFilters ? 'Filters active' : 'Add filters'}
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="bg-white border-2 border-black text-black w-[320px] p-3">
            <div className="space-y-3">
              {/* Calories */}
              <div>
                <label className="text-xs font-medium text-black mb-1 block">Calories (kcal)</label>
                <div className="flex gap-2 items-center">
                  <input
                    type="number"
                    placeholder="Min"
                    value={localNutritionFilters.calories_kcal?.min ?? ''}
                    onChange={(e) => handleNutritionInputChange('calories_kcal', 'min', e.target.value)}
                    className="w-full px-2 py-1 text-sm border border-black rounded"
                  />
                  <span className="text-sm">-</span>
                  <input
                    type="number"
                    placeholder="Max"
                    value={localNutritionFilters.calories_kcal?.max ?? ''}
                    onChange={(e) => handleNutritionInputChange('calories_kcal', 'max', e.target.value)}
                    className="w-full px-2 py-1 text-sm border border-black rounded"
                  />
                </div>
              </div>

              {/* Protein */}
              <div>
                <label className="text-xs font-medium text-black mb-1 block">Protein (g)</label>
                <div className="flex gap-2 items-center">
                  <input
                    type="number"
                    placeholder="Min"
                    value={localNutritionFilters.protein_g?.min ?? ''}
                    onChange={(e) => handleNutritionInputChange('protein_g', 'min', e.target.value)}
                    className="w-full px-2 py-1 text-sm border border-black rounded"
                  />
                  <span className="text-sm">-</span>
                  <input
                    type="number"
                    placeholder="Max"
                    value={localNutritionFilters.protein_g?.max ?? ''}
                    onChange={(e) => handleNutritionInputChange('protein_g', 'max', e.target.value)}
                    className="w-full px-2 py-1 text-sm border border-black rounded"
                  />
                </div>
              </div>

              {/* Fat */}
              <div>
                <label className="text-xs font-medium text-black mb-1 block">Fat (g)</label>
                <div className="flex gap-2 items-center">
                  <input
                    type="number"
                    placeholder="Min"
                    value={localNutritionFilters.fat_g?.min ?? ''}
                    onChange={(e) => handleNutritionInputChange('fat_g', 'min', e.target.value)}
                    className="w-full px-2 py-1 text-sm border border-black rounded"
                  />
                  <span className="text-sm">-</span>
                  <input
                    type="number"
                    placeholder="Max"
                    value={localNutritionFilters.fat_g?.max ?? ''}
                    onChange={(e) => handleNutritionInputChange('fat_g', 'max', e.target.value)}
                    className="w-full px-2 py-1 text-sm border border-black rounded"
                  />
                </div>
              </div>

              {/* Carbs */}
              <div>
                <label className="text-xs font-medium text-black mb-1 block">Carbohydrates (g)</label>
                <div className="flex gap-2 items-center">
                  <input
                    type="number"
                    placeholder="Min"
                    value={localNutritionFilters.carbs_g?.min ?? ''}
                    onChange={(e) => handleNutritionInputChange('carbs_g', 'min', e.target.value)}
                    className="w-full px-2 py-1 text-sm border border-black rounded"
                  />
                  <span className="text-sm">-</span>
                  <input
                    type="number"
                    placeholder="Max"
                    value={localNutritionFilters.carbs_g?.max ?? ''}
                    onChange={(e) => handleNutritionInputChange('carbs_g', 'max', e.target.value)}
                    className="w-full px-2 py-1 text-sm border border-black rounded"
                  />
                </div>
              </div>

              {/* Fiber */}
              <div>
                <label className="text-xs font-medium text-black mb-1 block">Fiber (g)</label>
                <div className="flex gap-2 items-center">
                  <input
                    type="number"
                    placeholder="Min"
                    value={localNutritionFilters.fiber_g?.min ?? ''}
                    onChange={(e) => handleNutritionInputChange('fiber_g', 'min', e.target.value)}
                    className="w-full px-2 py-1 text-sm border border-black rounded"
                  />
                  <span className="text-sm">-</span>
                  <input
                    type="number"
                    placeholder="Max"
                    value={localNutritionFilters.fiber_g?.max ?? ''}
                    onChange={(e) => handleNutritionInputChange('fiber_g', 'max', e.target.value)}
                    className="w-full px-2 py-1 text-sm border border-black rounded"
                  />
                </div>
              </div>

              {/* Sugars */}
              <div>
                <label className="text-xs font-medium text-black mb-1 block">Sugars (g)</label>
                <div className="flex gap-2 items-center">
                  <input
                    type="number"
                    placeholder="Min"
                    value={localNutritionFilters.sugars_g?.min ?? ''}
                    onChange={(e) => handleNutritionInputChange('sugars_g', 'min', e.target.value)}
                    className="w-full px-2 py-1 text-sm border border-black rounded"
                  />
                  <span className="text-sm">-</span>
                  <input
                    type="number"
                    placeholder="Max"
                    value={localNutritionFilters.sugars_g?.max ?? ''}
                    onChange={(e) => handleNutritionInputChange('sugars_g', 'max', e.target.value)}
                    className="w-full px-2 py-1 text-sm border border-black rounded"
                  />
                </div>
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  onClick={applyNutritionFilters}
                  className="flex-1 px-3 py-1.5 text-sm bg-black text-white rounded hover:bg-gray-800"
                >
                  Apply
                </button>
                <button
                  onClick={clearNutritionFilters}
                  className="flex-1 px-3 py-1.5 text-sm border border-black rounded hover:bg-gray-100"
                >
                  Clear
                </button>
              </div>
            </div>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Sort by Likes */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-black">Sort by likes:</span>
        <select
          value={likesSortOrder}
          onChange={(e) => onLikesSortChange(e.target.value as 'none' | 'asc' | 'desc')}
          className="px-3 py-1.5 text-sm border-2 border-black rounded bg-white hover:bg-gray-100 text-black"
        >
          <option value="none">None</option>
          <option value="asc">Ascending</option>
          <option value="desc">Descending</option>
        </select>
      </div>

      {/* Saved Only */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-black">Saved:</span>
        <button
          onClick={onSavedOnlyToggle}
          className={`px-3 py-1.5 text-sm border-2 border-black rounded transition-colors ${
            showSavedOnly
              ? 'bg-black text-white hover:bg-gray-800'
              : 'bg-white text-black hover:bg-gray-100'
          }`}
        >
          {showSavedOnly ? 'Saved only' : 'All recipes'}
        </button>
      </div>
      </div>
    </div>
  );
}
