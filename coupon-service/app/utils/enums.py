from enum import Enum


class CouponState(str, Enum):
    """Coupon lifecycle states"""
    UNASSIGNED = "UNASSIGNED"
    ASSIGNED = "ASSIGNED"
    LOCKED = "LOCKED"
    REDEEMED = "REDEEMED"
    EXPIRED = "EXPIRED"
    
    @classmethod
    def get_valid_transitions(cls, from_state: "CouponState") -> list["CouponState"]:
        """Get valid state transitions from current state"""
        transitions = {
            cls.UNASSIGNED: [cls.ASSIGNED, cls.EXPIRED],
            cls.ASSIGNED: [cls.LOCKED, cls.REDEEMED, cls.EXPIRED],
            cls.LOCKED: [cls.ASSIGNED, cls.EXPIRED],  # Lock cannot redeem, must unlock first
            cls.REDEEMED: [],  # Terminal state
            cls.EXPIRED: [],   # Terminal state
        }
        return transitions.get(from_state, [])
    
    @classmethod
    def is_valid_transition(cls, from_state: "CouponState", to_state: "CouponState") -> bool:
        """Check if state transition is valid"""
        return to_state in cls.get_valid_transitions(from_state)
