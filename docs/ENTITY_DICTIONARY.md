# Fiti Backend Entity Dictionary

This document outlines the core entities and their required attributes for the Fiti Backend Application based on the database schema. It groups entities into their respective domains.

---

## 1. Profile & Identity Domain

### Firebase User Identity (Off-Database)
*Note: Full user identity is managed externally by Firebase Authentication. The PostgreSQL database only stores role-specific profile extensions linked by the Firebase UID (`id`).*
*   **`uid`** *(Primary Identifier)*: String (Maps to `id` in Postgres)
*   **`email`**: String
*   **`email_verified`**: Boolean
*   **`display_name`**: String (Full name)
*   **`phone_number`**: String
*   **`photo_url`**: String (Profile picture)
*   **`disabled`**: Boolean (Account status)
*   **`provider_data`**: Array (Linked authentication providers e.g. Google, Email/Password)

### Client
Represents a customer using the platform.
*   **`id`** *(Primary Key)*: String (Firebase Auth UID)
*   **`display_name`**: String (From JWT)
*   **`email`**: String (From JWT)
*   **`photo_url`**: String (From JWT)
*   **`phone`**: String
*   **`city`**: String
*   **`address`**: String
*   **`created_at`**: Timestamp
*   **`updated_at`**: Timestamp

### Tailor
Represents a tailor providing services on the platform.
*   **`id`** *(Primary Key)*: String (Firebase Auth UID)
*   **`display_name`**: String (From JWT)
*   **`email`**: String (From JWT)
*   **`photo_url`**: String (From JWT)
*   **`nic_front`**: String (Cloud storage URL for ID verification)
*   **`nic_rear`**: String (Cloud storage URL for ID verification)
*   **`is_verified`**: Boolean
*   **`phone`**: String
*   **`city`**: String
*   **`address`**: String
*   **`created_at`**: Timestamp
*   **`updated_at`**: Timestamp

### Measurement Profile
Stores the base measurements for a client.
*   **`measurement_id`** *(Primary Key)*: Integer
*   **`client_id`** *(Foreign Key)*: String (Ref: Client.id)
*   **`chest`**: Numeric
*   **`waist`**: Numeric
*   **`shoulder`**: Numeric
*   **`sleeve`**: Numeric
*   **`neck`**: Numeric
*   **`hip`**: Numeric
*   **`inseam`**: Numeric
*   **`length`**: Numeric
*   **`notes`**: Text
*   **`created_at`**: Timestamp
*   **`updated_at`**: Timestamp

---

## 2. Role-Based Access Control (RBAC) Domain

### Role
*   **`id`** *(Primary Key)*: Integer
*   **`name`**: String (e.g., 'client', 'tailor', 'admin')

### User Role
Mapping of users to their roles.
*   **`firebase_uid`** *(Composite PK)*: String
*   **`role_id`** *(Composite PK, Foreign Key)*: Integer (Ref: Role.id)

### Section
UI sections accessible to roles.
*   **`id`** *(Primary Key)*: Integer
*   **`name`**: String
*   **`route_name`**: String

### Role Section Grant
Permissions linking roles to UI sections.
*   **`role_id`** *(Composite PK, Foreign Key)*: Integer (Ref: Role.id)
*   **`section_id`** *(Composite PK, Foreign Key)*: Integer (Ref: Section.id)

### Sub Section
*   **`id`** *(Primary Key)*: Integer
*   **`name`**: String
*   **`component_id`**: String

### Section Sub Section
Mapping of sections to their sub-components.
*   **`section_id`** *(Composite PK, Foreign Key)*: Integer (Ref: Section.id)
*   **`sub_section_id`** *(Composite PK, Foreign Key)*: Integer (Ref: Sub Section.id)

---

## 3. Shop & Tailor Domain

### Shop
Represents a tailor's business profile.
*   **`shop_id`** *(Primary Key)*: Integer
*   **`tailor_id`** *(Foreign Key)*: String (Ref: Tailor.id)
*   **`shop_name`**: String
*   **`shop_bio`**: Text
*   **`shop_address`**: String
*   **`city`**: String
*   **`contact_number`**: String
*   **`registration_number`**: String
*   **`latitude`**: Numeric
*   **`longitude`**: Numeric
*   **`average_rating`**: Numeric
*   **`created_at`**: Timestamp
*   **`updated_at`**: Timestamp

### Shop Image
*   **`image_id`** *(Primary Key)*: Integer
*   **`shop_id`** *(Foreign Key)*: Integer (Ref: Shop.shop_id)
*   **`image_url`**: String (Cloud storage URL)
*   **`created_at`**: Timestamp

---

## 4. Order Flow & Marketplace Domain

