"""
Base classes for payment gateway adapters - Fashion-Website
Ported from ElectroHub - adapted for Django
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


class PaymentGatewayError(Exception):
    """Raised when a provider call fails before a local state change is possible."""

    def __init__(self, message: str, *, debug_id: Optional[str] = None) -> None:
        super().__init__(message)
        self.debug_id = debug_id


@dataclass(frozen=True)
class GatewayOutcome:
    """Provider result normalised to the local payment state machine."""
    status: str  # paid | pending | failed | refunded
    provider_status: Optional[str] = None
    provider_txn_id: Optional[str] = None
    amount_minor: Optional[int] = None
    currency: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)