#!/usr/bin/env python3
"""Test UserUpdate compatibility."""
from cnm_bookhub_be.db.models.users import UserUpdate

# Test creating an instance
u = UserUpdate(full_name='Test User', phone_number='0123456789')
print("UserUpdate instance created:", u)

# Test create_update_dict method
result = u.create_update_dict()
print("create_update_dict() result:", result)
print("✅ Test passed!")
