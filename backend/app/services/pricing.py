"""
AI-Based Pricing Engine for RoadLancer
Considers: distance, weight, vehicle type, goods category, fuel, tolls, labour, market factors
"""
from datetime import datetime
from typing import Optional


# === Rate Tables ===

# Distance-based per-km rate (INR) — tiered for local/short/long haul
DISTANCE_RATES = [
    (100, 18.0),    # Local: <100 km
    (500, 14.0),    # Short haul: 100-500 km
    (float('inf'), 11.0),  # Long haul: 500+ km
]

# Weight-based rate (INR per kg) — tiered with diminishing marginal cost
WEIGHT_RATES = [
    (1000, 2.0),    # First 1000 kg
    (5000, 1.5),    # 1000-5000 kg
    (float('inf'), 1.0),  # 5000+ kg
]

# Vehicle type multipliers
VEHICLE_MULTIPLIERS = {
    "tempo": 0.80,
    "407": 1.00,
    "canter": 1.00,
    "10wheeler": 1.40,
    "10_wheeler": 1.40,
    "19mt": 1.40,
    "19_mt": 1.40,
    "32mt": 1.80,
    "32_mt": 1.80,
    "trailer": 1.80,
    "lcv": 0.80,
    "hcv": 1.40,
    "container": 1.60,
}

# Vehicle fuel consumption (litres per km) — loaded
VEHICLE_FUEL_RATE = {
    "tempo": 0.08,
    "407": 0.12,
    "canter": 0.12,
    "10wheeler": 0.18,
    "10_wheeler": 0.18,
    "19mt": 0.22,
    "19_mt": 0.22,
    "32mt": 0.30,
    "32_mt": 0.30,
    "trailer": 0.30,
    "lcv": 0.08,
    "hcv": 0.18,
    "container": 0.25,
}

# Vehicle labour cost (driver + helper) per trip base
VEHICLE_LABOUR = {
    "tempo": 500,
    "407": 800,
    "canter": 800,
    "10wheeler": 1200,
    "10_wheeler": 1200,
    "19mt": 1500,
    "19_mt": 1500,
    "32mt": 2000,
    "32_mt": 2000,
    "trailer": 2000,
    "lcv": 500,
    "hcv": 1200,
    "container": 1800,
}

# Goods category multipliers
GOODS_MULTIPLIERS = {
    "general": 1.00,
    "electronics": 1.10,
    "fragile": 1.15,
    "glass": 1.20,
    "hazmat": 1.25,
    "hazardous": 1.25,
    "perishable": 1.20,
    "cold_chain": 1.30,
    "cold chain": 1.30,
    "fmcg": 1.00,
    "textiles": 0.95,
    "industrial": 1.05,
    "construction": 1.00,
    "automobile": 1.10,
    "pharmaceutical": 1.15,
    "high_value": 1.10,
    "high value": 1.10,
    "livestock": 1.20,
    "furniture": 1.10,
}

# Diesel price per litre (INR) — can be updated dynamically
DIESEL_PRICE_PER_LITRE = 90.0

# Toll estimate per km for highway routes (INR)
TOLL_PER_KM = 2.0

# Seasonal multipliers by month (1-indexed)
SEASONAL_MULTIPLIERS = {
    1: 0.95,   # January — post-festival slowdown
    2: 0.95,   # February — slow
    3: 1.00,   # March — fiscal year end
    4: 1.00,   # April — normal
    5: 1.00,   # May — normal
    6: 1.05,   # June — pre-monsoon stock-up
    7: 1.00,   # July — monsoon
    8: 1.00,   # August — monsoon
    9: 1.10,   # September — festive season begins
    10: 1.15,  # October — Diwali peak
    11: 1.15,  # November — Diwari + wedding season
    12: 1.05,  # December — year-end
}


def get_distance_rate(distance_km: float) -> float:
    """Get per-km rate based on distance tier."""
    for threshold, rate in DISTANCE_RATES:
        if distance_km <= threshold:
            return rate
    return DISTANCE_RATES[-1][1]


def calculate_weight_cost(weight_kg: float) -> float:
    """Calculate total weight-based cost with tiered pricing."""
    total = 0.0
    remaining = weight_kg
    prev_threshold = 0

    for threshold, rate in WEIGHT_RATES:
        tier_weight = min(remaining, threshold - prev_threshold)
        if tier_weight <= 0:
            break
        total += tier_weight * rate
        remaining -= tier_weight
        prev_threshold = threshold

    return total


