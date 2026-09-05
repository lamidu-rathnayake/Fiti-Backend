import pytest

from app.domain.entities.order import (
    Bid,
    ClothingRequest,
    ClothingRequestImage,
    Order,
    Payment,
    Rating,
    ShopRequest,
    ShopRequestStatusEnum,
)
from app.domain.entities.rbac import (
    Role,
    Section,
    UserRole,
)
from app.domain.entities.shop import Shop, ShopImage
from app.domain.entities.support import FavoriteShop, Notification
from app.domain.entities.user import Client, Tailor
from app.domain.exceptions.rbac import AccessDeniedError
from app.domain.exceptions.user import ProfileAlreadyExistsError
from app.domain.repositories.notification_repository import (
    AbstractFavoriteShopRepository,
    AbstractNotificationRepository,
)
from app.domain.repositories.order_repository import AbstractOrderRepository
from app.domain.repositories.profile_repository import (
    AbstractClientRepository,
    AbstractMeasurementProfileRepository,
    AbstractTailorRepository,
)
from app.domain.repositories.rbac_repository import AbstractRBACRepository
from app.domain.repositories.shop_repository import AbstractShopRepository
from app.use_cases.dtos.order_dto import (
    BidCreateDTO,
    ClothingRequestCreateDTO,
    OrderCreateDTO,
    RatingCreateDTO,
)
from app.use_cases.dtos.rbac_dto import RoleAssignDTO
from app.use_cases.dtos.shop_dto import ShopCreateDTO, ShopUpdateDTO
from app.use_cases.dtos.support_dto import FavoriteShopCreateDTO, NotificationCreateDTO
from app.use_cases.dtos.user_dto import ClientRegisterDTO, TailorRegisterDTO
from app.use_cases.order.manage_order import ManageOrderUseCase
from app.use_cases.rbac.manage_rbac import ManageRBACUseCase
from app.use_cases.shop.manage_shop import ManageShopUseCase
from app.use_cases.support.manage_support import ManageSupportUseCase
from app.use_cases.user.manage_profile import ManageProfileUseCase

# ── Profile Mocks ─────────────────────────────────────────────────────────────


class InMemoryClientRepository(AbstractClientRepository):
    def __init__(self):
        self._store: dict[str, Client] = {}

    async def create(self, client: Client) -> Client:
        self._store[client.id] = client
        return client

    async def get_by_id(self, client_id: str) -> Client | None:
        return self._store.get(client_id)

    async def update(self, client: Client) -> Client:
        self._store[client.id] = client
        return client


class InMemoryTailorRepository(AbstractTailorRepository):
    def __init__(self):
        self._store: dict[str, Tailor] = {}

    async def create(self, tailor: Tailor) -> Tailor:
        self._store[tailor.id] = tailor
        return tailor

    async def get_by_id(self, tailor_id: str) -> Tailor | None:
        return self._store.get(tailor_id)

    async def update_verification(self, tailor_id: str, is_verified: bool) -> Tailor:
        tailor = self._store[tailor_id]
        tailor.is_verified = is_verified
        return tailor

    async def update(self, tailor: Tailor) -> Tailor:
        self._store[tailor.id] = tailor
        return tailor


class InMemoryMeasurementRepository(AbstractMeasurementProfileRepository):
    def __init__(self):
        self._store = {}

    async def create(self, profile):
        self._store[profile.client_id] = profile
        return profile

    async def get_by_client_id(self, client_id: str):
        return self._store.get(client_id)

    async def update(self, profile):
        self._store[profile.client_id] = profile
        return profile


# ── Shop Mocks ────────────────────────────────────────────────────────────────


class InMemoryShopRepository(AbstractShopRepository):
    def __init__(self):
        self._store: dict[int, Shop] = {}
        self._next_id = 1

    async def create(self, shop: Shop) -> Shop:
        shop.shop_id = self._next_id
        self._next_id += 1
        self._store[shop.shop_id] = shop
        return shop

    async def get_by_id(self, shop_id: int) -> Shop | None:
        return self._store.get(shop_id)

    async def get_by_tailor_id(self, tailor_id: str) -> list[Shop]:
        return [s for s in self._store.values() if s.tailor_id == tailor_id]

    async def list_all(
        self, skip: int = 0, limit: int = 100, city: str | None = None
    ) -> list[Shop]:
        shops = list(self._store.values())
        if city:
            shops = [s for s in shops if s.city == city]
        return shops[skip : skip + limit]

    async def add_image(self, image: ShopImage) -> ShopImage:
        image.image_id = 1
        shop = self._store[image.shop_id]
        shop.images.append(image)
        return image

    async def update_average_rating(self, shop_id: int, new_rating: float) -> None:
        if shop_id in self._store:
            self._store[shop_id].average_rating = new_rating

    async def update_shop(self, shop: Shop) -> Shop:
        self._store[shop.shop_id] = shop
        return shop

    async def delete_shop(self, shop_id: int) -> bool:
        if shop_id in self._store:
            del self._store[shop_id]
            return True
        return False

    async def search_near_location(
        self, lat: float, lng: float, radius_km: float = 10.0
    ) -> list[Shop]:
        # Dumb mock: just return everything
        return list(self._store.values())