### Clothing Request
A client's request for custom clothing.
*   **`request_id`** *(Primary Key)*: Integer
*   **`client_id`** *(Foreign Key)*: String (Ref: Client.id)
*   **`target_date`**: Date
*   **`target_budget`**: Numeric
*   **`clothing_category`**: String
*   **`gender`**: Enum ('male', 'female', 'other')
*   **`fabric_status`**: Enum ('client_provided', 'shop_provides')
*   **`description`**: Text
*   **`voice_note_url`**: String (Cloud storage URL)
*   **`service_type`**: Enum ('online', 'physical_visit')
*   **`request_location`**: String
*   **`status`**: Enum ('open', 'in_progress', 'completed', 'cancelled')
*   **`created_at`**: Timestamp
*   **`updated_at`**: Timestamp

### Clothing Request Image
Inspiration images for a request.
*   **`image_id`** *(Primary Key)*: Integer
*   **`request_id`** *(Foreign Key)*: Integer (Ref: Clothing Request.request_id)
*   **`image_url`**: String (Cloud storage URL)
*   **`created_at`**: Timestamp

### Measurement (Order Specific)
Measurements associated with a specific request.
*   **`measurement_id`** *(Primary Key)*: Integer
*   **`request_id`** *(Foreign Key)*: Integer (Ref: Clothing Request.request_id)
*   **`chest`**: Numeric
*   **`waist`**: Numeric
*   **`shoulder`**: Numeric
*   **`sleeve`**: Numeric
*   **`neck`**: Numeric
*   **`hip`**: Numeric
*   **`inseam`**: Numeric
*   **`length`**: Numeric
*   **`notes`**: Text
*   **`created_at`**: Timestamp
*   **`updated_at`**: Timestamp

### Shop Request
Tracks which shops received a request and their response status.
*   **`shop_request_id`** *(Primary Key)*: Integer
*   **`request_id`** *(Foreign Key)*: Integer (Ref: Clothing Request.request_id)
*   **`shop_id`** *(Foreign Key)*: Integer (Ref: Shop.shop_id)
*   **`offered_price`**: Numeric
*   **`status`**: Enum ('pending', 'quoted', 'accepted', 'rejected', 'withdrawn')
*   **`response_date`**: Timestamp
*   **`created_at`**: Timestamp
*   **`updated_at`**: Timestamp

### Bid
A specific price offer and message from a shop for a request.
*   **`bid_id`** *(Primary Key)*: Integer
*   **`shop_request_id`** *(Foreign Key)*: Integer (Ref: Shop Request.shop_request_id)
*   **`bid_amount`**: Numeric
*   **`message`**: Text
*   **`created_at`**: Timestamp

### Order
An accepted bid that becomes a confirmed order.
*   **`order_id`** *(Primary Key)*: Integer
*   **`shop_request_id`** *(Foreign Key)*: Integer (Ref: Shop Request.shop_request_id)
*   **`order_status`**: Enum ('in_progress', 'completed', 'cancelled')
*   **`accepted_price`**: Numeric
*   **`started_date`**: Date
*   **`completed_date`**: Date
*   **`created_at`**: Timestamp
*   **`updated_at`**: Timestamp

### Payment
Payment records for orders.
*   **`payment_id`** *(Primary Key)*: Integer
*   **`order_id`** *(Foreign Key)*: Integer (Ref: Order.order_id)
*   **`amount`**: Numeric
*   **`payment_method`**: Enum ('cash', 'card', 'bank_transfer', 'mobile_wallet')
*   **`payment_status`**: Enum ('pending', 'paid', 'failed', 'refunded')
*   **`payment_date`**: Timestamp
*   **`created_at`**: Timestamp

### Rating
Reviews left by clients for completed orders.
*   **`rating_id`** *(Primary Key)*: Integer
*   **`order_id`** *(Foreign Key)*: Integer (Ref: Order.order_id)
*   **`client_id`** *(Foreign Key)*: String (Ref: Client.id)
*   **`shop_id`** *(Foreign Key)*: Integer (Ref: Shop.shop_id)
*   **`rating`**: Small Integer (1-5)
*   **`review`**: Text
*   **`created_at`**: Timestamp

---

## 5. Support & Engagement Domain

### Favorite Shop
Client's bookmarked shops.
*   **`favorite_id`** *(Primary Key)*: Integer
*   **`client_id`** *(Foreign Key)*: String (Ref: Client.id)
*   **`shop_id`** *(Foreign Key)*: Integer (Ref: Shop.shop_id)
*   **`created_at`**: Timestamp

### Notification
Alerts sent to users (Firebase UI).
*   **`notification_id`** *(Primary Key)*: Integer
*   **`firebase_uid`**: String
*   **`title`**: String
*   **`message`**: Text
*   **`is_read`**: Boolean
*   **`created_at`**: Timestamp
