#!/usr/bin/env python3
"""
Example API usage script demonstrating the coupon service flow
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1"


def print_response(title: str, response: requests.Response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    if response.status_code < 400:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")


def main():
    """Demonstrate complete coupon service workflow"""
    
    # 1. Create a coupon book
    print("\n🔹 Step 1: Create a Coupon Book")
    book_data = {
        "name": "Summer 2024 Promotion",
        "description": "10% off summer products",
        "owner_id": "owner-user-123",
        "expiration_date": "2024-12-31T23:59:59Z",
        "allow_multi_redemption": False,
        "max_redemptions_per_user": 1,
        "max_assignments_per_user": 3,
        "code_pattern": "SUMMER2024-{}",
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/books/", json=book_data)
    print_response("Create Book", response)
    
    if response.status_code != 201:
        print("❌ Failed to create book. Exiting.")
        return
    
    book_id = response.json()["book_id"]
    print(f"\n✅ Book created with ID: {book_id}")
    
    # 2. Generate coupon codes
    print("\n🔹 Step 2: Generate Coupon Codes")
    generate_data = {
        "count": 10,
        "length": 8,
        "max_redemptions": 1
    }
    
    response = requests.post(
        f"{BASE_URL}/books/{book_id}/codes/generate",
        json=generate_data,
        params={"include_codes": True}
    )
    print_response("Generate Codes", response)
    
    if response.status_code != 200:
        print("❌ Failed to generate codes. Exiting.")
        return
    
    codes = response.json()["codes"]
    print(f"\n✅ Generated {len(codes)} codes")
    print(f"Sample code: {codes[0]}")
    
    # 3. Assign random coupon to user
    print("\n🔹 Step 3: Assign Random Coupon to User")
    user_id = "customer-user-456"
    assign_data = {
        "book_id": book_id,
        "user_id": user_id,
        "count": 2
    }
    
    response = requests.post(f"{BASE_URL}/coupons/assign", json=assign_data)
    print_response("Assign Random Coupons", response)
    
    if response.status_code != 200:
        print("❌ Failed to assign coupons. Exiting.")
        return
    
    assigned_coupons = response.json()["coupons"]
    assigned_code = assigned_coupons[0]["code"]
    print(f"\n✅ Assigned {len(assigned_coupons)} coupons to user {user_id}")
    print(f"First assigned code: {assigned_code}")
    
    # 4. Get user's coupons
    print("\n🔹 Step 4: Get User's Coupons")
    response = requests.get(f"{BASE_URL}/users/{user_id}/coupons")
    print_response("User's Coupons", response)
    
    # 5. Lock coupon for redemption
    print("\n🔹 Step 5: Lock Coupon for Redemption")
    lock_data = {
        "user_id": user_id,
        "lock_duration_seconds": 300
    }
    
    response = requests.post(
        f"{BASE_URL}/coupons/lock/{assigned_code}",
        json=lock_data
    )
    print_response("Lock Coupon", response)
    
    if response.status_code != 200:
        print("⚠️  Failed to lock coupon. Continuing anyway.")
    else:
        print(f"✅ Coupon {assigned_code} locked for 5 minutes")
    
    # 6. Redeem coupon
    print("\n🔹 Step 6: Redeem Coupon")
    redeem_data = {
        "user_id": user_id,
        "metadata": {
            "order_id": "ORDER-789-XYZ",
            "discount_amount": 10.00,
            "product": "Summer T-Shirt"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/coupons/redeem/{assigned_code}",
        json=redeem_data
    )
    print_response("Redeem Coupon", response)
    
    if response.status_code == 200:
        redemption = response.json()
        print(f"\n✅ Coupon redeemed successfully!")
        print(f"   Redemption count: {redemption['redemption_count']}")
        print(f"   Remaining: {redemption['remaining_redemptions']}")
    else:
        print("❌ Failed to redeem coupon")
    
    # 7. Try to redeem again (should fail for single-use coupon)
    print("\n🔹 Step 7: Try to Redeem Again (Expected to Fail)")
    response = requests.post(
        f"{BASE_URL}/coupons/redeem/{assigned_code}",
        json=redeem_data
    )
    print_response("Redeem Again", response)
    
    if response.status_code == 400:
        print("\n✅ Correctly prevented double redemption")
    
    # 8. Get coupon details
    print("\n🔹 Step 8: Get Coupon Details")
    response = requests.get(f"{BASE_URL}/coupons/{assigned_code}")
    print_response("Coupon Details", response)
    
    # 9. Assign specific coupon
    print("\n🔹 Step 9: Assign Specific Coupon to Another User")
    another_user = "customer-user-789"
    specific_code = codes[5]  # Use one of the generated codes
    assign_specific_data = {
        "user_id": another_user
    }
    
    response = requests.post(
        f"{BASE_URL}/coupons/assign/{specific_code}",
        json=assign_specific_data
    )
    print_response("Assign Specific Coupon", response)
    
    if response.status_code == 200:
        print(f"\n✅ Assigned code {specific_code} to user {another_user}")
    
    # 10. Upload custom codes
    print("\n🔹 Step 10: Upload Custom Codes to Another Book")
    custom_book_data = {
        "name": "VIP Codes",
        "owner_id": "owner-user-123",
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/books/", json=custom_book_data)
    if response.status_code == 201:
        vip_book_id = response.json()["book_id"]
        
        upload_data = {
            "codes": [
                "VIP-GOLD-2024",
                "VIP-PLATINUM-2024",
                "VIP-DIAMOND-2024"
            ],
            "max_redemptions": 1
        }
        
        response = requests.post(
            f"{BASE_URL}/books/{vip_book_id}/codes/upload",
            json=upload_data
        )
        print_response("Upload Custom Codes", response)
        
        if response.status_code == 200:
            print("\n✅ Successfully uploaded custom VIP codes")
    
    print("\n" + "="*60)
    print("✅ Demo Complete!")
    print("="*60)
    print("\nCheck the API documentation at: http://localhost:8000/docs")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the service is running: docker-compose up -d")
        print("Or: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")
