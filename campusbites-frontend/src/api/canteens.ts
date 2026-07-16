import { apiRequest } from "./client";

export interface Canteen {
  id: number;
  name: string;
  location: string | null;
  is_active: boolean;
}

export function getCanteens(): Promise<Canteen[]> {
  return apiRequest<Canteen[]>("/canteens");
}