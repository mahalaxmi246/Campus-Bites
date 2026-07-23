import { useEffect, useState } from "react";
import { Link, Navigate, useParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { getOrder, type Order } from "../api/orders";
import { useAuth } from "../context/AuthContext";

const STATUS_LABELS: Record<Order["status"], string> = {
  placed: "Placed",
  preparing: "Preparing",
  ready: "Ready",
};

export function OrderConfirmationPage() {
  const { orderId } = useParams<{ orderId: string }>();
  const { isAuthenticated, accessToken } = useAuth();

  const [order, setOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!accessToken || !orderId) return;

    // Fetched fresh via GET /orders/{id} rather than passed through route
    // state on purpose — this page must work correctly on a hard refresh
    // too (exactly why that endpoint exists per its Week 5 Day 3 docstring).
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    getOrder(Number(orderId), accessToken)
      .then((data) => {
        if (!cancelled) setOrder(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(
            err instanceof ApiError ? err.message : "Couldn't load your order."
          );
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [orderId, accessToken]);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (isLoading) {
    return (
      <div className="confirmation-page">
        <p className="menu-status">Loading your order...</p>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="confirmation-page">
        <p className="menu-status menu-error">{error ?? "Order not found."}</p>
        <Link to="/">Back to menu</Link>
      </div>
    );
  }

  return (
    <div className="confirmation-page">
      <div className="confirmation-card">
        <div className="confirmation-check">✓</div>
        <h1>Order Placed Successfully!</h1>
        <p className="confirmation-subtext">Your food is being prepared</p>

        <div className="confirmation-token">
          <span className="confirmation-token-label">Your Token Number</span>
          <span className="confirmation-token-number">#{order.token_number}</span>
          <span className="confirmation-token-hint">Show this at the counter</span>
        </div>

        <div className="confirmation-details">
          <div className="confirmation-row">
            <span>Order ID</span>
            <span>#{order.id}</span>
          </div>
          <div className="confirmation-row">
            <span>Total Paid</span>
            <span>Rs.{order.total_amount}</span>
          </div>
          <div className="confirmation-row">
            <span>Status</span>
            <span className={`status-badge order-status-${order.status}`}>
              {STATUS_LABELS[order.status]}
            </span>
          </div>
        </div>

        <Link to="/" className="checkout-btn confirmation-order-more">
          Order More
        </Link>
      </div>
    </div>
  );
}