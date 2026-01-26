export function RecipeCardSkeleton() {
  return (
    <div className="bg-white border-2 border-black rounded-lg overflow-hidden shadow-lg animate-pulse">
      {/* Image skeleton */}
      <div className="w-full h-48 bg-gray-300" />

      <div className="p-4 space-y-3">
        {/* Title skeleton */}
        <div className="h-6 bg-gray-300 rounded w-3/4" />

        {/* Type skeleton */}
        <div className="h-4 bg-gray-200 rounded w-1/2" />

        {/* Ingredients skeleton */}
        <div className="space-y-2 pt-2">
          <div className="h-3 bg-gray-200 rounded w-full" />
          <div className="h-3 bg-gray-200 rounded w-5/6" />
          <div className="h-3 bg-gray-200 rounded w-4/6" />
        </div>

        {/* Actions skeleton */}
        <div className="flex gap-2 pt-2">
          <div className="h-8 bg-gray-300 rounded flex-1" />
          <div className="h-8 bg-gray-300 rounded w-8" />
          <div className="h-8 bg-gray-300 rounded w-8" />
        </div>
      </div>
    </div>
  );
}
