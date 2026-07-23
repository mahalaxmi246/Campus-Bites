import { apiRequest } from "./client";

export interface ValidatedCartItem {
  menu_item_id: number;
  name: string;
  price: number;
  quantity: number;
  line_subtotal: number;
}

export interface CartValidationResult {
  items: ValidatedCartItem[];
  subtotal: number;
  handling_fee: number;
  total: number;
}

export function validateCart(
  items: { menu_item_id: number; quantity: number }[],
  token: string
): Promise<CartValidationResult> {
  return apiRequest<CartValidationResult>("/cart/validate", {
    method: "POST",
    body: { items },
    token,
  });
}