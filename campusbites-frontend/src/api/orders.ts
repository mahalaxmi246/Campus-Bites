import { apiRequest } from "./client";

export interface OrderItem {
  menu_item_id: number;
  item_name_snapshot: string;
  price_snapshot: number;
  quantity: number;
  subtotal: number;
}

export interface Order {
  id: number;
  token_number: number;
  status: "placed" | "preparing" | "ready";
  subtotal: number;
  handling_fee: number;
  total_amount: number;
  created_at: string;
  items: OrderItem[];
}

export interface CreateOrderInput {
  canteen_id: number;
  items: { menu_item_id: number; quantity: number }[];
}

export function createOrder(data: CreateOrderInput, token: string): Promise<Order> {
  return apiRequest<Order>("/orders", { method: "POST", body: data, token });
}

export function getOrder(orderId: number, token: string): Promise<Order> {
  return apiRequest<Order>(`/orders/${orderId}`, { token });
}