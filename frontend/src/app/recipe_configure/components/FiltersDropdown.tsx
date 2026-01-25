import { useEffect, useState } from "react";
import { ChevronRight } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
  DropdownMenuSeparator,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
} from "./ui/dropdown-menu";
import { tagsAPI, Tag } from "@/lib/api";

interface FiltersDropdownProps {
  checkedTagIds: number[];
  checkedNutrition: boolean;
  checkedTopLiked: boolean;
  checkedSaved: boolean;
  filterMatchMode: 'any' | 'all';
  onTagToggle: (tagId: number) => void;
  onNutritionToggle: () => void;
  onTopLikedToggle: () => void;
  onSavedToggle: () => void;
  onFilterMatchModeChange: (mode: 'any' | 'all') => void;
  onClearFilters: () => void;
}

export function FiltersDropdown({
  checkedTagIds,
  checkedNutrition,
  checkedTopLiked,
  checkedSaved,
  filterMatchMode,
  onTagToggle,
  onNutritionToggle,
  onTopLikedToggle,
  onSavedToggle,
  onFilterMatchModeChange,
  onClearFilters,
}: FiltersDropdownProps) {
  const [availableTags, setAvailableTags] = useState<Tag[]>([]);
  const [isLoadingTags, setIsLoadingTags] = useState(false);

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

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="px-4 py-2 border border-black rounded hover:bg-gray-100 text-black whitespace-nowrap">
          Filters
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="bg-white border border-black text-black min-w-[220px]" align="start">
        <DropdownMenuSub>
          <DropdownMenuSubTrigger className="cursor-pointer focus:bg-gray-100 text-black data-[state=open]:bg-gray-100">
            Tags {checkedTagIds.length > 0 && `(${checkedTagIds.length})`}
          </DropdownMenuSubTrigger>
          <DropdownMenuSubContent className="bg-white border border-black text-black max-h-[300px] overflow-y-auto">
            {isLoadingTags ? (
              <DropdownMenuItem disabled className="text-gray-500">
                Loading tags...
              </DropdownMenuItem>
            ) : availableTags.length === 0 ? (
              <DropdownMenuItem disabled className="text-gray-500">
                No tags available
              </DropdownMenuItem>
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
                    <div className="px-2 py-2">
                      <p className="text-xs font-medium text-gray-600 mb-1">Match mode:</p>
                      <DropdownMenuRadioGroup value={filterMatchMode} onValueChange={(value) => onFilterMatchModeChange(value as 'any' | 'all')}>
                        <DropdownMenuRadioItem value="any" className="cursor-pointer text-xs">
                          Any tag (OR)
                        </DropdownMenuRadioItem>
                        <DropdownMenuRadioItem value="all" className="cursor-pointer text-xs">
                          All tags (AND)
                        </DropdownMenuRadioItem>
                      </DropdownMenuRadioGroup>
                    </div>
                  </>
                )}
              </>
            )}
          </DropdownMenuSubContent>
        </DropdownMenuSub>
        
        <DropdownMenuCheckboxItem
          checked={checkedNutrition}
          onCheckedChange={onNutritionToggle}
          className="cursor-pointer focus:bg-gray-100 text-black"
        >
          Nutritional value
        </DropdownMenuCheckboxItem>
        
        <DropdownMenuCheckboxItem
          checked={checkedTopLiked}
          onCheckedChange={onTopLikedToggle}
          className="cursor-pointer focus:bg-gray-100 text-black"
        >
          Top 10 in likes
        </DropdownMenuCheckboxItem>
        
        <DropdownMenuCheckboxItem
          checked={checkedSaved}
          onCheckedChange={onSavedToggle}
          className="cursor-pointer focus:bg-gray-100 text-black"
        >
          User saved
        </DropdownMenuCheckboxItem>
        
        <DropdownMenuSeparator className="bg-gray-300" />
        
        <DropdownMenuItem
          onClick={onClearFilters}
          className="cursor-pointer focus:bg-gray-100 text-black"
        >
          Clean filters
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
