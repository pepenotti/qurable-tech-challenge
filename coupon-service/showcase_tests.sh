#!/bin/bash

# 🎯 Coupon Service - Showcase Test Script
# This script demonstrates all key features and validation

BASE_URL="http://localhost:8000/api/v1"

echo "═══════════════════════════════════════════════════════════"
echo "🎯 COUPON SERVICE - SHOWCASE TEST SUITE"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Login as alice
echo -e "${BLUE}📝 Test 1: Authentication${NC}"
echo "Logging in as alice@example.com..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"demo123"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

if [ -z "$TOKEN" ]; then
  echo -e "${RED}❌ Login failed${NC}"
  exit 1
fi

echo -e "${GREEN}✅ Login successful${NC}"
echo ""

# Get alice's coupons
echo -e "${BLUE}📝 Test 2: Get User Coupons${NC}"
COUPONS_RESPONSE=$(curl -s -X GET "$BASE_URL/users/me/coupons" \
  -H "Authorization: Bearer $TOKEN")

# Extract first ASSIGNED coupon
ASSIGNED_CODE=$(echo $COUPONS_RESPONSE | grep -o '"code":"[^"]*","book_id"[^}]*"state":"ASSIGNED"' | head -1 | grep -o '"code":"[^"]*' | sed 's/"code":"//')

if [ -z "$ASSIGNED_CODE" ]; then
  echo -e "${YELLOW}⚠️  No ASSIGNED coupons found for alice${NC}"
else
  echo -e "${GREEN}✅ Found ASSIGNED coupon: $ASSIGNED_CODE${NC}"
fi
echo ""

# Test 3: Valid Redemption
if [ ! -z "$ASSIGNED_CODE" ]; then
  echo -e "${BLUE}📝 Test 3: Valid Redemption (ASSIGNED → REDEEMED)${NC}"
  echo "Attempting to redeem coupon $ASSIGNED_CODE..."
  
  REDEEM_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/coupons/redeem/$ASSIGNED_CODE" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json")
  
  HTTP_CODE=$(echo "$REDEEM_RESPONSE" | tail -1)
  
  if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Test 3 PASSED: Coupon redeemed successfully${NC}"
  else
    echo -e "${RED}❌ Test 3 FAILED: Expected 200, got $HTTP_CODE${NC}"
  fi
  echo ""
fi

# Get another ASSIGNED coupon for lock tests
echo -e "${BLUE}📝 Test 4: Lock Coupon (ASSIGNED → LOCKED)${NC}"
COUPONS_RESPONSE=$(curl -s -X GET "$BASE_URL/users/me/coupons" \
  -H "Authorization: Bearer $TOKEN")

ASSIGNED_CODE=$(echo $COUPONS_RESPONSE | grep -o '"code":"[^"]*","book_id"[^}]*"state":"ASSIGNED"' | head -1 | grep -o '"code":"[^"]*' | sed 's/"code":"//')

if [ -z "$ASSIGNED_CODE" ]; then
  echo -e "${YELLOW}⚠️  No more ASSIGNED coupons for lock test${NC}"
