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

export interface MenuItemCreateInput {
  canteen_id: number;
  name: string;
  description?: string;
  price: number;
  category: string;
}

export interface MenuItemUpdateInput {
  name?: string;
  description?: string;
  price?: number;
  category?: string;
  is_available?: boolean;
}

export function getMenu(category?: string, includeUnavailable = false): Promise<MenuItem[]> {
  const params = new URLSearchParams();
  if (category && category !== "all") {
    params.set("category", category);
  }
  if (includeUnavailable) {
    params.set("include_unavailable", "true");
  }
  const query = params.toString();
  return apiRequest<MenuItem[]>(`/menu${query ? `?${query}` : ""}`);
}

export function createMenuItem(data: MenuItemCreateInput, token: string): Promise<MenuItem> {
  return apiRequest<MenuItem>("/menu", { method: "POST", body: data, token });
}

export function updateMenuItem(
  id: number,
  data: MenuItemUpdateInput,
  token: string
): Promise<MenuItem> {
  return apiRequest<MenuItem>(`/menu/${id}`, { method: "PUT", body: data, token });
}

export function deleteMenuItem(id: number, token: string): Promise<void> {
  return apiRequest<void>(`/menu/${id}`, { method: "DELETE", token });
}