# ── RBAC Mocks ────────────────────────────────────────────────────────────────


class InMemoryRBACRepository(AbstractRBACRepository):
    def __init__(self):
        self.roles = {"client": Role(id=1, name="client")}
        self.user_roles = {}
        self.sections = {
            "/client/dashboard": Section(
                id=1, name="Dashboard", route_name="/client/dashboard"
            )
        }
        self.grants = [(1, 1)]  # Role 1 has access to Section 1

    async def get_role_by_name(self, name: str) -> Role | None:
        return self.roles.get(name)

    async def assign_role_to_user(self, user_id: str, role_id: int) -> None:
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        self.user_roles[user_id].append(UserRole(user_id=user_id, role_id=role_id))

    async def get_user_roles(self, user_id: str) -> list[Role]:
        roles = []
        for ur in self.user_roles.get(user_id, []):
            for r in self.roles.values():
                if r.id == ur.role_id:
                    roles.append(r)
        return roles

    async def check_user_access_to_route(self, user_id: str, route_name: str) -> bool:
        user_role_ids = [ur.role_id for ur in self.user_roles.get(user_id, [])]
        sec_id = None
        for s in self.sections.values():
            if s.route_name == route_name:
                sec_id = s.id
                break
        if not sec_id:
            return False
        return any((r_id, sec_id) in self.grants for r_id in user_role_ids)

    async def get_accessible_sections_for_user(self, user_id: str) -> list[Section]:
        user_role_ids = [ur.role_id for ur in self.user_roles.get(user_id, [])]
        access_sec_ids = [
            sec_id for (r_id, sec_id) in self.grants if r_id in user_role_ids
        ]
        return [s for s in self.sections.values() if s.id in access_sec_ids]

    async def check_user_access_to_component(
        self, user_id: str, component_id: str
    ) -> bool:
        return True


# ── Order Mocks ───────────────────────────────────────────────────────────────


class InMemoryOrderRepository(AbstractOrderRepository):
    def __init__(self):
        self._reqs = {}
        self._shop_reqs = {}
        self._bids = {}
        self._orders = {}
        self._payments = {}
        self._ratings = {}
        self._id = 1

    def _next(self):
        val = self._id
        self._id += 1
        return val

    async def create_clothing_request(self, req: ClothingRequest) -> ClothingRequest:
        req.request_id = self._next()
        self._reqs[req.request_id] = req
        return req

    async def get_clothing_request(self, request_id: int) -> ClothingRequest | None:
        return self._reqs.get(request_id)

    async def list_clothing_requests_by_client(
        self, client_id: str
    ) -> list[ClothingRequest]:
        return [r for r in self._reqs.values() if r.client_id == client_id]

    async def list_open_clothing_requests(
        self, skip: int = 0, limit: int = 100
    ) -> list[ClothingRequest]:
        return list(self._reqs.values())[skip : skip + limit]

    async def add_design_image(
        self, image: ClothingRequestImage
    ) -> ClothingRequestImage:
        image.image_id = self._next()
        self._reqs[image.request_id].design_images.append(image)
        return image

    async def create_shop_request(self, sr: ShopRequest) -> ShopRequest:
        sr.shop_request_id = self._next()
        self._shop_reqs[sr.shop_request_id] = sr
        self._reqs[sr.request_id].shop_requests.append(sr)
        return sr

    async def get_shop_request(self, sr_id: int) -> ShopRequest | None:
        return self._shop_reqs.get(sr_id)

    async def list_shop_requests_by_shop(self, shop_id: int) -> list[ShopRequest]:
        return [sr for sr in self._shop_reqs.values() if sr.shop_id == shop_id]

    async def create_bid(self, bid: Bid) -> Bid:
        bid.bid_id = self._next()
        self._bids[bid.bid_id] = bid
        sr = self._shop_reqs.get(bid.shop_request_id)
        if sr:
            sr.bids.append(bid)
            sr.offered_price = bid.bid_amount
            sr.status = ShopRequestStatusEnum.QUOTED
        return bid

    async def create_order(self, order: Order) -> Order:
        order.order_id = self._next()
        self._orders[order.order_id] = order
        return order

    async def get_order(self, order_id: int) -> Order | None:
        return self._orders.get(order_id)

    async def update_order_status(self, order_id: int, new_status: str) -> Order:
        self._orders[order_id].order_status = new_status
        return self._orders[order_id]

    async def list_orders_by_shop(self, shop_id: int) -> list[Order]:
        res = []
        for o in self._orders.values():
            sr = self._shop_reqs.get(o.shop_request_id)
            if sr and sr.shop_id == shop_id:
                res.append(o)
        return res

    async def list_orders_by_client(self, client_id: str) -> list[Order]:
        res = []
        for o in self._orders.values():
            sr = self._shop_reqs.get(o.shop_request_id)
            req = self._reqs.get(sr.request_id) if sr else None
            if req and req.client_id == client_id:
                res.append(o)
        return res

    async def create_payment(self, payment: Payment) -> Payment:
        payment.payment_id = self._next()
        self._payments[payment.payment_id] = payment
        return payment

    async def get_payment(self, payment_id: int) -> Payment | None:
        return self._payments.get(payment_id)

    async def create_rating(self, rating: Rating) -> Rating:
        rating.rating_id = self._next()
        self._ratings[rating.rating_id] = rating
        return rating

    async def get_ratings_by_shop(self, shop_id: int) -> list[Rating]:
        return [r for r in self._ratings.values() if r.shop_id == shop_id]

    async def cancel_clothing_request(self, request_id: int) -> ClothingRequest | None:
        req = self._reqs.get(request_id)
        if req:
            req.status = "cancelled"
        return req

    async def get_payment_by_order(self, order_id: int) -> Payment | None:
        for p in self._payments.values():
            if p.order_id == order_id:
                return p
        return None

    async def list_bids_by_shop_request(self, shop_request_id: int) -> list[Bid]:
        return [b for b in self._bids.values() if b.shop_request_id == shop_request_id]


