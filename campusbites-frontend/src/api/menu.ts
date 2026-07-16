import { apiRequest } from "./client";

export interface MenuItem {
  id: number;
  canteen_id: number;
  name: string;
  description: string | null;
  price: number;
  category: string;
  is_available: boolean;
}

export function getMenu(category?: string): Promise<MenuItem[]> {
  const params = new URLSearchParams();
  if (category && category !== "all") {
    params.set("category", category);
  }
  const query = params.toString();
  return apiRequest<MenuItem[]>(`/menu${query ? `?${query}` : ""}`);
}