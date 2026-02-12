"""
Financial Intelligence Platform - Alerts Endpoints

API endpoints for managing user alerts and notifications.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import uuid

from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ============================================================================
# Models
# ============================================================================

class AlertCondition(BaseModel):
    """Alert condition model."""
    field: str
    operator: str  # gt, lt, gte, lte, eq, cross_above, cross_below
    value: float


class AlertNotification(BaseModel):
    """Alert notification model."""
    channel: str  # email, sms, push, webhook
    settings: Dict[str, Any]


class AlertBase(BaseModel):
    """Base alert model."""
    name: str
    description: Optional[str]
    alert_type: str
    conditions: List[AlertCondition]
    condition_logic: str = "AND"
    symbols: List[str]
    asset_types: Optional[List[str]]
    enabled: bool = True
    notifications: List[AlertNotification]


class AlertCreate(AlertBase):
    """Alert creation model."""
    pass


class AlertUpdate(BaseModel):
    """Alert update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[List[AlertCondition]] = None
    enabled: Optional[bool] = None
    notifications: Optional[List[AlertNotification]] = None


class AlertResponse(AlertBase):
    """Alert response model."""
    id: str
    user_id: str
    status: str
    last_triggered_at: Optional[datetime]
    trigger_count: int
    created_at: datetime
    updated_at: datetime


class AlertTrigger(BaseModel):
    """Alert trigger event model."""
    alert_id: str
    triggered_at: datetime
    triggered_value: float
    message: str
    acknowledged: bool = False


# ============================================================================
# Alerts CRUD Endpoints
# ============================================================================

