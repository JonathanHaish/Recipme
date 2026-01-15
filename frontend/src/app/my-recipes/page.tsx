import { MyRecipesClient } from "@/app/my-recipes-app/MyRecipesClient";
import { MOCK_DJANGO_RECIPES } from "@/types/my_recipes";

export default function MyRecipesPage() {
  const rows = MOCK_DJANGO_RECIPES.map((r) => ({
    name: r.name,
    createdAt: r.createdAt,
    updatedAt: r.updatedAt,
  }));

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        <MyRecipesClient rows={rows} />
      </div>
    </div>
  );
}