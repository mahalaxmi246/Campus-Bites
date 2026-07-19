import { Link } from "react-router-dom";
import { selectSubtotal, useCartStore } from "../store/cartStore";

export function CartPage() {
  const items = useCartStore((state) => state.items);
  const updateQuantity = useCartStore((state) => state.updateQuantity);
  const removeItem = useCartStore((state) => state.removeItem);

  const subtotal = selectSubtotal(items);

  if (items.length === 0) {
    return (
      <div className="cart-page">
        <h1>Your Cart</h1>
        <p className="menu-status">
          Your cart is empty. <Link to="/">Browse the menu</Link>
        </p>
      </div>
    );
  }

  return (
    <div className="cart-page">
      <h1>Your Cart</h1>
      <p className="cart-subheading">Review your order before placing it</p>

      <div className="cart-items">
        {items.map((item) => (
          <div key={item.menuItemId} className="cart-item">
            <div>
              <h3>{item.name}</h3>
              <p className="cart-item-unit-price">Rs.{item.price} each</p>
            </div>
            <div className="qty-stepper">
              <button onClick={() => updateQuantity(item.menuItemId, item.quantity - 1)}>-</button>
              <span>{item.quantity}</span>
              <button onClick={() => updateQuantity(item.menuItemId, item.quantity + 1)}>+</button>
            </div>
            <span className="cart-item-line-total">Rs.{item.price * item.quantity}</span>
            <button className="cart-item-remove" onClick={() => removeItem(item.menuItemId)}>
              Remove
            </button>
          </div>
        ))}
      </div>

      <div className="cart-summary">
        <div className="cart-summary-row">
          <span>Subtotal</span>
          <span>Rs.{subtotal}</span>
        </div>
        <p className="cart-summary-note">
          Handling fee and final total are calculated at checkout.
        </p>
        {/* Checkout wiring (backend price validation, order placement) lands Week 4/5 */}
        <button className="checkout-btn" disabled>
          Proceed to Checkout
        </button>
      </div>
    </div>
  );
}