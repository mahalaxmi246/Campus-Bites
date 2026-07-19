import { Link, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { selectSubtotal, useCartStore } from "../store/cartStore";

export function CheckoutPage() {
  const { isAuthenticated } = useAuth();
  const items = useCartStore((state) => state.items);

  // Checkout requires login — browsing and cart don't (matches the
  // backend: GET /menu is public, but order placement will need a token).
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (items.length === 0) {
    return (
      <div className="checkout-page">
        <h1>Checkout</h1>
        <p className="menu-status">
          Your cart is empty. <Link to="/">Browse the menu</Link>
        </p>
      </div>
    );
  }

  const subtotal = selectSubtotal(items);

  return (
    <div className="checkout-page">
      <h1>Review Your Order</h1>
      <p className="cart-subheading">Confirm everything looks right before you pay</p>

      <div className="checkout-items">
        {items.map((item) => (
          <div key={item.menuItemId} className="checkout-item">
            <span className="checkout-item-name">
              {item.name} <span className="checkout-item-qty">x{item.quantity}</span>
            </span>
            <span>Rs.{item.price * item.quantity}</span>
          </div>
        ))}
      </div>

      <div className="cart-summary">
        <div className="cart-summary-row">
          <span>Subtotal</span>
          <span>Rs.{subtotal}</span>
        </div>
        <p className="cart-summary-note">
          Handling fee and final total will be confirmed on the payment step.
        </p>
        {/* Live price re-validation (POST /cart/validate) lands Day 5.
            Actual payment + order placement lands Week 5. */}
        <button className="checkout-btn" disabled>
          Continue to Payment
        </button>
        <Link to="/cart" className="checkout-back-link">
          Back to cart
        </Link>
      </div>
    </div>
  );
}