# ── Support Mocks ─────────────────────────────────────────────────────────────


class InMemoryNotificationRepository(AbstractNotificationRepository):
    def __init__(self):
        self._store = {}
        self._id = 1

    async def create_notification(self, n: Notification) -> Notification:
        n.notification_id = self._id
        self._id += 1
        self._store[n.notification_id] = n
        return n

    async def list_by_user(self, user_id: str) -> list[Notification]:
        return [n for n in self._store.values() if n.user_id == user_id]

    async def mark_read(self, n_id: int) -> bool:
        if n_id in self._store:
            self._store[n_id].is_read = True
            return True
        return False


class InMemoryFavoriteShopRepository(AbstractFavoriteShopRepository):
    def __init__(self):
        self._store = {}
        self._id = 1

    async def add_favorite(self, fav: FavoriteShop) -> FavoriteShop:
        fav.favorite_id = self._id
        self._id += 1
        self._store[fav.favorite_id] = fav
        return fav

    async def remove_favorite(self, client_id: str, shop_id: int) -> bool:
        to_del = [
            k
            for k, v in self._store.items()
            if v.client_id == client_id and v.shop_id == shop_id
        ]
        for k in to_del:
            del self._store[k]
        return len(to_del) > 0

    async def list_favorites_by_client(self, client_id: str) -> list[FavoriteShop]:
        return [f for f in self._store.values() if f.client_id == client_id]


# ── Tests ─────────────────────────────────────────────────────────────────────


def make_profile_use_case():
    return ManageProfileUseCase(
        client_repository=InMemoryClientRepository(),
        tailor_repository=InMemoryTailorRepository(),
        measurement_repository=InMemoryMeasurementRepository(),
    )


def make_shop_use_case():
    return ManageShopUseCase(shop_repository=InMemoryShopRepository())


def make_rbac_use_case():
    return ManageRBACUseCase(rbac_repository=InMemoryRBACRepository())


def make_order_use_case(shop_repo=None):
    if not shop_repo:
        shop_repo = InMemoryShopRepository()
    return ManageOrderUseCase(
        order_repository=InMemoryOrderRepository(), shop_repository=shop_repo
    )


def make_support_use_case():
    return ManageSupportUseCase(
        notification_repository=InMemoryNotificationRepository(),
        favorite_shop_repository=InMemoryFavoriteShopRepository(),
    )


# PROFILE TESTS
@pytest.mark.asyncio
async def test_register_client_profile():
    use_case = make_profile_use_case()
    result = await use_case.register_client(ClientRegisterDTO(id="client_1"))
    assert result.id == "client_1"


@pytest.mark.asyncio
async def test_register_client_duplicate_raises_error():
    use_case = make_profile_use_case()
    await use_case.register_client(ClientRegisterDTO(id="client_1"))
    with pytest.raises(ProfileAlreadyExistsError):
        await use_case.register_client(ClientRegisterDTO(id="client_1"))


@pytest.mark.asyncio
async def test_register_tailor_profile():
    use_case = make_profile_use_case()
    result = await use_case.register_tailor(
        TailorRegisterDTO(id="tailor_1", nic_front="front.jpg")
    )
    assert result.id == "tailor_1"
    assert result.is_verified is False