else
  echo "Locking coupon $ASSIGNED_CODE..."
  
  LOCK_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/coupons/lock/$ASSIGNED_CODE" \
    -H "Authorization: Bearer $TOKEN")
  
  HTTP_CODE=$(echo "$LOCK_RESPONSE" | tail -1)
  
  if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Test 4 PASSED: Coupon locked${NC}"
    
    # Test 5: Try to redeem locked coupon (SHOULD FAIL)
    echo ""
    echo -e "${BLUE}📝 Test 5: Try Redeem LOCKED Coupon (Should FAIL)${NC}"
    echo "Attempting to redeem locked coupon (expecting 400 error)..."
    
    REDEEM_LOCKED_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/coupons/redeem/$ASSIGNED_CODE" \
      -H "Authorization: Bearer $TOKEN")
    
    HTTP_CODE=$(echo "$REDEEM_LOCKED_RESPONSE" | tail -1)
    RESPONSE_BODY=$(echo "$REDEEM_LOCKED_RESPONSE" | head -n -1)
    
    if [ "$HTTP_CODE" = "400" ] || [ "$HTTP_CODE" = "409" ]; then
      echo -e "${GREEN}✅ Test 5 PASSED: API correctly rejected redemption of LOCKED coupon${NC}"
      echo -e "${YELLOW}   Error message: $(echo $RESPONSE_BODY | grep -o '"detail":"[^"]*' | sed 's/"detail":"//')${NC}"
    else
      echo -e "${RED}❌ Test 5 FAILED: Expected 400/409, got $HTTP_CODE${NC}"
    fi
    
    # Test 6: Unlock coupon
    echo ""
    echo -e "${BLUE}📝 Test 6: Unlock Coupon (LOCKED → ASSIGNED)${NC}"
    echo "Unlocking coupon $ASSIGNED_CODE..."
    
    UNLOCK_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/coupons/unlock/$ASSIGNED_CODE" \
      -H "Authorization: Bearer $TOKEN")
    
    HTTP_CODE=$(echo "$UNLOCK_RESPONSE" | tail -1)
    
    if [ "$HTTP_CODE" = "200" ]; then
      echo -e "${GREEN}✅ Test 6 PASSED: Coupon unlocked${NC}"
      
      # Test 7: Now redeem the unlocked coupon
      echo ""
      echo -e "${BLUE}📝 Test 7: Redeem After Unlock (ASSIGNED → REDEEMED)${NC}"
      echo "Redeeming unlocked coupon..."
      
      REDEEM_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/coupons/redeem/$ASSIGNED_CODE" \
        -H "Authorization: Bearer $TOKEN")
      
      HTTP_CODE=$(echo "$REDEEM_RESPONSE" | tail -1)
      
      if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ Test 7 PASSED: Unlocked coupon redeemed successfully${NC}"
      else
        echo -e "${RED}❌ Test 7 FAILED: Expected 200, got $HTTP_CODE${NC}"
      fi
    else
      echo -e "${RED}❌ Test 6 FAILED: Expected 200, got $HTTP_CODE${NC}"
    fi
  else
    echo -e "${RED}❌ Test 4 FAILED: Expected 200, got $HTTP_CODE${NC}"
  fi
fi
echo ""

# Test 8: Try to redeem already redeemed coupon
echo -e "${BLUE}📝 Test 8: Try Redeem REDEEMED Coupon (Should FAIL)${NC}"
COUPONS_RESPONSE=$(curl -s -X GET "$BASE_URL/users/me/coupons" \
  -H "Authorization: Bearer $TOKEN")

REDEEMED_CODE=$(echo $COUPONS_RESPONSE | grep -o '"code":"[^"]*","book_id"[^}]*"state":"REDEEMED"' | head -1 | grep -o '"code":"[^"]*' | sed 's/"code":"//')

if [ -z "$REDEEMED_CODE" ]; then
  echo -e "${YELLOW}⚠️  No REDEEMED coupons found for test${NC}"
else
  echo "Attempting to redeem already redeemed coupon (expecting error)..."
  
  REDEEM_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/coupons/redeem/$REDEEMED_CODE" \
    -H "Authorization: Bearer $TOKEN")
  
  HTTP_CODE=$(echo "$REDEEM_RESPONSE" | tail -1)
  RESPONSE_BODY=$(echo "$REDEEM_RESPONSE" | head -n -1)
  
  if [ "$HTTP_CODE" = "400" ] || [ "$HTTP_CODE" = "409" ]; then
    echo -e "${GREEN}✅ Test 8 PASSED: API correctly rejected re-redemption${NC}"
    echo -e "${YELLOW}   Error message: $(echo $RESPONSE_BODY | grep -o '"detail":"[^"]*' | sed 's/"detail":"//')${NC}"
  else
    echo -e "${RED}❌ Test 8 FAILED: Expected 400/409, got $HTTP_CODE${NC}"
  fi
fi
echo ""

# Test 9: Email lookup
echo -e "${BLUE}📝 Test 9: User Search by Email${NC}"
echo "Searching for bob@example.com..."

SEARCH_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/users/search/by-email?email=bob@example.com" \
  -H "Authorization: Bearer $TOKEN")

HTTP_CODE=$(echo "$SEARCH_RESPONSE" | tail -1)

if [ "$HTTP_CODE" = "200" ]; then
  echo -e "${GREEN}✅ Test 9 PASSED: User found by email${NC}"
  RESPONSE_BODY=$(echo "$SEARCH_RESPONSE" | head -n -1)
  USER_ID=$(echo $RESPONSE_BODY | grep -o '"user_id":"[^"]*' | sed 's/"user_id":"//')
  echo -e "${YELLOW}   Found user_id: $USER_ID${NC}"
else
  echo -e "${RED}❌ Test 9 FAILED: Expected 200, got $HTTP_CODE${NC}"
fi
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "🎉 SHOWCASE TEST SUITE COMPLETED"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Summary of Features Demonstrated:"
echo "  ✅ Authentication (JWT tokens)"
echo "  ✅ State machine validation (ASSIGNED→LOCKED→REDEEMED)"
echo "  ✅ Lock/Unlock operations"
echo "  ✅ Error handling with clear messages"
echo "  ✅ User search by email"
echo "  ✅ Invalid operation rejection"
echo ""
echo "🌐 Visit http://localhost:5173 for the full UI showcase"
echo "📚 Visit http://localhost:8000/docs for API documentation"
echo ""
