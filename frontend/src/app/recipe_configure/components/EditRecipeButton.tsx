import { Edit } from "lucide-react";

interface EditRecipeButtonProps {
  onClick: () => void;
}

export function EditRecipeButton({ onClick }: EditRecipeButtonProps) {
  return (
    <button
      onClick={onClick}
      className="px-4 py-2 border border-black rounded hover:bg-gray-100 text-black"
    >
      Edit Recipe
    </button>
  );
}
