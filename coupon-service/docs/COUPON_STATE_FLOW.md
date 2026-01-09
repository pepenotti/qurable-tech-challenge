# Coupon State Flow (Corrected)

## State Machine

```
UNASSIGNED ──────► ASSIGNED ──────► LOCKED
                       │               │
                       │               │
                       ▼               ▼
                   REDEEMED ◄──── ASSIGNED
                                 (unlock)
                       │
                       ▼
                   (terminal)
```

## Valid State Transitions

### UNASSIGNED
- ✅ → ASSIGNED (when assigned to a user)
- ✅ → EXPIRED (if book expires)

### ASSIGNED
- ✅ → LOCKED (user locks for reservation)
- ✅ → REDEEMED (user redeems directly)
- ✅ → EXPIRED (if book expires)

### LOCKED
- ✅ → ASSIGNED (user unlocks - returns to assigned state)
- ✅ → EXPIRED (if book expires)
- ❌ → REDEEMED (CANNOT redeem while locked - must unlock first!)

### REDEEMED
- ❌ Terminal state (no further transitions)

### EXPIRED
- ❌ Terminal state (no further transitions)

## User Actions by State

### ASSIGNED Coupon
**Actions Available:**
1. **✅ Redeem** - Immediately redeem the coupon (moves to REDEEMED)
2. **🔒 Lock (Optional)** - Reserve the coupon temporarily (moves to LOCKED)

**Use Cases:**
- Direct redemption: User wants to use the coupon immediately
- Lock first: User wants to hold the coupon while completing purchase

### LOCKED Coupon
**Actions Available:**
1. **🔓 Unlock to Redeem** - Unlock the coupon (moves back to ASSIGNED)

**NOT Available:**
- ❌ Cannot redeem while locked

**Message Shown:**
- "🔒 Locked - Cannot redeem until unlocked"

**Use Cases:**
- User locked a coupon but changed their mind
- Lock expired and user needs to unlock to proceed
- User wants to release the reservation

### REDEEMED Coupon
**Actions Available:**
- None (terminal state)

**Display:**
- Shows redemption timestamp
- No action buttons

## Lock Purpose

The **LOCK** state serves as a temporary reservation:
- Prevents other users from claiming the coupon (in multi-user scenarios)
- Gives user time to complete a purchase/action
- Prevents concurrent redemption attempts
- **Does NOT allow redemption** - must unlock first

## Correct Flow Examples

### Flow 1: Direct Redemption
```
ASSIGNED → Click "✅ Redeem" → REDEEMED ✅
```

### Flow 2: Lock then Change Mind
```
ASSIGNED → Click "🔒 Lock" → LOCKED → Click "🔓 Unlock" → ASSIGNED → Click "✅ Redeem" → REDEEMED ✅
```

### Flow 3: Incorrect (Now Blocked)
```
ASSIGNED → Click "🔒 Lock" → LOCKED → Try "✅ Redeem" → ❌ ERROR
Error: "Cannot redeem coupon in state LOCKED. Unlock the coupon first."
```

## Backend Validation

The backend enforces these rules at the service level:

**File:** `app/services/redemption_service.py`
```python
# Validate state (must be ASSIGNED, or already REDEEMED for multi-use)
# LOCKED coupons cannot be redeemed - must unlock first
valid_states = [CouponState.ASSIGNED]
if book.allow_multi_redemption:
    valid_states.append(CouponState.REDEEMED)

if coupon.state not in valid_states:
    raise InvalidStateTransitionException(
        f"Cannot redeem coupon in state {coupon.state}. "
        f"{'Unlock the coupon first.' if coupon.state == CouponState.LOCKED else ''}"
    )
```

## Frontend Display

**File:** `frontend/src/views/CouponsView.vue`

### ASSIGNED State
- Shows: "✅ Redeem" button (primary action)
- Shows: "🔒 Lock (Optional)" button (secondary action)

### LOCKED State
- Shows: "🔓 Unlock to Redeem" button
- Shows: "🔒 Locked - Cannot redeem until unlocked" message
- Does NOT show: Redeem button

### REDEEMED State
- Shows: "✅ Redeemed" text with timestamp
- No action buttons

## Testing Checklist

- [ ] ✅ Can redeem ASSIGNED coupon directly
- [ ] ✅ Can lock ASSIGNED coupon
- [ ] ✅ Can unlock LOCKED coupon (returns to ASSIGNED)
- [ ] ✅ Can redeem after unlocking
- [ ] ❌ Cannot redeem LOCKED coupon (button not shown)
- [ ] ❌ Backend rejects redemption of LOCKED coupon with helpful error
