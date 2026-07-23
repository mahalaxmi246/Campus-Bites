import { useEffect, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { getCanteens } from "../api/canteens";
import { validateCart, type CartValidationResult } from "../api/cart";
import { ApiError } from "../api/client";
import { createOrder } from "../api/orders";
import { useAuth } from "../context/AuthContext";
import { useCartStore } from "../store/cartStore";

export function CheckoutPage() {
  const { isAuthenticated, accessToken } = useAuth();
  const navigate = useNavigate();
  const items = useCartStore((state) => state.items);
  const clearCart = useCartStore((state) => state.clearCart);

  const [validated, setValidated] = useState<CartValidationResult | null>(null);
  const [isValidating, setIsValidating] = useState(true);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isPlacingOrder, setIsPlacingOrder] = useState(false);
  const [placeOrderError, setPlaceOrderError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated || !accessToken || items.length === 0) {
      setIsValidating(false);
      return;
    }

    // NFR6, made visible: never trust the local cart's math for the amount
    // the student actually pays. Re-check current prices/availability with
    // the server before showing a final total — matches exactly what
    // POST /orders will independently re-verify at the moment of charge.
    let cancelled = false;
    setIsValidating(true);
    setValidationError(null);

    validateCart(
      items.map((i) => ({ menu_item_id: i.menuItemId, quantity: i.quantity })),
      accessToken
    )
      .then((result) => {
        if (!cancelled) setValidated(result);
      })
      .catch((err) => {
        if (!cancelled) {
          setValidationError(
            err instanceof ApiError
              ? err.message
              : "Couldn't confirm your order total. Please try again."
          );
        }
      })
      .finally(() => {
        if (!cancelled) setIsValidating(false);
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, accessToken]);

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

  async function handlePlaceOrder() {
    if (!accessToken) return;
    setPlaceOrderError(null);
    setIsPlacingOrder(true);
    try {
      const canteens = await getCanteens();
      if (canteens.length === 0) {
        throw new Error("No canteen is available right now.");
      }
      const order = await createOrder(
        {
          canteen_id: canteens[0].id,
          items: items.map((i) => ({ menu_item_id: i.menuItemId, quantity: i.quantity })),
        },
        accessToken
      );
      clearCart();
      navigate(`/orders/${order.id}/confirmation`);
    } catch (err) {
      setPlaceOrderError(
        err instanceof ApiError ? err.message : "Couldn't place your order. Please try again."
      );
    } finally {
      setIsPlacingOrder(false);
    }
  }

  return (
    <div className="checkout-page">
      <h1>Review Your Order</h1>
      <p className="cart-subheading">Confirm everything looks right before you order</p>

      {isValidating && <p className="menu-status">Confirming your order total...</p>}

      {validationError && (
        <div className="checkout-items">
          <p className="auth-error">{validationError}</p>
          <Link to="/cart" className="checkout-back-link">
            Back to cart
          </Link>
        </div>
      )}

      {validated && (
        <>
          <div className="checkout-items">
            {validated.items.map((item) => (
              <div key={item.menu_item_id} className="checkout-item">
                <span className="checkout-item-name">
                  {item.name} <span className="checkout-item-qty">x{item.quantity}</span>
                </span>
                <span>Rs.{item.line_subtotal}</span>
              </div>
            ))}
          </div>

          <div className="cart-summary">
            <div className="cart-summary-row">
              <span>Subtotal</span>
              <span>Rs.{validated.subtotal}</span>
            </div>
            <div className="cart-summary-row">
              <span>Handling fee</span>
              <span>Rs.{validated.handling_fee}</span>
            </div>
            <div className="cart-summary-row cart-summary-total">
              <span>Total</span>
              <span>Rs.{validated.total}</span>
            </div>

            {placeOrderError && <p className="auth-error">{placeOrderError}</p>}

            <button className="checkout-btn" onClick={handlePlaceOrder} disabled={isPlacingOrder}>
              {isPlacingOrder ? "Placing Order..." : "Place Order"}
            </button>
            <Link to="/cart" className="checkout-back-link">
              Back to cart
            </Link>
          </div>
        </>
      )}
    </div>
  );
}