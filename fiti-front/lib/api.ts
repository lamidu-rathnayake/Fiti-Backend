const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer mock_firebase_uid",
    ...options.headers,
  };

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errorDetail = "API Request Failed";
    try {
      const errJson = await res.json();
      errorDetail = errJson.detail || JSON.stringify(errJson);
    } catch {}
    throw new Error(errorDetail);
  }

  if (res.status === 204) {
    return {} as T;
  }

  return res.json();
}

// ── Types ─────────────────────────────────────────────────────────────

export interface ClientRegisterRequest {
  id?: string;
  name?: string;
  phone?: string;
}

export interface ClientResponse {
  id: string;
  created_at: string;
}

export interface SellerRegisterRequest {
  id?: string;
  nic_front?: string;
  nic_rear?: string;
}

export interface SellerResponse {
  id: string;
  created_at: string;
}

export interface ShopCreateRequest {
  seller_id: string;
  shop_name: string;
  shop_bio?: string;
  shop_address: string;
  city: string;
  contact_number?: string;
  registration_number?: string;
  latitude?: number;
  longitude?: number;
}

export interface ShopResponse {
  shop_id: number;
  seller_id: string;
  shop_name: string;
  shop_bio?: string;
  shop_address: string;
  city: string;
  contact_number?: string;
  registration_number?: string;
  latitude?: number;
  longitude?: number;
  average_rating: number;
  created_at: string;
}

export interface ClothingRequestCreateRequest {
  client_id: string;
  target_date: string;
  target_budget: number;
  clothing_category: string;
  gender?: string;
  fabric_status?: string;
  description?: string;
  voice_note_url?: string;
  service_type?: string;
  request_location?: string;
  target_shop_ids?: number[];
  design_image_urls?: string[];
}

export interface ClothingRequestResponse {
  request_id: number;
  client_id: string;
  target_date: string;
  target_budget: number;
  clothing_category: string;
  status: string;
  created_at: string;
}

export interface OrderResponse {
  order_id: number;
  bid_id: number;
  accepted_price: number;
  order_status: string;
  started_date?: string;
  completed_date?: string;
}

// ── API Functions ──────────────────────────────────────────────────────

export async function registerClient(data: ClientRegisterRequest): Promise<ClientResponse> {
  return request<ClientResponse>("/profiles/client", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function registerSeller(data: SellerRegisterRequest): Promise<SellerResponse> {
  return request<SellerResponse>("/profiles/seller", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function createShop(data: ShopCreateRequest): Promise<ShopResponse> {
  return request<ShopResponse>("/shops/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getShop(shopId: number): Promise<ShopResponse> {
  return request<ShopResponse>(`/shops/${shopId}`);
}

export async function listShopsBySeller(sellerId: string): Promise<ShopResponse[]> {
  return request<ShopResponse[]>(`/shops/seller/${sellerId}`);
}

export async function listNearbyShops(lat: number, lng: number, radiusKm: number = 10): Promise<ShopResponse[]> {
  return request<ShopResponse[]>(`/shops/nearby?lat=${lat}&lng=${lng}&radius_km=${radiusKm}`);
}

export async function createClothingRequest(data: ClothingRequestCreateRequest): Promise<ClothingRequestResponse> {
  return request<ClothingRequestResponse>("/orders/requests", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function listOrdersByClient(clientId: string): Promise<OrderResponse[]> {
  return request<OrderResponse[]>(`/orders/client/${clientId}`);
}

export async function listOrdersByShop(shopId: number): Promise<OrderResponse[]> {
  return request<OrderResponse[]>(`/orders/shop/${shopId}`);
}
