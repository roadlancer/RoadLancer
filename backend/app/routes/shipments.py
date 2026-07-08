from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from app.routes.auth import get_current_user
from app.database import db
from app.services.pricing import estimate_price

router = APIRouter()


class ShipmentCreate(BaseModel):
    title: str
    goods_category: str
    weight_kg: float
    pickup_address: str
    dropoff_address: str
    distance_km: float
    vehicle_type: str
    shipper_budget: Optional[float] = None
    is_forced_price: Optional[bool] = False
    custom_min_price: Optional[float] = None
    custom_max_price: Optional[float] = None


class PriceEstimateRequest(BaseModel):
    distance_km: float
    weight_kg: float
    vehicle_type: str
    goods_category: str


class BidCreate(BaseModel):
    amount: float
    message: Optional[str] = None


def shipment_to_dict(s) -> dict:
    return {
        "id": s.id,
        "shipper_id": s.shipperId,
        "title": s.title,
        "goods_category": s.goodsCategory,
        "weight_kg": float(s.weightKg),
        "pickup_address": s.pickupAddress,
        "dropoff_address": s.dropoffAddress,
        "distance_km": float(s.distanceKm),
        "vehicle_type": s.vehicleType,
        "ai_floor_price": float(s.aiFloorPrice) if s.aiFloorPrice is not None else None,
        "ai_estimated_min": float(s.aiEstimatedMin) if s.aiEstimatedMin is not None else None,
        "ai_estimated_max": float(s.aiEstimatedMax) if s.aiEstimatedMax is not None else None,
        "shipper_budget": float(s.shipperBudget) if s.shipperBudget is not None else None,
        "is_forced_price": s.isForcedPrice,
        "status": s.status,
        "assigned_driver_id": s.assignedDriverId,
        "bidding_ends_at": s.biddingEndsAt.isoformat() if s.biddingEndsAt else None,
        "created_at": s.createdAt.isoformat(),
        "updated_at": s.updatedAt.isoformat(),
    }


def bid_to_dict(b) -> dict:
    return {
        "id": b.id,
        "shipment_id": b.shipmentId,
        "driver_id": b.driverId,
        "amount": float(b.amount),
        "message": b.message,
        "status": b.status,
        "created_at": b.createdAt.isoformat(),
    }


async def check_user_verified(user_id: str) -> bool:
    verif = await db.user_verifications.find_unique(where={"userId": user_id})
    if not verif:
        return False
    status = verif.status.value if hasattr(verif.status, "value") else verif.status
    return status == "approved"


@router.get("/")
async def list_shipments(user: dict = Depends(get_current_user)):
    if user["role"] == "shipper":
        shipments = await db.shipments.find_many(
            where={"shipperId": user["id"]},
            order={"createdAt": "desc"},
        )
    elif user["role"] == "driver":
        shipments = await db.shipments.find_many(
            where={"status": "active"},
            order={"createdAt": "desc"},
        )
    else:
        shipments = await db.shipments.find_many(
            order={"createdAt": "desc"},
        )
    return [shipment_to_dict(s) for s in shipments]


@router.get("/assigned")
async def list_assigned_shipments(user: dict = Depends(get_current_user)):
    if user["role"] != "driver":
        raise HTTPException(status_code=403, detail="Only drivers can view assigned shipments")

    shipments = await db.shipments.find_many(
        where={"assignedDriverId": user["id"]},
        order={"createdAt": "desc"},
    )
    return [shipment_to_dict(s) for s in shipments]


@router.put("/{shipment_id}/status")
async def update_shipment_status(
    shipment_id: str,
    status_update: dict,
    user: dict = Depends(get_current_user),
):
    if not await check_user_verified(user["id"]):
        raise HTTPException(status_code=403, detail="You must complete Document & Profile Verification before updating shipment status.")
    shipment = await db.shipments.find_unique(where={"id": shipment_id})
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    new_status = status_update.get("status")
    valid_statuses = ["active", "assigned", "picked_up", "in_transit", "delivered", "completed", "cancelled"]

    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    if user["role"] == "driver":
        if shipment.assignedDriverId != user["id"]:
            raise HTTPException(status_code=403, detail="You are not assigned to this shipment")
        allowed = {"picked_up", "in_transit", "delivered"}
        if new_status not in allowed:
            raise HTTPException(status_code=400, detail=f"Drivers can only update to: {allowed}")
    elif user["role"] == "shipper":
        if shipment.shipperId != user["id"]:
            raise HTTPException(status_code=403, detail="You are not the owner of this shipment")
        if new_status not in {"completed", "cancelled"}:
            raise HTTPException(status_code=400, detail=f"Shippers can only update to: completed, cancelled")
    else:
        raise HTTPException(status_code=403, detail="Only drivers and shippers can update shipment status")

    if shipment.status == "completed" or shipment.status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot update a completed or cancelled shipment")

    status_flow = {
        "active": ["assigned", "cancelled"],
        "assigned": ["picked_up", "cancelled"],
        "picked_up": ["in_transit"],
        "in_transit": ["delivered"],
        "delivered": ["completed"],
    }

    allowed_next = status_flow.get(shipment.status, [])
    if new_status not in allowed_next:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from '{shipment.status}' to '{new_status}'",
        )

    updated_shipment = await db.shipments.update(
        where={"id": shipment_id},
        data={"status": new_status},
    )
    return shipment_to_dict(updated_shipment)


