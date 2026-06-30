from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from app.routes.auth import get_current_user
from app.database import db

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
        "ai_floor_price": float(s.aiFloorPrice) if s.aiFloorPrice else None,
        "ai_estimated_min": float(s.aiEstimatedMin) if s.aiEstimatedMin else None,
        "ai_estimated_max": float(s.aiEstimatedMax) if s.aiEstimatedMax else None,
        "shipper_budget": float(s.shipperBudget) if s.shipperBudget else None,
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


@router.get("/")
async def list_shipments(user: dict = Depends(get_current_user)):
    if user["role"] == "shipper":
        shipments = await db.shipments.find_many(
            where={"shipperId": user["id"], "status": "active"},
        )
    else:
        shipments = await db.shipments.find_many(
            where={"status": "active"},
        )
    return [shipment_to_dict(s) for s in shipments]


@router.post("/")
async def create_shipment(
    shipment: ShipmentCreate,
    user: dict = Depends(get_current_user),
):
    if user.get("role") != "shipper":
        raise HTTPException(status_code=403, detail="Only shippers can create shipments")

    base_price = shipment.distance_km * 15 + shipment.weight_kg * 2
    ai_floor_price = base_price * 0.7
    ai_estimated_min = base_price * 0.8
    ai_estimated_max = base_price * 1.2

    new_shipment = await db.shipments.create(
        data={
            "shipperId": user["id"],
            "title": shipment.title,
            "goodsCategory": shipment.goods_category,
            "weightKg": Decimal(str(shipment.weight_kg)),
            "pickupAddress": shipment.pickup_address,
            "dropoffAddress": shipment.dropoff_address,
            "distanceKm": Decimal(str(shipment.distance_km)),
            "vehicleType": shipment.vehicle_type,
            "aiFloorPrice": Decimal(str(ai_floor_price)),
            "aiEstimatedMin": Decimal(str(ai_estimated_min)),
            "aiEstimatedMax": Decimal(str(ai_estimated_max)),
            "shipperBudget": Decimal(str(shipment.shipper_budget)) if shipment.shipper_budget else None,
            "status": "active",
        }
    )
    return shipment_to_dict(new_shipment)


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

    shipment = await db.shipments.find_unique(where={"id": shipment_id})
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if shipment.status != "active":
        raise HTTPException(status_code=400, detail="Shipment is not accepting bids")

    if shipment.aiFloorPrice and Decimal(str(bid.amount)) < shipment.aiFloorPrice:
        raise HTTPException(
            status_code=400,
            detail=f"Bid must be at least ₹{shipment.aiFloorPrice}",
        )

    new_bid = await db.bids.create(
        data={
            "shipmentId": shipment_id,
            "driverId": user["id"],
            "amount": Decimal(str(bid.amount)),
            "message": bid.message,
        }
    )
    return bid_to_dict(new_bid)


@router.get("/{shipment_id}/bids")
async def list_bids(shipment_id: str, user: dict = Depends(get_current_user)):
    shipment = await db.shipments.find_unique(where={"id": shipment_id})
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if user["role"] == "driver":
        bids = await db.bids.find_many(
            where={"shipmentId": shipment_id, "driverId": user["id"]},
        )
    else:
        if shipment.shipperId != user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        bids = await db.bids.find_many(
            where={"shipmentId": shipment_id},
        )

    return [bid_to_dict(b) for b in bids]


@router.put("/bids/{bid_id}/accept")
async def accept_bid(bid_id: str, user: dict = Depends(get_current_user)):
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
