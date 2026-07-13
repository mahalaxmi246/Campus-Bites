---

##  API Contract — Phase 1 scope (FR1–FR13)

Base path: `/api/v1`. All request/response bodies are JSON. Auth via `Authorization: Bearer <access_token>` header unless marked public.

### Auth

| Method | Path | Auth | Request body | Response | Notes |
|---|---|---|---|---|---|
| POST | `/auth/register` | Public | `{full_name, username, email, password}` | `201 {id, username, email, role}` | FR1. Password hashed server-side, never returned. |
| POST | `/auth/login` | Public | `{username, password}` | `200 {access_token, refresh_token, token_type}` | FR2. |
| POST | `/auth/refresh` | Public (refresh token in body) | `{refresh_token}` | `200 {access_token}` | FR2. Rotate refresh token if you implement rotation. |
| POST | `/auth/logout` | Bearer | — | `204` | Invalidate/blacklist refresh token server-side. |

### Users

| Method | Path | Auth | Response | Notes |
|---|---|---|---|---|
| GET | `/users/me` | Bearer | `{id, full_name, username, email, role, created_at, total_orders, total_spent}` | FR11. `total_orders`/`total_spent` computed via aggregate query, not stored redundantly. |

### Canteens

| Method | Path | Auth | Response | Notes |
|---|---|---|---|---|
| GET | `/canteens` | Public | `[{id, name, location, is_active}]` | Minimal in Phase 1 (likely one seeded canteen); full selection UX lands in Phase 3. |

### Menu

| Method | Path | Auth | Request body | Response | Notes |
|---|---|---|---|---|---|
| GET | `/menu?canteen_id=&category=` | Public | — | `[{id, name, description, price, category, is_available}]` | FR5. Query params optional; no filter = all items. |
| POST | `/menu` | Bearer (staff/admin) | `{canteen_id, name, description, price, category}` | `201 {...item}` | FR4. |
| PUT | `/menu/{item_id}` | Bearer (staff/admin) | `{name?, description?, price?, category?, is_available?}` | `200 {...item}` | FR4. Partial update. |
| DELETE | `/menu/{item_id}` | Bearer (staff/admin) | — | `204` | FR4. Consider soft-delete (`is_available=false`) instead of hard delete to preserve order_items history integrity. |

### Cart validation

| Method | Path | Auth | Request body | Response | Notes |
|---|---|---|---|---|---|
| POST | `/cart/validate` | Bearer | `{items: [{menu_item_id, quantity}]}` | `200 {items: [...with live price], subtotal, handling_fee, total}` | NFR6. Called before checkout render so the user sees server-truth pricing, not just their local cart math. |

### Orders

| Method | Path | Auth | Request body | Response | Notes |
|---|---|---|---|---|---|
| POST | `/orders` | Bearer (student) | `{canteen_id, items: [{menu_item_id, quantity}]}` | `201 {id, token_number, status, total_amount, created_at}` | FR7, FR8. Wrapped in a DB transaction (NFR3): validates prices server-side, creates order + order_items atomically. |
| GET | `/orders/me` | Bearer (student) | — | `[{id, token_number, status, total_amount, created_at, items: [...]}]` | FR10. Paginated if list grows (`?page=&limit=`). |
| GET | `/orders/{order_id}` | Bearer (owner or staff/admin) | — | `{id, token_number, status, items: [...], total_amount, created_at}` | Used for the confirmation/status screen. |
| PATCH | `/orders/{order_id}/status` | Bearer (staff/admin) | `{status}` | `200 {id, status}` | FR12. Validates status is a legal value (Placed→Preparing→Ready only in Phase 1; full lifecycle expansion is Phase 3). |

### WebSocket (real-time)

| Path | Auth | Direction | Payload | Notes |
|---|---|---|---|---|
| `WS /ws/orders?token=<access_token>` | Bearer (as query param, since WS can't send headers easily) | Server → client | `{order_id, status, token_number}` | FR9. Student subscribes on the order status page; receives a push whenever their order's status changes. |
| `WS /ws/staff/{canteen_id}?token=<access_token>` | Bearer (staff/admin) | Server → client | `{order_id, status, token_number, total_amount}` | FR9/FR12. Staff dashboard subscribes to all order events for their canteen. |

### Admin

| Method | Path | Auth | Response | Notes |
|---|---|---|---|---|
| GET | `/admin/stats` | Bearer (admin) | `{total_orders, placed, preparing, ready}` | FR13. Aggregate counts, likely `SELECT status, COUNT(*) GROUP BY status`. |

### Error response shape (apply consistently from Day 1, even though it's formally an NFR7/FR15 item in Phase 2)

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Username or password is incorrect"
  }
}
```