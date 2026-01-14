import { Plus } from "lucide-react";

interface CreateRecipeButtonProps {
  onClick: () => void;
}

export function CreateRecipeButton({ onClick }: CreateRecipeButtonProps) {
  return (
    <button
      onClick={onClick}
      className="px-4 py-2 border border-black rounded hover:bg-gray-100 text-black"
    >
      Add Recipe
    </button>
  );
}
