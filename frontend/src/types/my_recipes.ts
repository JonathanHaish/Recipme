export interface Recipe {
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
}

export interface MyRecipeRow {
  name: string;
  createdAt: string;
  updatedAt: string;
}


//temp mock django table
export const MOCK_DJANGO_RECIPES: Recipe[] = [
  {
    id: "r1",
    name: "Shakshuka",
    createdAt: "2025-12-01T10:00:00.000Z",
    updatedAt: "2026-01-02T12:30:00.000Z",
  },
  {
    id: "r2",
    name: "Pasta Pomodoro",
    createdAt: "2025-11-15T09:00:00.000Z",
    updatedAt: "2025-11-15T09:00:00.000Z",
  },
  {
    id: "r3",
    name: "Greek Salad",
    createdAt: "2026-01-05T18:10:00.000Z",
    updatedAt: "2026-01-06T08:10:00.000Z",
  },
];