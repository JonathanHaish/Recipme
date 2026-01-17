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
} from "./ui/dropdown-menu";

const RECIPE_TYPES = [
  "Vegan",
  "Vegetarian",
  "Lactose-free",
  "Flour-free",
  "Full of protein",
  "Full of vegetables",
];

interface FiltersDropdownProps {
  checkedTypes: string[];
  checkedNutrition: boolean;
  checkedTopLiked: boolean;
  checkedSaved: boolean;
  onTypeToggle: (type: string) => void;
  onNutritionToggle: () => void;
  onTopLikedToggle: () => void;
  onSavedToggle: () => void;
  onClearFilters: () => void;
}

export function FiltersDropdown({
  checkedTypes,
  checkedNutrition,
  checkedTopLiked,
  checkedSaved,
  onTypeToggle,
  onNutritionToggle,
  onTopLikedToggle,
  onSavedToggle,
  onClearFilters,
}: FiltersDropdownProps) {
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
            Type
          </DropdownMenuSubTrigger>
          <DropdownMenuSubContent className="bg-white border border-black text-black">
            {RECIPE_TYPES.map((type) => (
              <DropdownMenuCheckboxItem
                key={type}
                checked={checkedTypes.includes(type)}
                onCheckedChange={() => onTypeToggle(type)}
                className="cursor-pointer focus:bg-gray-100 text-black"
              >
                {type}
              </DropdownMenuCheckboxItem>
            ))}
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
