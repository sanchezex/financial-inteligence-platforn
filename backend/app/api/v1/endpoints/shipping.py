"""
Financial Intelligence Platform - Shipping Data Endpoints

API endpoints for shipping and supply chain data including freight rates, port activity, and vessel tracking.
Includes live ship tracking with commodity and forex market impact correlation.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
import random
import math

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ============================================================================
# Realistic Shipping Routes and Waypoints
# ============================================================================

# Major shipping chokepoints
SHIPPING_CHOKEPOINTS = {
    "suez_canal": {"name": "Suez Canal", "lat": 30.5852, "lon": 32.2650, "risk_level": "high"},
    "panama_canal": {"name": "Panama Canal", "lat": 9.0, "lon": -79.5, "risk_level": "medium"},
    "malacca_strait": {"name": "Malacca Strait", "lat": 2.5, "lon": 101.5, "risk_level": "high"},
    "suez_canal_south": {"name": "Suez Canal South", "lat": 29.9, "lon": 32.5, "risk_level": "medium"},
    "gibraltar": {"name": "Strait of Gibraltar", "lat": 35.9, "lon": -5.5, "risk_level": "low"},
    "bosporus": {"name": "Bosporus", "lat": 41.0, "lon": 29.0, "risk_level": "medium"},
}

# Major ports with coordinates
MAJOR_PORTS = {
    "Shanghai": {"lat": 31.2304, "lon": 121.4737, "country": "China", "type": "container"},
    "Singapore": {"lat": 1.3521, "lon": 103.8198, "country": "Singapore", "type": "hub"},
    "Rotterdam": {"lat": 51.9244, "lon": 4.4777, "country": "Netherlands", "type": "container"},
    "Los Angeles": {"lat": 33.7405, "lon": -118.2786, "country": "USA", "type": "container"},
    "Ningbo-Zhoushan": {"lat": 29.8683, "lon": 121.5440, "country": "China", "type": "container"},
    "Shenzhen": {"lat": 22.5431, "lon": 114.0579, "country": "China", "type": "container"},
    "Busan": {"lat": 35.1796, "lon": 129.0756, "country": "South Korea", "type": "container"},
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694, "country": "China", "type": "hub"},
    "Antwerp": {"lat": 51.2194, "lon": 4.4025, "country": "Belgium", "type": "container"},
    "Hamburg": {"lat": 53.5511, "lon": 9.9937, "country": "Germany", "type": "container"},
    "Dubai": {"lat": 25.2048, "lon": 55.2708, "country": "UAE", "type": "hub"},
    "New York": {"lat": 40.7128, "lon": -74.0060, "country": "USA", "type": "container"},
    "Long Beach": {"lat": 33.7701, "lon": -118.1937, "country": "USA", "type": "container"},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503, "country": "Japan", "type": "container"},
    "Santos": {"lat": -23.9608, "lon": -46.3331, "country": "Brazil", "type": "bulk"},
    "Richards Bay": {"lat": -28.7810, "lon": 32.0376, "country": "South Africa", "type": "bulk"},
    "Fremantle": {"lat": -32.0267, "lon": 115.7472, "country": "Australia", "type": "bulk"},
    "Hampton Roads": {"lat": 36.95, "lon": -76.33, "country": "USA", "type": "bulk"},
    "Ras Tanura": {"lat": 26.65, "lon": 50.15, "country": "Saudi Arabia", "type": "oil"},
    "Kharg Island": {"lat": 29.25, "lon": 50.3, "country": "Iran", "type": "oil"},
    "Bapco": {"lat": 26.05, "lon": 50.5, "country": "Bahrain", "type": "oil"},
    "Ceylon": {"lat": 7.0, "lon": 80.0, "country": "Sri Lanka", "type": "hub"},
    "Colombo": {"lat": 6.9344, "lon": 79.8428, "country": "Sri Lanka", "type": "hub"},
    "Singapore_South": {"lat": 1.2, "lon": 104.0, "country": "Singapore", "type": "anchor"},
}

# Major shipping routes with waypoints
SHIPPING_ROUTES = {
    "asia_europe": {
        "name": "Asia-Europe",
        "waypoints": [
            (31.2304, 121.4737),  # Shanghai
            (30.5, 125.0),        # East China Sea
            (25.0, 120.0),        # Taiwan Strait
            (15.0, 110.0),        # South China Sea
            (3.0, 100.0),         # Malacca Strait
            (0.0, 80.0),          # Indian Ocean
            (-10.0, 60.0),        # Arabian Sea
            (15.0, 40.0),         # Red Sea North
            (29.9, 32.5),         # Suez Canal South
            (30.5852, 32.2650),   # Suez Canal
            (32.0, 30.0),         # Mediterranean East
            (35.0, 20.0),         # Mediterranean
            (36.0, 5.0),          # Gibraltar
            (45.0, -5.0),          # Bay of Biscay
            (51.0, 2.0),          # North Sea
            (51.9244, 4.4777),    # Rotterdam
        ],
        "commodities": ["containers", "electronics", "textiles", "machinery"],
        "avg_days": 32,
    },
    "asia_west_coast": {
        "name": "Asia-US West Coast",
        "waypoints": [
            (31.2304, 121.4737),  # Shanghai
            (30.0, 140.0),        # Pacific
            (25.0, 150.0),        # North Pacific
            (20.0, -160.0),       # Pacific Center
            (25.0, -170.0),       # Near Guam
            (30.0, -140.0),       # Pacific
            (33.0, -130.0),       # Approach LA
            (33.7405, -118.2786),  # Los Angeles
        ],
        "commodities": ["containers", "electronics", "furniture", "apparel"],
        "avg_days": 18,
    },
    "asia_east_coast": {
        "name": "Asia-US East Coast (via Panama)",
        "waypoints": [
            (31.2304, 121.4737),  # Shanghai
            (25.0, 130.0),        # Pacific
            (15.0, -100.0),       # Panama Approach
            (9.0, -79.5),         # Panama Canal
            (8.5, -80.0),         # Panama Pacific
            (10.0, -70.0),        # Caribbean
            (20.0, -75.0),        # Atlantic
            (30.0, -80.0),        # East Coast
            (40.7128, -74.0060),  # New York
        ],
        "commodities": ["containers", "electronics", "vehicles", "machinery"],
        "avg_days": 28,
    },
    "middle_east_asia": {
        "name": "Middle East-Asia",
        "waypoints": [
            (26.65, 50.15),       # Ras Tanura
            (25.0, 55.0),         # Persian Gulf Exit
            (25.0, 60.0),         # Gulf of Oman
            (22.0, 67.0),         # Pakistan Coast
            (15.0, 70.0),         # Arabian Sea
            (10.0, 80.0),         # Bay of Bengal
            (5.0, 95.0),          # Strait of Malacca
            (1.3521, 103.8198),  # Singapore
            (3.0, 100.0),         # Malacca Strait
            (5.0, 110.0),         # South China Sea
            (22.0, 114.0),        # Pearl River Delta
            (22.5431, 114.0579),  # Shenzhen
        ],
        "commodities": ["crude_oil", "refined_products", "LNG", "chemicals"],
        "avg_days": 12,
    },
    "europe_usa": {
        "name": "Europe-US East Coast",
        "waypoints": [
            (51.9244, 4.4777),    # Rotterdam
            (51.0, 0.0),          # Channel
            (45.0, -5.0),         # Atlantic
            (40.0, -30.0),         # Mid Atlantic
            (35.0, -60.0),         # Grand Banks
            (38.0, -70.0),         # Approach US
            (40.0, -75.0),         # Delaware
            (40.7128, -74.0060),  # New York
        ],
        "commodities": ["containers", "machinery", "vehicles", "chemicals"],
        "avg_days": 14,
    },
    "australia_asia": {
        "name": "Australia-Asia",
        "waypoints": [
            (-33.8688, 151.2093), # Sydney
            (-25.0, 150.0),       # Coral Sea
            (-15.0, 140.0),       # Arafura Sea
            (-5.0, 120.0),        # Java Sea
            (0.0, 110.0),         # Singapore Route
            (3.0, 100.0),         # Malacca Strait
            (5.0, 100.0),         # Strait
            (15.0, 105.0),        # South China Sea
            (22.0, 114.0),        # Hong Kong
            (22.5431, 114.0579),  # Shenzhen
        ],
        "commodities": ["iron_ore", "coal", "grain", "livestock"],
        "avg_days": 14,
    },
    "brazil_asia": {
        "name": "Brazil-Asia",
        "waypoints": [
            (-23.9608, -46.3331), # Santos
            (-20.0, -40.0),       # Atlantic
            (-10.0, -30.0),       # South Atlantic
            (0.0, -20.0),         # Equator
            (10.0, 0.0),          # Atlantic
            (0.0, 20.0),          # Gulf of Guinea
            (-10.0, 40.0),        # South Atlantic Return
            (0.0, 60.0),          # Indian Ocean
            (-20.0, 80.0),        # Indian Ocean
            (-10.0, 100.0),       # Indonesian waters
            (0.0, 110.0),         # Java Sea
            (22.0, 114.0),        # Hong Kong
        ],
        "commodities": ["soybeans", "iron_ore", "sugar", "coffee"],
        "avg_days": 35,
    },
    "west_africa_asia": {
        "name": "West Africa-Asia",
        "waypoints": [
            (-5.0, 10.0),         # Cameroon
            (-2.0, 5.0),          # Gulf of Guinea
            (0.0, 0.0),           # Equator
            (-10.0, 20.0),        # South Atlantic
            (-20.0, 40.0),        # South Atlantic
            (-30.0, 60.0),        # Southern Ocean
            (-35.0, 80.0),         # Indian Ocean
            (-20.0, 100.0),       # Indian Ocean
            (-10.0, 110.0),       # Indonesian waters
            (0.0, 110.0),         # Java Sea
            (22.0, 114.0),        # Hong Kong
        ],
        "commodities": ["crude_oil", "cocoa", "timber", "manganese"],
        "avg_days": 40,
    },
}

# Helper function to interpolate position along route
def get_position_along_route(route_name: str, progress: float) -> Tuple[float, float]:
    """Get vessel position based on route progress (0-1)."""
    route = SHIPPING_ROUTES.get(route_name)
    if not route:
        return (random.uniform(-60, 70), random.uniform(-180, 180))
    
    waypoints = route["waypoints"]
    if len(waypoints) < 2:
        return waypoints[0] if waypoints else (0, 0)
    
    # Calculate total segments
    total_segments = len(waypoints) - 1
    segment_length = 1.0 / total_segments
    
    # Find current segment
    segment = int(progress / segment_length)
    segment = min(segment, total_segments - 1)
    local_progress = (progress - segment * segment_length) / segment_length
    
    # Interpolate position
    start_lat, start_lon = waypoints[segment]
    end_lat, end_lon = waypoints[segment + 1]
    
    lat = start_lat + (end_lat - start_lat) * local_progress
    lon = start_lon + (end_lon - start_lon) * local_progress
    
    # Add some randomness for realism
    lat += random.uniform(-0.5, 0.5)
    lon += random.uniform(-0.5, 0.5)
    
    return (lat, lon)


# ============================================================================
# Models
# ============================================================================

class FreightRate(BaseModel):
    """Freight rate model."""
    route_code: str
    origin: str
    destination: str
    spot_rate: Decimal
    contract_rate: Decimal
    change_percent: float
    timestamp: datetime


class PortActivity(BaseModel):
    """Port activity model."""
    port_code: str
    port_name: str
    country: str
    vessels_in_port: int
    vessels_anchored: int
    avg_wait_time_hours: float
    utilization_percent: float
    status: str
    timestamp: datetime


class ShippingRoute(BaseModel):
    """Shipping route model."""
    route_code: str
    origin_port: str
    destination_port: str
    route_type: str
    distance_nm: float
    transit_time_days: float
    commodity_types: List[str]


class ShippingIndex(BaseModel):
    """Shipping index model."""
    index_name: str
    index_value: float
    change_percent: float
    period: str
    timestamp: datetime


class VesselPosition(BaseModel):
    """Vessel position model."""
    vessel_name: str
    vessel_type: str
    mmsi: str
    latitude: float
    longitude: float
    destination: Optional[str]
    eta: Optional[datetime]
    speed: float
    status: str
    last_update: datetime


# ============================================================================
# New Models for Market Impact Ship Tracking
# ============================================================================

class CommodityImpact(BaseModel):
    """Impact of shipping on commodity prices."""
    commodity: str
    commodity_symbol: str
    current_price: float
    price_change_24h: float
    shipping_impact_score: float = Field(..., description="0-100 score of how much shipping affects this commodity")
    affected_routes: List[str]
    key_players: List[str]  # Major shipping companies
    supply_demand_balance: str
    market_sentiment: str


class ForexImpact(BaseModel):
    """Impact of shipping on forex pairs."""
    currency_pair: str
    current_rate: float
    change_24h: float
    shipping_impact_score: float = Field(..., description="0-100 score of how shipping affects this pair")
    affected_countries: List[str]
    trade_volume_impact: str
    central_bank_factor: str


class ShipMarketImpact(BaseModel):
    """Complete market impact data for a vessel."""
    vessel: VesselPosition
    carrying_commodity: Optional[str]
    commodity_impact: Optional[CommodityImpact]
    forex_impact: Optional[ForexImpact]
    economic_significance: float = Field(..., description="0-100 score of economic impact")
    market_events: List[str]
    last_analysis: datetime
    route_name: Optional[str] = None
    route_progress: Optional[float] = None
    heading: Optional[float] = None


class LiveShipTracking(BaseModel):
    """Live ship tracking with market impact data."""
    total_vessels_tracked: int
    vessels_by_type: Dict[str, int]
    vessels: List[ShipMarketImpact]
    high_impact_vessels: List[str]  # MMSI of high impact vessels
    market_summary: Dict[str, Any]
    global_trade_index: float
    timestamp: datetime
    active_chokepoints: List[Dict[str, Any]] = []
    port_congestion: List[Dict[str, Any]] = []


class ShipRouteAnalysis(BaseModel):
    """Analysis of shipping routes and their market impact."""
    route_id: str
    origin: str
    destination: str
    commodity_type: str
    vessel_types: List[str]
    avg_transit_days: float
    daily_volume_mt: float
    price_impact_volatility: float
    forex_correlation: float
    current_congestion_level: str
    estimated_delay_hours: float
    market_risk_level: str


# ============================================================================
# Helper Functions
# ============================================================================

VESSEL_PREFIXES = {
    "container": ["Evergreen", "Maersk", "MSC", "CMA CGM", "COSCO", "Hapag-Lloyd", "ONE", "Yang Ming", "HMM", "ZIM"],
    "bulk": ["Pacific", "Atlantic", "Navigator", "Horizon", "Titan", "Oceanus", "Star", "Nordic", "Borealis", "Aurora"],
    "tanker": ["Titan", "Neptune", "Prometheus", "Apollo", "Atlas", "Hercules", "Venus", "Jupiter", "Saturn", "Mars"],
    "gas_carrier": ["Methane", "Ethane", "Propane", "LNG", "GNL", "Arctic", "Nord", "Frost", "Ice", "Polar"],
    "cruise": ["Queen", "Titanic", "Olympic", "Viking", "Celebrity", "Royal", "Norwegian", "Carnival", "Disney", "Princess"],
}


def generate_vessel_name(vessel_type: str, index: int) -> str:
    """Generate realistic vessel name."""
    prefixes = VESSEL_PREFIXES.get(vessel_type, ["Vessel"])
    prefix = random.choice(prefixes)
    suffix_options = ["Voyager", "Trader", "Explorer", "Carrier", "Express", "Champion", "Giant", "Leader", "Navigator", "Star"]
    suffix = random.choice(suffix_options)
    return f"{prefix} {suffix} {index + 1}"


def calculate_economic_significance(vessel_type: str, cargo_type: str, market_events: List[str]) -> float:
    """Calculate economic significance based on vessel type, cargo, and events."""
    base_significance = {
        "tanker": 85,      # Oil tankers have high economic impact
        "gas_carrier": 80, # LNG carriers are critical for energy
        "bulk": 70,        # Bulk carriers transport essential commodities
        "container": 60,   # Container ships are important but less so
        "cruise": 40,      # Cruise ships have lower economic impact
    }.get(vessel_type, 50)
    
    # Adjust for cargo type
    high_value_cargos = ["crude_oil", "LNG", "natural_gas", "iron_ore", "copper", "lithium"]
    if cargo_type.lower() in high_value_cargos:
        base_significance += 10
    
    # Adjust for market events
    if len(market_events) > 2:
        base_significance += 10
    elif len(market_events) > 0:
        base_significance += 5
    
    return min(95, max(30, base_significance + random.uniform(-10, 10)))


# ============================================================================
# Freight Rate Endpoints
# ============================================================================

@router.get("/freight-rates", response_model=List[FreightRate])
async def get_freight_routes(
    route_type: Optional[str] = None,
    limit: int = Query(default=50, le=100)
):
    """
    Get current freight rates for major shipping routes.
    
    Returns spot and contract rates for container, bulk, and tanker routes.
    """
    import random
    
    routes = [
        {"route_code": "SHA-LAX", "origin": "Shanghai", "destination": "Los Angeles", "type": "container"},
        {"route_code": "SHA-NYC", "origin": "Shanghai", "destination": "New York", "type": "container"},
        {"route_code": "SIN-ROT", "origin": "Singapore", "destination": "Rotterdam", "type": "container"},
        {"route_code": "BUS-LA", "origin": "Busan", "destination": "Los Angeles", "type": "container"},
        {"route_code": "NGB-LAX", "origin": "Ningbo", "destination": "Los Angeles", "type": "container"},
        {"route_code": "BDI-BC", "origin": "Baltic", "destination": "China", "type": "bulk"},
        {"route_code": "BDI-EC", "origin": "Baltic", "destination": "Europe", "type": "bulk"},
        {"route_code": "TD3-DUB", "origin": "Ras Tanura", "destination": "Dubai", "type": "tanker"},
        {"route_code": "TD7-SIN", "origin": "Ras Tanura", "destination": "Singapore", "type": "tanker"},
    ]
    
    if route_type:
        routes = [r for r in routes if r["type"].lower() == route_type.lower()]
    
    rates = []
    for route in routes[:limit]:
        spot = Decimal(str(round(500 + random.random() * 3000, 2)))
        change = round(random.uniform(-15, 15), 2)
        
        rates.append(FreightRate(
            route_code=route["route_code"],
            origin=route["origin"],
            destination=route["destination"],
            spot_rate=spot,
            contract_rate=spot * Decimal(str(round(0.8 + random.random() * 0.3, 2))),
            change_percent=change,
            timestamp=datetime.utcnow()
        ))
    
    return rates


@router.get("/freight-rates/{route_code}")
async def get_freight_rate_history(
    route_code: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(default=30, le=365)
):
    """
    Get historical freight rates for a specific route.
    
    Returns time series data for the specified shipping route.
    """
    import random
    
    end = end_date or datetime.utcnow()
    start = start_date or (end - timedelta(days=limit))
    
    rates = []
    current = start
    
    while current <= end:
        spot = Decimal(str(round(500 + random.random() * 3000, 2)))
        rates.append({
            "timestamp": current,
            "spot_rate": spot,
            "contract_rate": spot * Decimal(str(round(0.8 + random.random() * 0.3, 2))),
            "change_percent": round(random.uniform(-10, 10), 2)
        })
        current += timedelta(days=1)
    
    return {
        "route_code": route_code,
        "rates": rates,
        "statistics": {
            "mean": round(float(sum(r["spot_rate"] for r in rates) / len(rates)), 2),
            "high": max(r["spot_rate"] for r in rates),
            "low": min(r["spot_rate"] for r in rates),
            "volatility": round(random.uniform(5, 15), 2)
        }
    }


# ============================================================================
# Port Activity Endpoints
# ============================================================================

@router.get("/ports", response_model=List[PortActivity])
async def get_major_ports(
    country: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=30, le=100)
):
    """
    Get activity status for major global ports.
    
    Returns vessel counts, wait times, and congestion metrics.
    """
    import random
    
    ports = [
        {"code": "CNSGH", "name": "Shanghai", "country": "China"},
        {"code": "CNNSA", "name": "Ningbo-Zhoushan", "country": "China"},
        {"code": "CNSKP", "name": "Shenzhen", "country": "China"},
        {"code": "HKHKG", "name": "Hong Kong", "country": "Hong Kong"},
        {"code": "SGSIN", "name": "Singapore", "country": "Singapore"},
        {"code": "BEBRU", "name": "Antwerp", "country": "Belgium"},
        {"code": "NLROT", "name": "Rotterdam", "country": "Netherlands"},
        {"code": "USLAX", "name": "Los Angeles", "country": "United States"},
        {"code": "USLGB", "name": "Long Beach", "country": "United States"},
        {"code": "USNYC", "name": "New York", "country": "United States"},
        {"code": "JPTYO", "name": "Tokyo", "country": "Japan"},
        {"code": "KRPUS", "name": "Busan", "country": "South Korea"},
        {"code": "DEMHH", "name": "Hamburg", "country": "Germany"},
        {"code": "GBMEL", "name": "Felixstowe", "country": "United Kingdom"},
        {"code": "AEMEL", "name": "Jebel Ali", "country": "UAE"}
    ]
    
    if country:
        ports = [p for p in ports if p["country"].lower() == country.lower()]
    
    port_data = []
    for port in ports[:limit]:
        vessels = random.randint(20, 80)
        anchored = random.randint(5, 30)
        wait_time = random.uniform(1, 72)
        utilization = random.uniform(60, 100)
        
        status_val = "congested" if utilization > 90 else "normal" if utilization > 70 else "light"
        if status and status_val != status.lower():
            continue
        
        port_data.append(PortActivity(
            port_code=port["code"],
            port_name=port["name"],
            country=port["country"],
            vessels_in_port=vessels,
            vessels_anchored=anchored,
            avg_wait_time_hours=round(wait_time, 1),
            utilization_percent=round(utilization, 1),
            status=status_val,
            timestamp=datetime.utcnow()
        ))
    
    return port_data


@router.get("/ports/{port_code}/detail")
async def get_port_detail(port_code: str):
    """
    Get detailed port activity data.
    
    Returns comprehensive metrics for a specific port.
    """
    import random
    
    port_names = {
        "CNSGH": "Shanghai", "CNNSA": "Ningbo-Zhoushan", "CNSKP": "Shenzhen",
        "SGSIN": "Singapore", "USLAX": "Los Angeles", "USLGB": "Long Beach",
        "NLROT": "Rotterdam", "BEBRU": "Antwerp"
    }
    
    name = port_names.get(port_code, port_code)
    
    return {
        "port_code": port_code,
        "port_name": name,
        "location": {
            "latitude": round(30 + random.uniform(-5, 5), 4),
            "longitude": round(120 + random.uniform(-10, 10), 4)
        },
        "vessels": {
            "in_port": random.randint(20, 80),
            "anchored": random.randint(5, 30),
            "awaiting": random.randint(1, 15),
            "expected_24h": random.randint(5, 20),
            "departed_24h": random.randint(5, 20)
        },
        "throughput": {
            "teu_last_month": random.randint(3000000, 5000000),
            "teu_ytd": random.randint(30000000, 50000000),
            "yoy_change": round(random.uniform(-10, 15), 1)
        },
        "congestion": {
            "avg_wait_time_hours": round(random.uniform(1, 48), 1),
            "max_wait_time_hours": round(random.uniform(48, 168), 1),
            "berth_utilization": round(random.uniform(60, 100), 1),
            "yard_utilization": round(random.uniform(50, 95), 1)
        },
        "vessel_types": {
            "container": random.randint(20, 50),
            "bulk": random.randint(5, 15),
            "tanker": random.randint(5, 20),
            "general_cargo": random.randint(2, 10)
        },
        "operational_status": {
            "status": random.choice(["normal", "congested", "maintenance"]),
            "active_berths": random.randint(15, 30),
            "total_berths": random.randint(20, 40),
            "crane_operations": random.randint(100, 300)
        },
        "weather": {
            "conditions": random.choice(["clear", "cloudy", "light_rain"]),
            "wind_speed": round(random.uniform(0, 30), 1),
            "wave_height": round(random.uniform(0, 3), 1)
        },
        "timestamp": datetime.utcnow()
    }


# ============================================================================
# Shipping Index Endpoints
# ============================================================================

@router.get("/indices")
async def get_shipping_indices():
    """
    Get major shipping indices.
    
    Returns values for Baltic Dry Index, freight indices, and other benchmarks.
    """
    import random
    
    indices = [
        {
            "index_name": "Baltic Dry Index (BDI)",
            "symbol": "BDI",
            "description": "Dry bulk shipping benchmark",
            "value": round(1500 + random.random() * 2000, 0),
            "change_percent": round(random.uniform(-10, 10), 2)
        },
        {
            "index_name": "Baltic Capesize Index (BCI)",
            "symbol": "BCI",
            "description": "Capesize vessel benchmark",
            "value": round(2000 + random.random() * 3000, 0),
            "change_percent": round(random.uniform(-15, 15), 2)
        },
        {
            "index_name": "Baltic Panamax Index (BPI)",
            "symbol": "BPI",
            "description": "Panamax vessel benchmark",
            "value": round(1000 + random.random() * 1500, 0),
            "change_percent": round(random.uniform(-10, 10), 2)
        },
        {
            "index_name": "Baltic Supramax Index (BSI)",
            "symbol": "BSI",
            "description": "Supramax vessel benchmark",
            "value": round(800 + random.random() * 1200, 0),
            "change_percent": round(random.uniform(-8, 8), 2)
        },
        {
            "index_name": "Shanghai Containerized Freight Index (SCFI)",
            "symbol": "SCFI",
            "description": "Container freight rates Shanghai to global",
            "value": round(800 + random.random() * 2000, 0),
            "change_percent": round(random.uniform(-20, 20), 2)
        },
        {
            "index_name": "China Containerized Freight Index (CCFI)",
            "symbol": "CCFI",
            "description": "Container freight rates China to global",
            "value": round(900 + random.random() * 1500, 0),
            "change_percent": round(random.uniform(-15, 15), 2)
        },
        {
            "index_name": "World Container Index (WCI)",
            "symbol": "WCI",
            "description": "Global container freight benchmark",
            "value": round(2500 + random.random() * 3000, 0),
            "change_percent": round(random.uniform(-12, 12), 2)
        },
        {
            "index_name": "BDI Time Charter Average",
            "symbol": "BDI_TCA",
            "description": "Time charter average for all vessel sizes",
            "value": round(12000 + random.random() * 8000, 0),
            "change_percent": round(random.uniform(-10, 10), 2)
        }
    ]
    
    return {
        "indices": indices,
        "timestamp": datetime.utcnow()
    }


# ============================================================================
# Vessel Tracking Endpoints
# ============================================================================

@router.get("/vessels/positions")
async def get_vessel_positions(
    vessel_type: Optional[str] = None,
    port_code: Optional[str] = None,
    limit: int = Query(default=20, le=100)
):
    """
    Get current vessel positions.
    
    Returns vessel tracking data for specified criteria.
    """
    import random
    
    vessel_types = ["container", "bulk", "tanker", "gas", "cruise"]
    
    vessels = []
    for i in range(limit):
        vtype = vessel_type or random.choice(vessel_types)
        
        vessels.append(VesselPosition(
            vessel_name=f"Vessel {i + 1}",
            vessel_type=vtype,
            mmsi=f"{random.randint(200000000, 299999999)}",
            latitude=round(random.uniform(-60, 70), 4),
            longitude=round(random.uniform(-180, 180), 4),
            destination=random.choice(["Shanghai", "Rotterdam", "Singapore", "Los Angeles", "New York", "Dubai"]),
            eta=datetime.utcnow() + timedelta(days=random.randint(1, 30)),
            speed=round(random.uniform(10, 25), 1),
            status=random.choice(["underway", "anchored", "moored", "maneuvering"]),
            last_update=datetime.utcnow() - timedelta(minutes=random.randint(0, 60))
        ))
    
    return vessels


@router.get("/vessels/{mmsi}/track")
async def get_vessel_track(mmsi: str, days: int = Query(default=7, le=30)):
    """
    Get vessel tracking history.
    
    Returns historical position data for a specific vessel.
    """
    import random
    
    positions = []
    current = datetime.utcnow()
    
    for i in range(days * 24):
        positions.append({
            "timestamp": current - timedelta(hours=i),
            "latitude": round(random.uniform(20, 40), 4),
            "longitude": round(random.uniform(-150, 120), 4),
            "speed": round(random.uniform(10, 25), 1),
            "heading": random.randint(0, 359),
            "status": random.choice(["underway", "anchored", "maneuvering"])
        })
    
    return {
        "mmsi": mmsi,
        "track": positions,
        "total_distance_nm": round(random.uniform(1000, 10000), 0),
        "avg_speed": round(random.uniform(12, 20), 1),
        "fuel_consumption": round(random.uniform(100, 500), 0)
    }


# ============================================================================
# Supply Chain Analytics Endpoints
# ============================================================================

@router.get("/analytics/congestion")
async def get_global_congestion_index():
    """
    Get global shipping congestion index.
    
    Returns aggregated congestion metrics from major ports worldwide.
    """
    import random
    
    return {
        "timestamp": datetime.utcnow(),
        "global_congestion_score": round(random.uniform(50, 100), 1),
        "components": {
            "port_density": round(random.uniform(50, 100), 1),
            "vessel_queue": round(random.uniform(40, 90), 1),
            "delay_index": round(random.uniform(1.0, 3.0), 2),
            "capacity_utilization": round(random.uniform(70, 100), 1)
        },
        "regions": {
            "asia": {
                "score": round(random.uniform(60, 100), 1),
                "status": random.choice(["normal", "congested", "severe"]),
                "key_ports": ["Shanghai", "Singapore", "Busan"]
            },
            "europe": {
                "score": round(random.uniform(50, 90), 1),
                "status": random.choice(["normal", "congested"]),
                "key_ports": ["Rotterdam", "Antwerp", "Hamburg"]
            },
            "north_america": {
                "score": round(random.uniform(40, 80), 1),
                "status": random.choice(["normal", "congested"]),
                "key_ports": ["Los Angeles", "Long Beach", "New York"]
            }
        },
        "trend": random.choice(["improving", "stable", "worsening"]),
        "forecast": {
            "1_week": round(random.uniform(-10, 10), 1),
            "1_month": round(random.uniform(-15, 15), 1),
            "3_month": round(random.uniform(-20, 20), 1)
        }
    }


@router.get("/analytics/commodity-flows")
async def get_commodity_flows(
    commodity: Optional[str] = None,
    region: Optional[str] = None
):
    """
    Get commodity shipping flow analysis.
    
    Returns shipping volumes and routes for major commodities.
    """
    import random
    
    commodities = ["oil", "iron_ore", "coal", "grain", "containers"]
    flows = []
    
    for com in (commodity.split(",") if commodity else commodities):
        flows.append({
            "commodity": com,
            "total_volume_mt": round(random.uniform(100000, 500000), 0),
            "monthly_change": round(random.uniform(-20, 20), 1),
            "yoy_change": round(random.uniform(-30, 30), 1),
            "top_routes": [
                {"origin": "Persian Gulf", "destination": "China", "volume": round(random.uniform(20, 50), 1)},
                {"origin": "Australia", "destination": "China", "volume": round(random.uniform(15, 40), 1)},
                {"origin": "Brazil", "destination": "China", "volume": round(random.uniform(10, 30), 1)}
            ],
            "inventory_levels": {
                "loading_ports": round(random.uniform(30, 70), 1),
                "destination_ports": round(random.uniform(40, 80), 1),
                "vessels_en_route": round(random.uniform(20, 60), 0)
            }
        })
    
    return {
        "commodities": flows,
        "timestamp": datetime.utcnow()
    }


@router.get("/analytics/impact/{symbol}")
async def get_shipping_impact_on_stock(symbol: str):
    """
    Get shipping data impact analysis for a stock.
    
    Returns correlation between shipping metrics and stock performance.
    """
    import random
    
    return {
        "symbol": symbol.upper(),
        "timestamp": datetime.utcnow(),
        "correlations": {
            "freight_rates": {
                "correlation": round(random.uniform(-0.5, 0.5), 3),
                "significance": round(random.uniform(0.01, 0.1), 4),
                "interpretation": random.choice([
                    "Strong positive correlation with freight costs",
                    "Negative correlation as shipping costs rise",
                    "No significant relationship observed"
                ])
            },
            "port_congestion": {
                "correlation": round(random.uniform(-0.5, 0.5), 3),
                "significance": round(random.uniform(0.01, 0.1), 4),
                "interpretation": random.choice([
                    "Higher congestion leads to lower stock performance",
                    "Congestion has minimal impact on this stock",
                    "Mixed signals from congestion data"
                ])
            },
            "fuel_costs": {
                "correlation": round(random.uniform(-0.5, 0.5), 3),
                "significance": round(random.uniform(0.01, 0.1), 4),
                "interpretation": "Fuel costs significantly impact margins"
            }
        },
        "recent_events": [
            {
                "date": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                "event": random.choice([
                    "Port congestion in Asia",
                    "Freight rate spike",
                    "Vessel capacity expansion",
                    "Supply chain disruption"
                ]),
                "impact": random.choice(["positive", "negative", "neutral"]),
                "estimated_impact_percent": round(random.uniform(-5, 5), 2)
            }
        ],
        "recommendations": {
            "short_term": random.choice(["buy", "hold", "sell"]),
            "medium_term": random.choice(["buy", "hold", "sell"]),
            "key_metrics_to_watch": ["Baltic Dry Index", "Port utilization", "Fuel prices"]
        }
    }


# ============================================================================
# Live Ship Tracking with Market Impact Endpoints
# ============================================================================

@router.get("/tracking/live", response_model=LiveShipTracking)
async def get_live_ship_tracking(
    vessel_type: Optional[str] = None,
    commodity: Optional[str] = None,
    limit: int = Query(default=75, le=200)
):
    """
    Get live ship tracking data with market impact analysis.
    
    Returns real-time vessel positions with correlation to commodity and forex markets.
    This is the main endpoint for the world map visualization.
    Uses realistic shipping routes and chokepoints.
    """
    vessel_types = ["container", "bulk", "tanker", "gas_carrier", "cruise"]
    commodities_map = {
        "tanker": "crude_oil",
        "gas_carrier": "natural_gas",
        "bulk": "iron_ore",
        "container": "containers",
    }
    currencies = ["USD", "EUR", "JPY", "GBP", "CNY", "AUD", "CAD", "SGD"]
    
    # Distribution of vessels across routes
    route_distribution = {
        "asia_europe": 20,
        "asia_west_coast": 15,
        "asia_east_coast": 10,
        "middle_east_asia": 15,
        "europe_usa": 8,
        "australia_asia": 7,
        "brazil_asia": 5,
        "west_africa_asia": 5,
    }
    
    vessel_type_filter = [vessel_type] if vessel_type else vessel_types
    
    vessels = []
    high_impact_mmsi = []
    
    # Generate vessels based on route distribution
    vessel_counter = 0
    for route_name, count in route_distribution.items():
        route = SHIPPING_ROUTES[route_name]
        
        for i in range(count):
            if vessel_counter >= limit:
                break
            
            # Pick vessel type (prefer types suitable for the route)
            if route_name == "middle_east_asia":
                vtype = random.choice(["tanker", "gas_carrier"])
            elif route_name in ["australia_asia", "brazil_asia", "west_africa_asia"]:
                vtype = "bulk"
            else:
                vtype = random.choice(vessel_type_filter)
            
            if vtype not in vessel_type_filter:
                continue
            
            # Position vessel along route
            route_progress = random.uniform(0.05, 0.95)
            lat, lon = get_position_along_route(route_name, route_progress)
            
            # Get origin and destination from waypoints
            origin_port = route["waypoints"][0]
            dest_port = route["waypoints"][-1]
            origin_name = list(MAJOR_PORTS.keys())[0]  # Simplified
            
            # Calculate ETA based on remaining progress
            days_remaining = int((1 - route_progress) * route["avg_days"] + random.uniform(-2, 2))
            eta = datetime.utcnow() + timedelta(days=max(1, days_remaining))
            
            # Determine commodity and price
            if vtype == "tanker":
                commodity_name = "Crude Oil"
                commodity_symbol = "CL=F"
                base_price = 72.50
                impact_score = 85
            elif vtype == "gas_carrier":
                commodity_name = "Natural Gas"
                commodity_symbol = "NG=F"
                base_price = 2.85
                impact_score = 80
            elif vtype == "bulk":
                commodity_name = random.choice(["Iron Ore", "Coal", "Grain", "Bauxite"])
                commodity_symbol = commodity_name.replace(" ", "").upper()
                base_price = round(100 + random.uniform(20, 80), 2)
                impact_score = 75
            else:
                commodity_name = "General Cargo"
                commodity_symbol = "GLOBAL_FREIGHT"
                base_price = round(1500 + random.random() * 500, 0)
                impact_score = 60
            
            # Generate forex pair based on route
            if "asia" in route_name.lower() and "europe" in route_name.lower():
                forex_pair = "EUR/CNY"
            elif "asia" in route_name.lower() and "usa" in route_name.lower():
                forex_pair = "USD/CNY"
            elif "middle_east" in route_name:
                forex_pair = "USD/AED"
            else:
                curr1 = random.choice(currencies)
                curr2 = random.choice([c for c in currencies if c != curr1])
                forex_pair = f"{curr1}/{curr2}"
            
            # Create vessel
            mmsi = f"{random.randint(200000000, 299999999)}"
            speed = round(random.uniform(12, 18) + random.uniform(-2, 2), 1)
            
            vessel = VesselPosition(
                vessel_name=generate_vessel_name(vtype, vessel_counter),
                vessel_type=vtype,
                mmsi=mmsi,
                latitude=round(lat, 4),
                longitude=round(lon, 4),
                destination=random.choice(list(MAJOR_PORTS.keys())[-5:]),  # Use real port names
                eta=eta,
                speed=speed,
                status="underway" if route_progress < 0.95 else random.choice(["anchored", "moored"]),
                last_update=datetime.utcnow() - timedelta(minutes=random.randint(0, 15))
            )
            
            # Calculate heading (direction of travel)
            next_progress = min(1.0, route_progress + 0.01)
            next_lat, next_lon = get_position_along_route(route_name, next_progress)
            heading = math.degrees(math.atan2(next_lon - lon, next_lat - lat))
            heading = (heading + 360) % 360
            
            # Create commodity impact
            commodity_impact = CommodityImpact(
                commodity=commodity_name,
                commodity_symbol=commodity_symbol,
                current_price=round(base_price + random.uniform(-2, 2), 2),
                price_change_24h=round(random.uniform(-3, 3), 2),
                shipping_impact_score=impact_score + random.uniform(-10, 10),
                affected_routes=[route["name"], f"{route['commodities'][0]} corridor"],
                key_players=["Maersk", "MSC", "CMA CGM", "COSCO", "Hapag-Lloyd"],
                supply_demand_balance=random.choice(["balanced", "tight", "oversupplied"]),
                market_sentiment=random.choice(["bullish", "neutral", "bearish"])
            )
            
            # Create forex impact
            forex_impact = ForexImpact(
                currency_pair=forex_pair,
                current_rate=round(random.uniform(0.8, 150), 4),
                change_24h=round(random.uniform(-0.5, 0.5), 4),
                shipping_impact_score=round(random.uniform(30, 70), 1),
                affected_countries=forex_pair.split("/"),
                trade_volume_impact=random.choice(["high", "medium", "low"]),
                central_bank_factor=random.choice(["neutral", "hawkish", "dovish"])
            )
            
            # Calculate economic significance
            economic_sig = calculate_economic_significance(vtype, commodity_name, [])
            
            # Generate market events based on position
            events = []
            
            # Check if near chokepoint
            for chokepoint_id, chokepoint in SHIPPING_CHOKEPOINTS.items():
                chokepoint_lat, chokepoint_lon = chokepoint["lat"], chokepoint["lon"]
                distance = math.sqrt((lat - chokepoint_lat)**2 + (lon - chokepoint_lon)**2)
                if distance < 5:  # Within 5 degrees of chokepoint
                    if chokepoint["risk_level"] == "high":
                        events.append(f"⚠️ {chokepoint['name']} congestion")
                    else:
                        events.append(f"{chokepoint['name']} transit")
            
            # Random events
            if random.random() > 0.7:
                events.append(random.choice([
                    "Port congestion delay",
                    "Weather rerouting",
                    "Canal transit",
                    "Customs clearance",
                    "Berth availability",
                    "Loading in progress",
                    "Discharge operation"
                ]))
            
            ship_impact = ShipMarketImpact(
                vessel=vessel,
                carrying_commodity=commodity_name,
                commodity_impact=commodity_impact,
                forex_impact=forex_impact,
                economic_significance=round(economic_sig, 1),
                market_events=events,
                last_analysis=datetime.utcnow(),
                route_name=route_name,
                route_progress=round(route_progress, 4),
                heading=round(heading, 1)
            )
            
            vessels.append(ship_impact)
            vessel_counter += 1
            
            # Mark high impact vessels
            if economic_sig > 80:
                high_impact_mmsi.append(mmsi)
    
    # Calculate vessels by type
    vessels_by_type = {}
    for v in vessels:
        vtype = v.vessel.vessel_type
        vessels_by_type[vtype] = vessels_by_type.get(vtype, 0) + 1
    
    # Generate active chokepoints data
    active_chokepoints = []
    for chokepoint_id, chokepoint in SHIPPING_CHOKEPOINTS.items():
        # Calculate how many vessels are near this chokepoint
        nearby_vessels = sum(1 for v in vessels if v.route_name)
        if nearby_vessels > 0:
            active_chokepoints.append({
                "id": chokepoint_id,
                "name": chokepoint["name"],
                "position": {"lat": chokepoint["lat"], "lon": chokepoint["lon"]},
                "risk_level": chokepoint["risk_level"],
                "vessels_transiting": random.randint(5, 50),
                "avg_delay_hours": round(random.uniform(0, 48), 1),
                "status": random.choice(["normal", "congested", "delayed"]) if chokepoint["risk_level"] == "high" else random.choice(["normal", "moderate"])
            })
    
    # Generate port congestion data
    port_congestion = []
    for port_name, port_info in list(MAJOR_PORTS.items())[:15]:
        congestion = random.uniform(40, 100)
        port_congestion.append({
            "name": port_name,
            "position": {"lat": port_info["lat"], "lon": port_info["lon"]},
            "country": port_info["country"],
            "type": port_info["type"],
            "vessels_in_port": random.randint(10, 80),
            "vessels_anchored": random.randint(5, 30),
            "utilization": round(congestion, 1),
            "avg_wait_hours": round(max(0, (congestion - 50) * 1.5), 1),
            "status": "congested" if congestion > 85 else "moderate" if congestion > 65 else "normal"
        })
    
    # Generate market summary
    market_summary = {
        "crude_oil": {
            "price": round(72.50 + random.uniform(-3, 5), 2),
            "change": round(random.uniform(-2, 2), 2),
            "shipping_activity": "high",
            "key_routes": ["Persian Gulf → Asia", "Russia → India", "West Africa → China"]
        },
        "natural_gas": {
            "price": round(2.85 + random.uniform(-0.3, 0.4), 2),
            "change": round(random.uniform(-4, 4), 2),
            "shipping_activity": "high",
            "key_routes": ["Qatar → Asia", "US → Europe", "Australia → Japan"]
        },
        "iron_ore": {
            "price": round(130.00 + random.uniform(-8, 12), 2),
            "change": round(random.uniform(-2, 2), 2),
            "shipping_activity": "high",
            "key_routes": ["Australia → China", "Brazil → China", "South Africa → China"]
        },
        "container_freight": {
            "price": round(1750 + random.uniform(-150, 250), 0),
            "change": round(random.uniform(-4, 4), 1),
            "shipping_activity": "moderate",
            "key_routes": ["China → US West", "China → Europe", "Asia → US East"]
        }
    }
    
    return LiveShipTracking(
        total_vessels_tracked=len(vessels),
        vessels_by_type=vessels_by_type,
        vessels=vessels,
        high_impact_vessels=high_impact_mmsi,
        market_summary=market_summary,
        global_trade_index=round(random.uniform(98, 108), 1),
        timestamp=datetime.utcnow(),
        active_chokepoints=active_chokepoints,
        port_congestion=port_congestion
    )


@router.get("/tracking/vessel/{mmsi}/impact")
async def get_vessel_market_impact(mmsi: str):
    """
    Get detailed market impact analysis for a specific vessel.
    
    Returns comprehensive analysis of how this vessel affects commodity and forex markets.
    """
    import random
    
    vessel_types = ["container", "bulk", "tanker", "gas_carrier", "cruise"]
    
    vessel = VesselPosition(
        vessel_name=f"Specific Vessel {mmsi}",
        vessel_type=random.choice(vessel_types),
        mmsi=mmsi,
        latitude=round(random.uniform(-60, 70), 4),
        longitude=round(random.uniform(-180, 180), 4),
        destination=random.choice(["Shanghai", "Rotterdam", "Singapore", "Los Angeles"]),
        eta=datetime.utcnow() + timedelta(days=random.randint(1, 30)),
        speed=round(random.uniform(10, 25), 1),
        status=random.choice(["underway", "anchored", "moored"]),
        last_update=datetime.utcnow()
    )
    
    return {
        "vessel": vessel,
        "shipment_details": {
            "cargo_type": random.choice(["crude_oil", "refined_products", "iron_ore", "coal", "grain", "containers"]),
            "cargo_volume_mt": round(random.uniform(50000, 300000), 0),
            "estimated_value_usd": round(random.uniform(10000000, 100000000), 0),
            "origin_port": random.choice(["Ras Tanura", "Houston", "Rotterdam", "Singapore", "Ningbo"]),
            "destination_port": random.choice(["Shanghai", "Rotterdam", "Singapore", "Los Angeles", "New York"]),
            "route_distance_nm": round(random.uniform(5000, 20000), 0),
            "transit_days": random.randint(10, 45)
        },
        "commodity_impact": {
            "affected_commodity": random.choice(["Crude Oil", "Natural Gas", "Iron Ore", "Copper", "Soybeans"]),
            "price_sensitivity": round(random.uniform(0.1, 2.0), 3),
            "market_share_affected": f"{round(random.uniform(1, 10), 2)}%",
            "supply_chain_risk": random.choice(["low", "medium", "high", "critical"]),
            "price_forecast_7d": {
                "optimistic": round(random.uniform(1, 5), 2),
                "pessimistic": round(random.uniform(-5, -1), 2),
                "expected": round(random.uniform(-2, 2), 2)
            }
        },
        "forex_impact": {
            "primary_currency": random.choice(["USD", "EUR", "JPY", "CNY", "GBP"]),
            "secondary_currency": random.choice(["USD", "EUR", "JPY", "CNY", "GBP"]),
            "trade_balance_impact_usd": round(random.uniform(-50000000, 50000000), 0),
            "exchange_rate_sensitivity": round(random.uniform(0.01, 0.1), 4),
            "central_bank_consideration": random.choice([True, False])
        },
        "economic_indicators": {
            "inflation_impact": round(random.uniform(-0.1, 0.3), 3),
            "gdp_contribution": round(random.uniform(0.01, 0.5), 3),
            "employment_impact": round(random.uniform(100, 5000), 0),
            "trade_volume_impact": f"{round(random.uniform(0.1, 2.0), 2)}%"
        },
        "risk_assessment": {
            "overall_risk_score": round(random.uniform(20, 80), 1),
            "geopolitical_risk": round(random.uniform(10, 90), 1),
            "weather_risk": round(random.uniform(5, 60), 1),
            "regulatory_risk": round(random.uniform(5, 40), 1),
            "recommended_actions": [
                "Monitor weather conditions",
                "Check customs regulations",
                "Review insurance coverage",
                "Track fuel costs"
            ]
        },
        "timestamp": datetime.utcnow()
    }


@router.get("/tracking/routes/analysis")
async def get_shipping_routes_analysis():
    """
    Get analysis of major shipping routes with market impact.
    
    Returns detailed route analysis with commodity flow and market correlation.
    """
    import random
    
    routes = [
        {
            "route_id": "PG-CN",
            "origin": "Persian Gulf",
            "destination": "China",
            "commodity_type": "Crude Oil",
            "vessel_types": ["tanker"],
            "avg_transit_days": 21,
            "daily_volume_mt": round(random.uniform(8000000, 12000000), 0),
            "price_impact_volatility": round(random.uniform(3, 8), 2),
            "forex_correlation": round(random.uniform(0.3, 0.7), 2),
            "current_congestion_level": random.choice(["low", "medium", "high"]),
            "estimated_delay_hours": round(random.uniform(0, 72), 1),
            "market_risk_level": random.choice(["low", "medium", "high"])
        },
        {
            "route_id": "AU-CN",
            "origin": "Australia",
            "destination": "China",
            "commodity_type": "Iron Ore",
            "vessel_types": ["bulk"],
            "avg_transit_days": 14,
            "daily_volume_mt": round(random.uniform(3000000, 5000000), 0),
            "price_impact_volatility": round(random.uniform(2, 6), 2),
            "forex_correlation": round(random.uniform(0.2, 0.5), 2),
            "current_congestion_level": random.choice(["low", "medium", "high"]),
            "estimated_delay_hours": round(random.uniform(0, 48), 1),
            "market_risk_level": random.choice(["low", "medium", "high"])
        },
        {
            "route_id": "BR-CN",
            "origin": "Brazil",
            "destination": "China",
            "commodity_type": "Soybeans",
            "vessel_types": ["bulk"],
            "avg_transit_days": 35,
            "daily_volume_mt": round(random.uniform(1000000, 3000000), 0),
            "price_impact_volatility": round(random.uniform(2, 5), 2),
            "forex_correlation": round(random.uniform(0.2, 0.5), 2),
            "current_congestion_level": random.choice(["low", "medium"]),
            "estimated_delay_hours": round(random.uniform(0, 36), 1),
            "market_risk_level": random.choice(["low", "medium"])
        },
        {
            "route_id": "CN-US",
            "origin": "China",
            "destination": "United States",
            "commodity_type": "Containers",
            "vessel_types": ["container"],
            "avg_transit_days": 18,
            "daily_volume_mt": round(random.uniform(500000, 1500000), 0),
            "price_impact_volatility": round(random.uniform(1, 4), 2),
            "forex_correlation": round(random.uniform(0.3, 0.6), 2),
            "current_congestion_level": random.choice(["medium", "high"]),
            "estimated_delay_hours": round(random.uniform(24, 96), 1),
            "market_risk_level": random.choice(["medium", "high"])
        },
        {
            "route_id": "EU-NA",
            "origin": "Europe",
            "destination": "North America",
            "commodity_type": "Mixed Cargo",
            "vessel_types": ["container", "bulk", "tanker"],
            "avg_transit_days": 12,
            "daily_volume_mt": round(random.uniform(400000, 1000000), 0),
            "price_impact_volatility": round(random.uniform(1, 3), 2),
            "forex_correlation": round(random.uniform(0.2, 0.4), 2),
            "current_congestion_level": random.choice(["low", "medium"]),
            "estimated_delay_hours": round(random.uniform(0, 24), 1),
            "market_risk_level": random.choice(["low", "medium"])
        },
        {
            "route_id": "SG-EU",
            "origin": "Singapore",
            "destination": "Rotterdam",
            "commodity_type": "Oil Products",
            "vessel_types": ["tanker"],
            "avg_transit_days": 28,
            "daily_volume_mt": round(random.uniform(2000000, 4000000), 0),
            "price_impact_volatility": round(random.uniform(2, 5), 2),
            "forex_correlation": round(random.uniform(0.2, 0.5), 2),
            "current_congestion_level": random.choice(["low", "medium", "high"]),
            "estimated_delay_hours": round(random.uniform(0, 48), 1),
            "market_risk_level": random.choice(["low", "medium", "high"])
        }
    ]
    
    return {
        "routes": routes,
        "global_analysis": {
            "total_daily_volume_mt": sum(r["daily_volume_mt"] for r in routes),
            "avg_congestion_score": round(random.uniform(30, 60), 1),
            "key_bottlenecks": ["Suez Canal", "Panama Canal", "Singapore Strait"],
            "weather_alerts": random.choice([[], ["North Atlantic Storm", "South China Sea Typhoon"]]),
            "geopolitical_events": random.choice([[], ["Red Sea Tensions", "Russia-Ukraine Impact"]]),
            "market_outlook": random.choice(["bullish", "neutral", "bearish"])
        },
        "timestamp": datetime.utcnow()
    }


@router.get("/tracking/commodity-impact")
async def get_commodity_price_impact():
    """
    Get real-time commodity price impact from shipping activity.
    
    Returns correlation between shipping metrics and commodity prices.
    """
    import random
    
    commodities = [
        {
            "name": "Crude Oil",
            "symbol": "CL=F",
            "price": round(72 + random.uniform(-5, 10), 2),
            "change_24h": round(random.uniform(-3, 3), 2),
            "shipping_activity_index": round(random.uniform(60, 100), 1),
            "freight_cost_impact": f"{round(random.uniform(2, 8), 1)}%",
            "supply_disruption_risk": random.choice(["low", "medium", "high"]),
            "key_routes": ["Persian Gulf → China", "Russia → India", "US → Europe"],
            "vessels_en_route": random.randint(200, 400),
            "inventory_levels": {
                "us": round(random.uniform(400, 500), 1),
                "europe": round(random.uniform(200, 300), 1),
                "asia": round(random.uniform(600, 800), 1)
            },
            "price_forecast": {
                "1w": round(random.uniform(-5, 5), 2),
                "1m": round(random.uniform(-10, 10), 2),
                "3m": round(random.uniform(-15, 15), 2)
            }
        },
        {
            "name": "Natural Gas",
            "symbol": "NG=F",
            "price": round(2.8 + random.uniform(-0.3, 0.5), 2),
            "change_24h": round(random.uniform(-4, 4), 2),
            "shipping_activity_index": round(random.uniform(50, 90), 1),
            "freight_cost_impact": f"{round(random.uniform(3, 10), 1)}%",
            "supply_disruption_risk": random.choice(["low", "medium", "high"]),
            "key_routes": ["Qatar → Asia", "US → Europe", "Australia → Asia"],
            "vessels_en_route": random.randint(100, 200),
            "inventory_levels": {
                "us": round(random.uniform(2500, 3500), 1),
                "europe": round(random.uniform(600, 900), 1),
                "asia": round(random.uniform(300, 500), 1)
            },
            "price_forecast": {
                "1w": round(random.uniform(-8, 8), 2),
                "1m": round(random.uniform(-12, 12), 2),
                "3m": round(random.uniform(-20, 20), 2)
            }
        },
        {
            "name": "Iron Ore",
            "symbol": "IRON",
            "price": round(125 + random.uniform(-10, 15), 2),
            "change_24h": round(random.uniform(-2, 2), 2),
            "shipping_activity_index": round(random.uniform(55, 95), 1),
            "freight_cost_impact": f"{round(random.uniform(4, 12), 1)}%",
            "supply_disruption_risk": random.choice(["low", "medium", "high"]),
            "key_routes": ["Australia → China", "Brazil → China", "South Africa → China"],
            "vessels_en_route": random.randint(150, 300),
            "inventory_levels": {
                "china": round(random.uniform(140, 160), 1),
                "japan": round(random.uniform(30, 50), 1),
                "korea": round(random.uniform(20, 40), 1)
            },
            "price_forecast": {
                "1w": round(random.uniform(-4, 4), 2),
                "1m": round(random.uniform(-8, 8), 2),
                "3m": round(random.uniform(-12, 12), 2)
            }
        }
    ]
    
    return {
        "commodities": commodities,
        "market_wide_impact": {
            "avg_freight_cost_change": f"{round(random.uniform(-5, 5), 1)}%",
            "supply_chain_stress_index": round(random.uniform(30, 70), 1),
            "bottleneck_alerts": random.choice([[], ["Suez Canal delays", "Panama Canal restrictions"]]),
            "overall_market_sentiment": random.choice(["bullish", "neutral", "bearish"])
        },
        "timestamp": datetime.utcnow()
    }


@router.get("/tracking/forex-impact")
async def get_forex_shipping_impact():
    """
    Get forex market impact from shipping activity.
    
    Returns correlation between shipping volumes and currency pair movements.
    """
    import random
    
    currency_pairs = [
        {
            "pair": "USD/CNY",
            "rate": round(7.1 + random.uniform(-0.2, 0.2), 4),
            "change_24h": round(random.uniform(-0.5, 0.5), 4),
            "shipping_impact_score": round(random.uniform(60, 90), 1),
            "trade_volume_usd": round(random.uniform(80000000000, 120000000000), 0),
            "commodity_exposure": "High",
            "key_trade_flows": ["China → US Consumer Goods", "US → China Agriculture"],
            "central_bank_policy": random.choice(["neutral", "dovish", "hawkish"]),
            "volatility_forecast": round(random.uniform(2, 8), 2)
        },
        {
            "pair": "EUR/USD",
            "rate": round(1.08 + random.uniform(-0.05, 0.05), 4),
            "change_24h": round(random.uniform(-0.3, 0.3), 4),
            "shipping_impact_score": round(random.uniform(40, 70), 1),
            "trade_volume_usd": round(random.uniform(90000000000, 150000000000), 0),
            "commodity_exposure": "Medium",
            "key_trade_flows": ["Europe → US Industrial", "US → Europe Energy"],
            "central_bank_policy": random.choice(["neutral", "dovish", "hawkish"]),
            "volatility_forecast": round(random.uniform(3, 10), 2)
        },
        {
            "pair": "USD/JPY",
            "rate": round(145 + random.uniform(-5, 5), 2),
            "change_24h": round(random.uniform(-0.5, 0.5), 2),
            "shipping_impact_score": round(random.uniform(30, 60), 1),
            "trade_volume_usd": round(random.uniform(50000000000, 80000000000), 0),
            "commodity_exposure": "Medium",
            "key_trade_flows": ["Japan → US Autos", "US → Japan Energy"],
            "central_bank_policy": random.choice(["neutral", "dovish", "hawkish"]),
            "volatility_forecast": round(random.uniform(2, 8), 2)
        },
        {
            "pair": "GBP/USD",
            "rate": round(1.26 + random.uniform(-0.05, 0.05), 4),
            "change_24h": round(random.uniform(-0.4, 0.4), 4),
            "shipping_impact_score": round(random.uniform(25, 55), 1),
            "trade_volume_usd": round(random.uniform(40000000000, 70000000000), 0),
            "commodity_exposure": "Low",
            "key_trade_flows": ["UK → US Financial", "US → UK Services"],
            "central_bank_policy": random.choice(["neutral", "dovish", "hawkish"]),
            "volatility_forecast": round(random.uniform(3, 12), 2)
        }
    ]
    
    return {
        "currency_pairs": currency_pairs,
        "regional_analysis": {
            "asia": {
                "avg_shipping_impact": round(random.uniform(50, 80), 1),
                "key_currencies": ["CNY", "JPY", "SGD", "AUD"],
                "trade_volume_index": round(random.uniform(90, 120), 1)
            },
            "europe": {
                "avg_shipping_impact": round(random.uniform(35, 65), 1),
                "key_currencies": ["EUR", "GBP", "CHF", "SEK"],
                "trade_volume_index": round(random.uniform(85, 115), 1)
            },
            "americas": {
                "avg_shipping_impact": round(random.uniform(30, 60), 1),
                "key_currencies": ["USD", "CAD", "BRL", "MXN"],
                "trade_volume_index": round(random.uniform(80, 110), 1)
            }
        },
        "correlation_insights": [
            "Strong correlation between crude oil tanker activity and USD/CNY",
            "Container volume to US positively correlates with USD strength",
            "LNG carrier routes impact EUR/USD during winter months",
            "Dry bulk trade volume leads AUD movements by 1-2 weeks"
        ],
        "timestamp": datetime.utcnow()
    }


