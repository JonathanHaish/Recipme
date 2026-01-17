import { ChevronDown } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";

interface RecipeActionsDropdownProps {
  onAddRecipe: () => void;
  onEditRecipe: () => void;
}

export function RecipeActionsDropdown({ onAddRecipe, onEditRecipe }: RecipeActionsDropdownProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="px-4 py-2 border border-black rounded hover:bg-gray-100 text-black flex items-center gap-2 whitespace-nowrap">
          Recipe Actions
          <ChevronDown className="w-4 h-4" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="bg-white border border-black text-black min-w-[150px]" align="start">
        <DropdownMenuItem 
          onClick={onAddRecipe} 
          className="cursor-pointer focus:bg-gray-100 text-black"
        >
          Add Recipe
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={onEditRecipe} 
          className="cursor-pointer focus:bg-gray-100 text-black"
        >
          Edit Recipe
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