@router.get("/")
async def get_alerts(
    status: Optional[str] = None,
    alert_type: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    Get user's alerts.
    
    Returns list of alerts with optional filtering.
    """
    # Mock alerts data
    alerts = [
        {
            "id": str(uuid.uuid4()),
            "name": "AAPL Price Alert",
            "description": "Alert when AAPL crosses $200",
            "alert_type": "price",
            "conditions": [{"field": "price", "operator": "cross_above", "value": 200}],
            "condition_logic": "AND",
            "symbols": ["AAPL"],
            "asset_types": ["stock"],
            "enabled": True,
            "notifications": [{"channel": "push", "settings": {}}],
            "status": "active",
            "last_triggered_at": datetime.utcnow(),
            "trigger_count": 5,
            "created_at": datetime.utcnow() - timedelta(days=30),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Market News Alert",
            "description": "Breaking news about tech stocks",
            "alert_type": "news",
            "conditions": [{"field": "sentiment", "operator": "lt", "value": -0.5}],
            "condition_logic": "AND",
            "symbols": ["AAPL", "MSFT", "GOOGL"],
            "asset_types": ["stock"],
            "enabled": True,
            "notifications": [{"channel": "email", "settings": {}}],
            "status": "active",
            "last_triggered_at": datetime.utcnow() - timedelta(hours=2),
            "trigger_count": 12,
            "created_at": datetime.utcnow() - timedelta(days=60),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Apply filters
    if status:
        alerts = [a for a in alerts if a["status"] == status]
    if alert_type:
        alerts = [a for a in alerts if a["alert_type"] == alert_type]
    
    return {
        "alerts": alerts[offset:offset + limit],
        "total": len(alerts),
        "limit": limit,
        "offset": offset
    }


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str):
    """
    Get a specific alert.
    
    Returns alert details including trigger history.
    """
    # Mock single alert
    alert = {
        "id": alert_id,
        "user_id": "user_123",
        "name": "AAPL Price Alert",
        "description": "Alert when AAPL crosses $200",
        "alert_type": "price",
        "conditions": [{"field": "price", "operator": "cross_above", "value": 200}],
        "condition_logic": "AND",
        "symbols": ["AAPL"],
        "asset_types": ["stock"],
        "enabled": True,
        "notifications": [{"channel": "push", "settings": {}}],
        "status": "active",
        "last_triggered_at": datetime.utcnow(),
        "trigger_count": 5,
        "created_at": datetime.utcnow() - timedelta(days=30),
        "updated_at": datetime.utcnow()
    }
    
    return AlertResponse(**alert)


@router.post("/")
async def create_alert(alert: AlertCreate):
    """
    Create a new alert.
    
    Returns created alert with ID.
    """
    alert_id = str(uuid.uuid4())
    
    created = {
        "id": alert_id,
        "user_id": "user_123",  # Would come from auth
        "name": alert.name,
        "description": alert.description,
        "alert_type": alert.alert_type,
        "conditions": [c.dict() for c in alert.conditions],
        "condition_logic": alert.condition_logic,
        "symbols": alert.symbols,
        "asset_types": alert.asset_types,
        "enabled": alert.enabled,
        "notifications": [n.dict() for n in alert.notifications],
        "status": "active",
        "last_triggered_at": None,
        "trigger_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    logger.info(f"Created alert: {alert_id}")
    
    return AlertResponse(**created)


@router.put("/{alert_id}")
async def update_alert(alert_id: str, update: AlertUpdate):
    """
    Update an existing alert.
    
    Returns updated alert.
    """
    # Mock update
    updated = {
        "id": alert_id,
        "user_id": "user_123",
        "name": update.name or "Updated Alert",
        "description": update.description,
        "alert_type": "price",
        "conditions": [c.dict() for c in update.conditions] if update.conditions else [],
        "condition_logic": "AND",
        "symbols": ["AAPL"],
        "asset_types": ["stock"],
        "enabled": update.enabled if update.enabled is not None else True,
        "notifications": [n.dict() for n in update.notifications] if update.notifications else [],
        "status": "active",
        "last_triggered_at": datetime.utcnow(),
        "trigger_count": 5,
        "created_at": datetime.utcnow() - timedelta(days=30),
        "updated_at": datetime.utcnow()
    }
    
    return AlertResponse(**updated)


@router.delete("/{alert_id}")
async def delete_alert(alert_id: str):
    """
    Delete an alert.
    
    Returns confirmation of deletion.
    """
    logger.info(f"Deleting alert: {alert_id}")
    
    return {
        "status": "deleted",
        "alert_id": alert_id,
        "deleted_at": datetime.utcnow()
    }


@router.post("/{alert_id}/pause")
async def pause_alert(alert_id: str):
    """
    Pause an alert.
    
    Returns updated alert status.
    """
    return {
        "alert_id": alert_id,
        "status": "paused",
        "paused_at": datetime.utcnow()
    }


@router.post("/{alert_id}/resume")
async def resume_alert(alert_id: str):
    """
    Resume a paused alert.
    
    Returns updated alert status.
    """
    return {
        "alert_id": alert_id,
        "status": "active",
        "resumed_at": datetime.utcnow()
    }


# ============================================================================
# Alert Types Endpoints
# ============================================================================

@router.get("/types")
async def get_alert_types():
    """
    Get available alert types.
    
    Returns list of supported alert types with descriptions.
    """
    alert_types = [
        {
            "type": "price",
            "name": "Price Alert",
            "description": "Triggered when price crosses a threshold",
            "fields": ["price", "change", "change_percent", "volume"],
            "operators": ["gt", "lt", "gte", "lte", "cross_above", "cross_below"],
            "supported_assets": ["stock", "forex", "commodity", "crypto"]
        },
        {
            "type": "volume",
            "name": "Volume Alert",
            "description": "Triggered on unusual volume",
            "fields": ["volume", "volume_ratio", "avg_volume"],
            "operators": ["gt", "lt", "gte", "lte"],
            "supported_assets": ["stock", "etf"]
        },
        {
            "type": "news",
            "name": "News Alert",
            "description": "Triggered when news matches criteria",
            "fields": ["sentiment", "sentiment_score", "relevance"],
            "operators": ["lt", "gt", "eq"],
            "supported_assets": ["all"]
        },
        {
            "type": "earnings",
            "name": "Earnings Alert",
            "description": "Triggered on earnings announcements",
            "fields": ["eps", "revenue", "growth"],
            "operators": ["gt", "lt"],
            "supported_assets": ["stock"]
        },
        {
            "type": "macro",
            "name": "Macro Alert",
            "description": "Triggered on economic data releases",
            "fields": ["actual", "forecast", "surprise"],
            "operators": ["gt", "lt", "cross_above", "cross_below"],
            "supported_assets": ["forex", "bond", "commodity"]
        },
        {
            "type": "sentiment",
            "name": "Sentiment Alert",
            "description": "Triggered on sentiment changes",
            "fields": ["sentiment_score", "mention_volume"],
            "operators": ["gt", "lt", "cross_above", "cross_below"],
            "supported_assets": ["stock", "crypto"]
        },
        {
            "type": "correlation",
            "name": "Correlation Alert",
            "description": "Triggered when correlation breaks down",
            "fields": ["correlation", "correlation_change"],
            "operators": ["lt", "gt"],
            "supported_assets": ["stock"]
        },
        {
            "type": "technical",
            "name": "Technical Indicator Alert",
            "description": "Triggered on technical signals",
            "fields": ["rsi", "macd", "moving_average", "bollinger"],
            "operators": ["gt", "lt", "cross_above", "cross_below"],
            "supported_assets": ["stock", "crypto"]
        }
    ]
    
    return {"alert_types": alert_types}


# ============================================================================
# Trigger History Endpoints
# ============================================================================

@router.get("/{alert_id}/history")
async def get_alert_history(
    alert_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    Get alert trigger history.
    
    Returns list of past alert triggers.
    """
    import random
    
    triggers = []
    for i in range(limit):
        triggers.append({
            "id": str(uuid.uuid4()),
            "alert_id": alert_id,
            "triggered_at": datetime.utcnow() - timedelta(hours=i * 6),
            "triggered_value": round(150 + random.uniform(-10, 20), 2),
            "message": f"Alert triggered: Price crossed ${round(150 + random.uniform(-10, 20), 2)}",
            "condition_met": f"price > ${200 - random.randint(0, 50)}",
            "acknowledged": i > 5,
            "acknowledged_at": datetime.utcnow() - timedelta(hours=i * 6 + 1) if i > 5 else None,
            "notifications_sent": random.sample(["push", "email", "sms"], k=random.randint(1, 2))
        })
    
    return {
        "alert_id": alert_id,
        "triggers": triggers,
        "total": len(triggers),
        "limit": limit,
        "offset": offset
    }


@router.post("/{alert_id}/acknowledge/{trigger_id}")
async def acknowledge_trigger(alert_id: str, trigger_id: str):
    """
    Acknowledge an alert trigger.
    
    Returns confirmation.
    """
    return {
        "trigger_id": trigger_id,
        "alert_id": alert_id,
        "acknowledged": True,
        "acknowledged_at": datetime.utcnow()
    }


# ============================================================================
# Notification Channels Endpoints
# ============================================================================

@router.get("/channels")
async def get_notification_channels():
    """
    Get available notification channels.
    
    Returns list of supported notification methods.
    """
    channels = [
        {
            "channel": "push",
            "name": "Push Notification",
            "description": "Mobile and browser push notifications",
            "settings": ["sound", "vibration", " Quiet hours"],
            "enabled": True
        },
        {
            "channel": "email",
            "name": "Email",
            "description": "Email notifications",
            "settings": ["frequency", "digest", "format"],
            "enabled": True
        },
        {
            "channel": "sms",
            "name": "SMS",
            "description": "Text message notifications",
            "settings": ["phone_number"],
            "enabled": True
        },
        {
            "channel": "webhook",
            "name": "Webhook",
            "description": "HTTP callbacks to external services",
            "settings": ["url", "headers", "method", "auth"],
            "enabled": True
        },
        {
            "channel": "slack",
            "name": "Slack",
            "description": "Slack channel notifications",
            "settings": ["webhook_url", "channel"],
            "enabled": False
        },
        {
            "channel": "discord",
            "name": "Discord",
            "description": "Discord channel notifications",
            "settings": ["webhook_url", "channel"],
            "enabled": False
        }
    ]
    
    return {"channels": channels}


# ============================================================================
# Preset Alerts Endpoints
# ============================================================================

@router.get("/presets")
async def get_alert_presets():
    """
    Get predefined alert presets.
    
    Returns commonly used alert configurations.
    """
    presets = [
        {
            "id": "price_spike",
            "name": "Price Spike Alert",
            "description": "Alert when a stock moves more than 5% in a day",
            "alert_type": "price",
            "conditions": [
                {"field": "change_percent", "operator": "gt", "value": 5}
            ],
            "notifications": ["push", "email"]
        },
        {
            "id": "volume_surge",
            "name": "Volume Surge Alert",
            "description": "Alert when volume is 3x the average",
            "alert_type": "volume",
            "conditions": [
                {"field": "volume_ratio", "operator": "gt", "value": 3}
            ],
            "notifications": ["push"]
        },
        {
            "id": "earnings_beat",
            "name": "Earnings Beat Alert",
            "description": "Alert when EPS beats estimates",
            "alert_type": "earnings",
            "conditions": [
                {"field": "eps_surprise_percent", "operator": "gt", "value": 5}
            ],
            "notifications": ["push", "email"]
        },
        {
            "id": "macro_surprise",
            "name": "Macro Surprise Alert",
            "description": "Alert on significant economic data surprises",
            "alert_type": "macro",
            "conditions": [
                {"field": "surprise", "operator": "gt", "value": 0.5}
            ],
            "notifications": ["push", "sms"]
        },
        {
            "id": "sentiment_shift",
            "name": "Sentiment Shift Alert",
            "description": "Alert when sentiment changes significantly",
            "alert_type": "sentiment",
            "conditions": [
                {"field": "sentiment_change", "operator": "gt", "value": 0.3}
            ],
            "notifications": ["email"]
        }
    ]
    
    return {"presets": presets}

