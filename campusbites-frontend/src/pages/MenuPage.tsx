import { useEffect, useState } from "react";
import { ApiError } from "../api/client";
import { getMenu, type MenuItem } from "../api/menu";

const CATEGORIES = [
  { value: "all", label: "All" },
  { value: "snacks", label: "Snacks" },
  { value: "meals", label: "Meals" },
  { value: "drinks", label: "Drinks" },
];

export function MenuPage() {
  const [activeCategory, setActiveCategory] = useState("all");
  const [items, setItems] = useState<MenuItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Guards against a race: if the user switches categories again before
    // the previous fetch resolves, that stale response must not overwrite
    // the newer one that (maybe) already landed.
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    getMenu(activeCategory)
      .then((data) => {
        if (!cancelled) setItems(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(
            err instanceof ApiError ? err.message : "Couldn't load the menu. Please try again."
          );
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [activeCategory]);

  return (
    <div className="menu-page">
      <div className="menu-header">
        <h1>Our Menu</h1>
        <p>Fresh, hot and ready for you!</p>
      </div>

      <div className="category-tabs">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.value}
            className={cat.value === activeCategory ? "category-tab active" : "category-tab"}
            onClick={() => setActiveCategory(cat.value)}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {isLoading && <p className="menu-status">Loading menu...</p>}
      {error && <p className="menu-status menu-error">{error}</p>}
      {!isLoading && !error && items.length === 0 && (
        <p className="menu-status">No items in this category yet.</p>
      )}

      <div className="menu-grid">
        {items.map((item) => (
          <div key={item.id} className="menu-card">
            <h3>{item.name}</h3>
            {item.description && <p className="menu-card-desc">{item.description}</p>}
            <div className="menu-card-footer">
              <span className="menu-card-price">Rs.{item.price}</span>
              {/* Add-to-cart button lands Week 4 */}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}