@router.post("/estimate-price")
async def get_price_estimate(req: PriceEstimateRequest):
    result = estimate_price(
        distance_km=req.distance_km,
        weight_kg=req.weight_kg,
        vehicle_type=req.vehicle_type,
        goods_category=req.goods_category,
    )
    return result


@router.post("/")
async def create_shipment(
    shipment: ShipmentCreate,
    user: dict = Depends(get_current_user),
):
    if user.get("role") != "shipper":
        raise HTTPException(status_code=403, detail="Only shippers can create shipments")

    if not await check_user_verified(user["id"]):
        raise HTTPException(status_code=403, detail="You must complete Document & Profile Verification before you can post shipments.")

    try:
        pricing = estimate_price(
            distance_km=shipment.distance_km,
            weight_kg=shipment.weight_kg,
            vehicle_type=shipment.vehicle_type,
            goods_category=shipment.goods_category,
        )

        custom_min = shipment.custom_min_price if shipment.custom_min_price is not None else pricing["estimated_min"]
        custom_max = shipment.custom_max_price if shipment.custom_max_price is not None else pricing["estimated_max"]
        budget = shipment.custom_max_price if shipment.custom_max_price is not None else shipment.shipper_budget

        new_shipment = await db.shipments.create(
            data={
                "shipper": {"connect": {"id": user["id"]}},
                "title": shipment.title,
                "goodsCategory": shipment.goods_category,
                "weightKg": Decimal(str(shipment.weight_kg)),
                "pickupAddress": shipment.pickup_address,
                "dropoffAddress": shipment.dropoff_address,
                "distanceKm": Decimal(str(shipment.distance_km)),
                "vehicleType": shipment.vehicle_type,
                "aiFloorPrice": Decimal(str(pricing["floor_price"])),
                "aiEstimatedMin": Decimal(str(custom_min)),
                "aiEstimatedMax": Decimal(str(custom_max)),
                "shipperBudget": Decimal(str(budget)) if budget is not None else None,
                "isForcedPrice": shipment.is_forced_price or False,
                "status": "active",
            }
        )
        return shipment_to_dict(new_shipment)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Shipment creation failed ({type(e).__name__}): {str(e)}")


@router.get("/{shipment_id}")
async def get_shipment(shipment_id: str, user: dict = Depends(get_current_user)):
    shipment = await db.shipments.find_unique(where={"id": shipment_id})
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if user["role"] == "shipper" and shipment.shipperId != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    if user["role"] == "driver" and shipment.status == "active":
        pass
    elif user["role"] == "driver" and shipment.assignedDriverId != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return shipment_to_dict(shipment)


@router.post("/{shipment_id}/bids")
async def place_bid(
    shipment_id: str,
    bid: BidCreate,
    user: dict = Depends(get_current_user),
):
    if user.get("role") != "driver":
        raise HTTPException(status_code=403, detail="Only drivers can place bids")

    if not await check_user_verified(user["id"]):
        raise HTTPException(status_code=403, detail="You must complete Document & Profile Verification before you can place bids.")

    shipment = await db.shipments.find_unique(where={"id": shipment_id})
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if shipment.status != "active":
        raise HTTPException(status_code=400, detail="Shipment is not accepting bids")

    existing_bid = await db.bids.find_first(
        where={"shipmentId": shipment_id, "driverId": user["id"]}
    )
    bid_amount = Decimal(str(bid.amount))
    min_limit = shipment.aiEstimatedMin if shipment.aiEstimatedMin is not None else shipment.aiFloorPrice
    if min_limit is not None and bid_amount < min_limit:
        raise HTTPException(
            status_code=400,
            detail=f"Bid amount (₹{bid_amount:,.2f}) cannot be less than the shipper's minimum limit of ₹{min_limit:,.2f}",
        )

    max_limit = shipment.aiEstimatedMax if shipment.aiEstimatedMax is not None else shipment.shipperBudget
    if max_limit is not None and bid_amount > max_limit:
        raise HTTPException(
            status_code=400,
            detail=f"Bid amount (₹{bid_amount:,.2f}) cannot exceed the shipper's maximum limit of ₹{max_limit:,.2f}",
        )

    if existing_bid:
        new_bid = await db.bids.update(
            where={"id": existing_bid.id},
            data={
                "amount": bid_amount,
                "message": bid.message,
            }
        )
    else:
        new_bid = await db.bids.create(
            data={
                "shipment": {"connect": {"id": shipment_id}},
                "driver": {"connect": {"id": user["id"]}},
                "amount": bid_amount,
                "message": bid.message,
            }
        )
    return bid_to_dict(new_bid)


