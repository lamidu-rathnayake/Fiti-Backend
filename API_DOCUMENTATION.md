# Fiti Backend — API Documentation

This document categorizes and details all the REST API endpoints available in the Fiti Backend platform.

> [!NOTE]
> All endpoints are prefixed with `/api/v1` (e.g., `/api/v1/auth/me/role`).

---

## 1. Authentication Gateway (`/auth`)

The centralized gateway for post-login redirection.

| Method | Endpoint | Auth Guard | Description |
|---|---|---|---|
| `GET` | `/auth/me/role` | Valid Token | Verifies user's Firebase token, checks role, and returns redirect URL (Client Dashboard, Seller Dashboard, Admin Console, or Onboarding). |

---

## 2. Profiles (`/profiles`)

Endpoints for managing user (Client and Tailor) profiles and body measurements.

| Method | Endpoint | Auth Guard | Description |
|---|---|---|---|
| `POST` | `/profiles/client` | Valid Token | Register a new client profile linked to the Firebase UID. |
| `GET` | `/profiles/client/{id}` | Client Role | Fetch a client's own profile. |
| `POST` | `/profiles/tailor` | Valid Token | Register a new tailor profile with NIC imagery. |
| `GET` | `/profiles/tailor/{id}` | Public | View a tailor's public profile. |
| `GET` | `/profiles/tailor/{id}/verification` | Public | Check if a tailor's profile has been verified by an admin. |
| `PUT` | `/profiles/client/{id}/measurements` | Client Role | Save or update a client's standard body measurements. |
| `GET` | `/profiles/client/{id}/measurements` | Client Role | Fetch a client's body measurements. |

---

## 3. Shops (`/shops`)

Endpoints for managing physical and online tailoring shops.

| Method | Endpoint | Auth Guard | Description |
|---|---|---|---|
| `GET` | `/shops/` | Public | List all shops, with optional pagination and city filters. |
| `GET` | `/shops/nearby` | Public | Discover tailor shops within a specified GPS radius (lat, lng, radius). |
| `GET` | `/shops/tailor/{tailor_id}` | Public | List all shops owned by a specific tailor. |
| `GET` | `/shops/{shop_id}` | Public | Get details of a specific shop by ID. |
| `POST` | `/shops/` | Tailor Role | Register a new tailor shop. |
| `PUT` | `/shops/{shop_id}` | Tailor Role | Update an existing shop's details. |
| `DELETE`| `/shops/{shop_id}` | Tailor Role | Delete a shop. |
| `POST` | `/shops/{shop_id}/images` | Tailor Role | Add a portfolio/shop image URL. |

---

## 4. Orders & Requests (`/orders`)

Endpoints for managing the entire fashion creation lifecycle: Requests → Bids → Orders → Payments → Ratings.

### Clothing Requests (Client's Need)
| Method | Endpoint | Auth Guard | Description |
|---|---|---|---|
| `POST` | `/orders/requests` | Client Role | Submit a new clothing request (marketplace broadcast). |
| `GET` | `/orders/requests/open` | Public | View all open marketplace requests (for tailors to browse). |
| `GET` | `/orders/requests/client/{id}` | Public | View all requests made by a specific client. |
| `GET` | `/orders/requests/{id}` | Public | Get details of a specific clothing request. |
| `PATCH`| `/orders/requests/{id}/cancel` | Client Role | Cancel an open request before a bid is accepted. |

### Bids & Shop Requests (Tailor's Offer)
| Method | Endpoint | Auth Guard | Description |
|---|---|---|---|
| `GET` | `/orders/shop-requests/shop/{id}` | Public | View all requests assigned to a specific shop. |
| `GET` | `/orders/shop-requests/{id}/bids` | Tailor Role | List all bids placed on a shop request. |
| `POST` | `/orders/bids` | Tailor Role | Submit a bid (price & message) on a client's request. |

### Orders & Payments (The Contract)
| Method | Endpoint | Auth Guard | Description |
|---|---|---|---|
| `POST` | `/orders/accept-bid` | Client Role | Accept a bid, finalizing the shop request into an active Order. |
| `GET` | `/orders/shop/{shop_id}` | Public | List all active/completed orders for a shop. |
| `GET` | `/orders/client/{client_id}`| Public | List all active/completed orders for a client. |
| `GET` | `/orders/{order_id}` | Valid Token | Get specific order details. |
| `PATCH`| `/orders/{order_id}/status` | Valid Token | Update order status (in_progress, completed). |
| `GET` | `/orders/{order_id}/payment`| Valid Token | Get the payment status of an order. |
| `POST` | `/orders/payments/mock` | Client Role | Process a mock simulated payment for an order. |
| `POST` | `/orders/ratings` | Client Role | Rate and review a shop upon order completion. |

---

## 5. Support & Engagement (`/support`)

Endpoints for user engagement and notifications.

| Method | Endpoint | Auth Guard | Description |
|---|---|---|---|
| `POST` | `/support/notifications` | Valid Token | Create a system notification for a user. |
| `GET` | `/support/notifications/{id}` | Valid Token | List a user's unread/recent notifications. |
| `PATCH`| `/support/notifications/{id}/read` | Valid Token | Mark a notification as read. |
| `POST` | `/support/favorites` | Valid Token | Add a shop to a client's favorites. |
| `DELETE`| `/support/favorites/{c_id}/{s_id}` | Valid Token | Remove a shop from a client's favorites. |
| `GET` | `/support/favorites/{id}` | Valid Token | View a client's favorite shops. |

---

## 6. RBAC (Role-Based Access Control) (`/rbac`)

Endpoints for viewing and assigning user permissions.

| Method | Endpoint | Auth Guard | Description |
|---|---|---|---|
| `POST` | `/rbac/assign-role` | Valid Token | Assign a role (`client`, `tailor`, `admin`) to a Firebase UID. |
| `GET` | `/rbac/users/{id}/access` | Public | View a user's assigned roles and accessible UI sections. |
| `GET` | `/rbac/users/{id}/check-route` | Public | Verify if a user is permitted to access a specific UI route. |

---

## 7. System Health (`/health`)

| Method | Endpoint | Auth Guard | Description |
|---|---|---|---|
| `GET` | `/health` | Public | Ping the server to check uptime, API version, and database connectivity. |