# SHOP TESTS
@pytest.mark.asyncio
async def test_shop_crud_operations():
    uc = make_shop_use_case()
    # Create
    shop = await uc.create_shop(
        ShopCreateDTO(tailor_id="tailor_1", shop_name="Test Shop", city="Kandy")
    )
    assert shop.shop_id == 1

    # Read
    fetched = await uc.get_shop_by_id(1)
    assert fetched.shop_name == "Test Shop"

    # Update
    updated = await uc.update_shop(
        ShopUpdateDTO(shop_id=1, shop_name="Updated Shop", city="Kandy")
    )
    assert updated.shop_name == "Updated Shop"

    # List
    shops = await uc.get_shops_by_tailor("tailor_1")
    assert len(shops) == 1

    # Delete
    assert await uc.delete_shop(1) is True


# RBAC TESTS
@pytest.mark.asyncio
async def test_rbac_operations():
    uc = make_rbac_use_case()
    await uc.assign_role(RoleAssignDTO(user_id="user_1", role_name="client"))

    overview = await uc.get_user_access_overview("user_1")
    assert "client" in overview.roles
    assert len(overview.accessible_sections) == 1

    access = await uc.verify_user_route_access("user_1", "/client/dashboard")
    assert access is True

    with pytest.raises(AccessDeniedError):
        await uc.verify_user_route_access("user_1", "/admin/dashboard")


# ORDER TESTS
@pytest.mark.asyncio
async def test_order_workflow_and_rating_recalc():
    shop_repo = InMemoryShopRepository()
    await shop_repo.create(
        Shop(tailor_id="tailor_1", shop_name="Tailor", city="Colombo", shop_id=1)
    )

    uc = make_order_use_case(shop_repo=shop_repo)

    # 1. Create request
    req = await uc.create_clothing_request(
        ClothingRequestCreateDTO(
            client_id="client_1", clothing_category="Suit", target_budget=100.0
        ),
        target_shop_ids=[1],
    )
    assert req.request_id == 1
    shop_req_id = req.shop_requests[0].shop_request_id

    # 2. Bid
    bid = await uc.submit_bid(
        BidCreateDTO(shop_request_id=shop_req_id, bid_amount=120.0)
    )

    # 3. Accept Bid -> Order
    order = await uc.accept_bid_and_create_order(
        OrderCreateDTO(shop_request_id=shop_req_id, accepted_price=120.0)
    )
    assert order.order_status == "in_progress"

    # 4. Rate (should recalc average rating)
    rating = await uc.submit_rating(
        RatingCreateDTO(
            order_id=order.order_id, client_id="client_1", shop_id=1, rating=4
        )
    )
    assert rating.rating == 4

    shop = await shop_repo.get_by_id(1)
    assert shop.average_rating == 4.0


@pytest.mark.asyncio
async def test_direct_order_workflow_without_bids():
    shop_repo = InMemoryShopRepository()
    await shop_repo.create(
        Shop(tailor_id="tailor_2", shop_name="Direct Tailor", city="Kandy", shop_id=2)
    )

    uc = make_order_use_case(shop_repo=shop_repo)

    # 1. Create request directly targeting the shop (no broadcast)
    req = await uc.create_clothing_request(
        ClothingRequestCreateDTO(
            client_id="client_2", clothing_category="Dress", target_budget=200.0
        ),
        target_shop_ids=[2],
    )
    assert req.request_id == 1
    shop_req_id = req.shop_requests[0].shop_request_id

    # 2. Skip the Bid phase entirely! (Client and tailor negotiated offline/chat)

    # 3. Create Order directly from the shop request
    order = await uc.accept_bid_and_create_order(
        OrderCreateDTO(shop_request_id=shop_req_id, accepted_price=180.0)
    )

    # Assertions
    assert order.order_status == "in_progress"
    assert order.accepted_price == 180.0

    # Verify the order exists and is tied to the shop correctly
    shop_orders = await uc.list_orders_by_shop(2)
    assert len(shop_orders) == 1
    assert shop_orders[0].accepted_price == 180.0


# SUPPORT TESTS
@pytest.mark.asyncio
async def test_support_operations():
    uc = make_support_use_case()

    # Notifications
    n = await uc.create_notification(
        NotificationCreateDTO(user_id="user_1", title="Hello", message="Test")
    )
    assert n.is_read is False

    await uc.mark_notification_read(n.notification_id)
    notifications = await uc.list_notifications("user_1")
    assert notifications[0].is_read is True

    # Favorites
    fav = await uc.add_favorite(FavoriteShopCreateDTO(client_id="user_1", shop_id=10))

    favs = await uc.list_favorites("user_1")
    assert len(favs) == 1
    assert favs[0].shop_id == 10

    await uc.remove_favorite("user_1", 10)
    assert len(await uc.list_favorites("user_1")) == 0