@router.get("/{shipment_id}/bids")
async def list_bids(shipment_id: str, user: dict = Depends(get_current_user)):
    shipment = await db.shipments.find_unique(where={"id": shipment_id})
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if user.get("role") == "driver":
        bids_list = await db.bids.find_many(
            where={"shipmentId": shipment_id, "driverId": user["id"]},
            order={"amount": "asc"},
        )
    else:
        if shipment.shipperId != user["id"] and user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to view these bids")
        bids_list = await db.bids.find_many(
            where={"shipmentId": shipment_id},
            order={"amount": "asc"},
        )

    return [bid_to_dict(b) for b in bids_list]


@router.get("/bids/my")
async def my_bids(user: dict = Depends(get_current_user)):
    if user.get("role") != "driver":
        raise HTTPException(status_code=403, detail="Only drivers have bids")

    bids_list = await db.bids.find_many(
        where={"driverId": user["id"]},
        order={"createdAt": "desc"},
    )
    return [bid_to_dict(b) for b in bids_list]


@router.get("/{shipment_id}/bids/count")
async def count_bids(shipment_id: str, user: dict = Depends(get_current_user)):
    shipment = await db.shipments.find_unique(where={"id": shipment_id})
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if user["role"] == "shipper" and shipment.shipperId != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    bids = await db.bids.find_many(where={"shipmentId": shipment_id})
    return {"count": len(bids)}


@router.put("/{shipment_id}/bids/update")
async def update_bid(
    shipment_id: str,
    bid_update: BidCreate,
    user: dict = Depends(get_current_user),
):
    if user.get("role") != "driver":
        raise HTTPException(status_code=403, detail="Only drivers can update bids")

    if user.get("status") != "approved":
        raise HTTPException(status_code=403, detail="Your account is currently pending verification and admin approval.")

    shipment = await db.shipments.find_unique(where={"id": shipment_id})
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if shipment.status != "active":
        raise HTTPException(status_code=400, detail="Shipment is not accepting bids")

    existing_bid = await db.bids.find_first(
        where={"shipmentId": shipment_id, "driverId": user["id"]}
    )
    if not existing_bid:
        raise HTTPException(status_code=404, detail="No bid found to update. Use POST to place a new bid.")

    bid_amount = Decimal(str(bid_update.amount))
    min_limit = shipment.aiEstimatedMin if shipment.aiEstimatedMin is not None else shipment.aiFloorPrice
    if min_limit is not None and bid_amount < min_limit:
        raise HTTPException(
            status_code=400,
            detail=f"Bid amount (₹{bid_amount:,.2f}) cannot be less than the shipper's minimum limit of ₹{min_limit:,.2f}",
        )

    max_limit = shipment.aiEstimatedMax if shipment.aiEstimatedMax is not None else shipment.shipperBudget
    if max_limit is not None and bid_amount > max_limit:
        raise HTTPException(
            status_code=400,
            detail=f"Bid amount (₹{bid_amount:,.2f}) cannot exceed the shipper's maximum limit of ₹{max_limit:,.2f}",
        )

    updated_bid = await db.bids.update(
        where={"id": existing_bid.id},
        data={
            "amount": Decimal(str(bid_update.amount)),
            "message": bid_update.message,
            "status": "pending",
        },
    )
    return bid_to_dict(updated_bid)


@router.delete("/{shipment_id}/bids/withdraw")
async def withdraw_bid(
    shipment_id: str,
    user: dict = Depends(get_current_user),
):
    if user.get("role") != "driver":
        raise HTTPException(status_code=403, detail="Only drivers can withdraw bids")

    if user.get("status") != "approved":
        raise HTTPException(status_code=403, detail="Your account is currently pending verification and admin approval.")

    shipment = await db.shipments.find_unique(where={"id": shipment_id})
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if shipment.status != "active":
        raise HTTPException(status_code=400, detail="Shipment is not accepting bids")

    existing_bid = await db.bids.find_first(
        where={"shipmentId": shipment_id, "driverId": user["id"]}
    )
    if not existing_bid:
        raise HTTPException(status_code=404, detail="No bid found to withdraw.")

    await db.bids.delete(where={"id": existing_bid.id})
    return {"message": "Bid withdrawn successfully"}


@router.put("/bids/{bid_id}/accept")
async def accept_bid(bid_id: str, user: dict = Depends(get_current_user)):
    if user.get("status") != "approved":
        raise HTTPException(status_code=403, detail="Your account is currently pending verification and admin approval. You cannot accept bids until your account is approved.")
    bid = await db.bids.find_unique(where={"id": bid_id})
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    shipment = await db.shipments.find_unique(where={"id": bid.shipmentId})
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if shipment.shipperId != user["id"]:
        raise HTTPException(status_code=403, detail="Only the shipper can accept bids")

    if shipment.status != "active":
        raise HTTPException(status_code=400, detail="Shipment is not accepting bids")

    await db.bids.update(
        where={"id": bid_id},
        data={"status": "accepted"},
    )
    await db.bids.update_many(
        where={"shipmentId": bid.shipmentId, "id": {"not": bid_id}},
        data={"status": "rejected"},
    )

    await db.shipments.update(
        where={"id": bid.shipmentId},
        data={
            "status": "assigned",
            "assignedDriverId": bid.driverId,
        },
    )

    return {"message": "Bid accepted", "shipment_status": "assigned"}
