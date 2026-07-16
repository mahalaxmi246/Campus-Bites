import { useEffect, useState, type FormEvent } from "react";
import { ApiError } from "../api/client";
import { getCanteens, type Canteen } from "../api/canteens";
import {
  createMenuItem,
  deleteMenuItem,
  getMenu,
  updateMenuItem,
  type MenuItem,
} from "../api/menu";
import { useAuth } from "../context/AuthContext";

export function StaffMenuPage() {
  const { accessToken } = useAuth();

  const [items, setItems] = useState<MenuItem[]>([]);
  const [canteens, setCanteens] = useState<Canteen[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [category, setCategory] = useState("snacks");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function loadData() {
    setIsLoading(true);
    setError(null);
    try {
      // include_unavailable=true so staff can see (and re-enable) 86'd items —
      // the public menu page never shows these.
      const [menuData, canteenData] = await Promise.all([getMenu(undefined, true), getCanteens()]);
      setItems(menuData);
      setCanteens(canteenData);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't load menu data.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    if (!accessToken) return;
    if (canteens.length === 0) {
      setFormError("No canteen exists yet — seed one first.");
      return;
    }

    setFormError(null);
    setIsSubmitting(true);
    try {
      await createMenuItem(
        {
          canteen_id: canteens[0].id,
          name,
          description: description || undefined,
          price: Number(price),
          category,
        },
        accessToken
      );
      setName("");
      setDescription("");
      setPrice("");
      await loadData();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Couldn't create item.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleToggleAvailability(item: MenuItem) {
    if (!accessToken) return;
    try {
      await updateMenuItem(item.id, { is_available: !item.is_available }, accessToken);
      await loadData();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't update item.");
    }
  }

  async function handleDelete(item: MenuItem) {
    if (!accessToken) return;
    if (!window.confirm(`Remove "${item.name}" from the menu?`)) return;
    try {
      await deleteMenuItem(item.id, accessToken);
      await loadData();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't delete item.");
    }
  }

  return (
    <div className="staff-menu-page">
      <h1>Manage Menu</h1>

      <form onSubmit={handleCreate} className="staff-menu-form">
        <h2>Add Item</h2>
        {formError && <p className="auth-error">{formError}</p>}

        <div className="form-row">
          <input
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <input
            placeholder="Price"
            type="number"
            min="0.01"
            step="0.01"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            required
          />
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="snacks">Snacks</option>
            <option value="meals">Meals</option>
            <option value="drinks">Drinks</option>
          </select>
        </div>

        <input
          placeholder="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Adding..." : "Add Item"}
        </button>
      </form>

      {isLoading && <p className="menu-status">Loading...</p>}
      {error && <p className="menu-status menu-error">{error}</p>}

      {!isLoading && !error && (
        <table className="staff-menu-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Category</th>
              <th>Price</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.name}</td>
                <td>{item.category}</td>
                <td>Rs.{item.price}</td>
                <td>
                  <span
                    className={item.is_available ? "status-badge available" : "status-badge unavailable"}
                  >
                    {item.is_available ? "Available" : "Unavailable"}
                  </span>
                </td>
                <td className="staff-menu-actions">
                  <button onClick={() => handleToggleAvailability(item)}>
                    {item.is_available ? "Mark Unavailable" : "Mark Available"}
                  </button>
                  <button className="danger" onClick={() => handleDelete(item)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}