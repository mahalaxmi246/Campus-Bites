import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface CartItem {
  menuItemId: number;
  name: string;
  price: number;
  quantity: number;
}

interface CartState {
  items: CartItem[];
  addItem: (item: Omit<CartItem, "quantity">, quantity?: number) => void;
  removeItem: (menuItemId: number) => void;
  updateQuantity: (menuItemId: number, quantity: number) => void;
  clearCart: () => void;
}

export const useCartStore = create<CartState>()(
  persist(
    (set) => ({
      items: [],

      addItem: (item, quantity = 1) =>
        set((state) => {
          const existing = state.items.find((i) => i.menuItemId === item.menuItemId);
          if (existing) {
            // Already in cart — bump quantity rather than adding a duplicate row.
            return {
              items: state.items.map((i) =>
                i.menuItemId === item.menuItemId ? { ...i, quantity: i.quantity + quantity } : i
              ),
            };
          }
          return { items: [...state.items, { ...item, quantity }] };
        }),

      removeItem: (menuItemId) =>
        set((state) => ({
          items: state.items.filter((i) => i.menuItemId !== menuItemId),
        })),

      updateQuantity: (menuItemId, quantity) =>
        set((state) => {
          if (quantity <= 0) {
            // Dropping to 0 (or below) removes the line entirely — matches
            // how the "-" button should behave at quantity 1.
            return { items: state.items.filter((i) => i.menuItemId !== menuItemId) };
          }
          return {
            items: state.items.map((i) => (i.menuItemId === menuItemId ? { ...i, quantity } : i)),
          };
        }),

      clearCart: () => set({ items: [] }),
    }),
    {
      name: "campusbites_cart", // localStorage key
      // Only persist `items` — the action functions are recreated on every
      // load anyway and can't (shouldn't) be serialized into localStorage.
      partialize: (state) => ({ items: state.items }),
    }
  )
);

// Derived values are kept as plain functions, not store state — they're
// recomputed from `items` on every call, so they can never go stale the
// way a manually-maintained "subtotal" field in the store could.
export function selectSubtotal(items: CartItem[]): number {
  return items.reduce((sum, i) => sum + i.price * i.quantity, 0);
}

export function selectItemCount(items: CartItem[]): number {
  return items.reduce((sum, i) => sum + i.quantity, 0);
}