def get_vehicle_multiplier(vehicle_type: str) -> float:
    """Get cost multiplier for vehicle type."""
    key = vehicle_type.lower().strip().replace(" ", "_").replace("-", "_")
    return VEHICLE_MULTIPLIERS.get(key, 1.0)


def get_fuel_rate(vehicle_type: str) -> float:
    """Get fuel consumption rate (L/km) for vehicle type."""
    key = vehicle_type.lower().strip().replace(" ", "_").replace("-", "_")
    return VEHICLE_FUEL_RATE.get(key, 0.15)


def get_labour_cost(vehicle_type: str) -> float:
    """Get base labour cost (driver + helper) for vehicle type."""
    key = vehicle_type.lower().strip().replace(" ", "_").replace("-", "_")
    return VEHICLE_LABOUR.get(key, 1000)


def get_goods_multiplier(goods_category: str) -> float:
    """Get cost multiplier for goods category."""
    key = goods_category.lower().strip().replace(" ", "_")
    return GOODS_MULTIPLIERS.get(key, 1.0)


def get_seasonal_multiplier() -> float:
    """Get current seasonal demand multiplier."""
    month = datetime.now().month
    return SEASONAL_MULTIPLIERS.get(month, 1.0)


def estimate_price(
    distance_km: float,
    weight_kg: float,
    vehicle_type: str,
    goods_category: str,
) -> dict:
    """
    Calculate AI-based price estimate for a shipment.

    Returns:
        {
            "base_cost": float,
            "fuel_cost": float,
            "toll_cost": float,
            "labour_cost": float,
            "vehicle_adjustment": float,
            "goods_adjustment": float,
            "seasonal_adjustment": float,
            "total_before_margin": float,
            "floor_price": float,
            "estimated_min": float,
            "estimated_max": float,
            "breakdown": { ... }
        }
    """
    # 1. Base transport cost (distance + weight)
    per_km_rate = get_distance_rate(distance_km)
    distance_cost = distance_km * per_km_rate
    weight_cost = calculate_weight_cost(weight_kg)
    base_cost = distance_cost + weight_cost

    # 2. Fuel cost
    fuel_rate = get_fuel_rate(vehicle_type)
    fuel_cost = distance_km * fuel_rate * DIESEL_PRICE_PER_LITRE

    # 3. Toll cost (highway estimate)
    toll_cost = distance_km * TOLL_PER_KM

    # 4. Labour cost (driver + helper)
    labour_base = get_labour_cost(vehicle_type)
    # Scale labour with distance: +₹5/km for long hauls
    labour_cost = labour_base + (max(0, distance_km - 200) * 5)

    # 5. Vehicle type adjustment
    vehicle_mult = get_vehicle_multiplier(vehicle_type)
    vehicle_adjustment = base_cost * (vehicle_mult - 1.0)

    # 6. Goods category adjustment
    goods_mult = get_goods_multiplier(goods_category)
    goods_adjustment = base_cost * (goods_mult - 1.0)

    # 7. Subtotal before seasonal adjustment
    subtotal = base_cost + fuel_cost + toll_cost + labour_cost + vehicle_adjustment + goods_adjustment

    # 8. Seasonal adjustment
    seasonal_mult = get_seasonal_multiplier()
    seasonal_adjustment = subtotal * (seasonal_mult - 1.0)

    # 9. Total before margin
    total_before_margin = subtotal + seasonal_adjustment

    # 10. Apply margin bands for floor/min/max
    # Floor: 70% — minimum viable price for drivers
    # Min: 85% — competitive low end
    # Max: 125% — premium pricing
    floor_price = round(total_before_margin * 0.70)
    estimated_min = round(total_before_margin * 0.85)
    estimated_max = round(total_before_margin * 1.25)

    return {
        "floor_price": floor_price,
        "estimated_min": estimated_min,
        "estimated_max": estimated_max,
        "breakdown": {
            "distance_cost": round(distance_cost),
            "weight_cost": round(weight_cost),
            "base_cost": round(base_cost),
            "fuel_cost": round(fuel_cost),
            "toll_cost": round(toll_cost),
            "labour_cost": round(labour_cost),
            "vehicle_adjustment": round(vehicle_adjustment),
            "goods_adjustment": round(goods_adjustment),
            "seasonal_adjustment": round(seasonal_adjustment),
            "total_before_margin": round(total_before_margin),
            "per_km_rate": per_km_rate,
            "fuel_rate_per_litre": DIESEL_PRICE_PER_LITRE,
            "vehicle_multiplier": vehicle_mult,
            "goods_multiplier": goods_mult,
            "seasonal_multiplier": seasonal_mult,
        },
    }
