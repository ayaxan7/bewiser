from typing import Optional


def r(x: Optional[float], mult: int = 100, nd: int = 2) -> Optional[float]:
    """Safe rounding helper for percentage values."""
    return round(x * mult, nd) if x is not None else None
