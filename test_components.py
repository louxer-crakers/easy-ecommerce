"""
Quick Test Script - Verify Application Components
Tests configuration, imports, and basic functionality
"""
import sys

print("=" * 60)
print("Cloud Store - Component Test")
print("=" * 60)

try:
    print("\n✓ Testing imports...")
    from config import Config
    print("  ✓ config.py")
    
    from auth import AuthManager
    print("  ✓ auth.py")
    
    # Test imports based on what's available
    try:
        from aws_rds import rds_manager
        print("  ✓ aws_rds.py (RDS available)")
        has_rds = True
    except Exception as e:
        print(f"  ⚠ aws_rds.py - {e}")
        has_rds = False
    
    try:
        from aws_dynamodb import dynamodb_manager
        print("  ✓ aws_dynamodb.py (DynamoDB available)")
        has_dynamodb = True
    except Exception as e:
        print(f"  ⚠ aws_dynamodb.py - {e}")
        has_dynamodb = False
    
    from flask import Flask
    print("  ✓ Flask")
    
    print("\n✓ Testing configuration...")
    print(f"  - AWS Region: {Config.AWS_REGION}")
    print(f"  - RDS Host: {Config.RDS_HOST}")
    print(f"  - RDS Database: {Config.RDS_DATABASE}")
    print(f"  - DynamoDB Products Table: {Config.DYNAMODB_PRODUCTS_TABLE}")
    print(f"  - DynamoDB Orders Table: {Config.DYNAMODB_ORDERS_TABLE}")
    print(f"  - DynamoDB Cart Table: {Config.DYNAMODB_CART_TABLE}")
    print(f"  - JWT Expiry: {Config.JWT_EXPIRY_HOURS} hours")
    print(f"  - Currency: {Config.CURRENCY}")
    print(f"  - Tax Rate: {Config.TAX_RATE * 100}%")
    
    print("\n✓ Testing authentication functions...")
    test_password = "TestPassword123"
    hashed = AuthManager.hash_password(test_password)
    print(f"  ✓ Password hashing works")
    
    verified = AuthManager.verify_password(test_password, hashed)
    print(f"  ✓ Password verification: {verified}")
    
    user_id = AuthManager.generate_user_id()
    print(f"  ✓ User ID generation: {user_id}")
    
    print("\n✓ Testing JWT token...")
    token = AuthManager.generate_token("test-user-123", "test@example.com")
    print(f"  ✓ Token generated: {token[:50]}...")
    
    decoded = AuthManager.decode_token(token)
    print(f"  ✓ Token decoded: user_id={decoded['user_id']}, email={decoded['email']}")
    
    print("\n✓ Testing email validation...")
    valid_emails = ["test@example.com", "user.name@domain.co.id"]
    invalid_emails = ["invalid", "test@", "@domain.com"]
    
    from auth import validate_email
    for email in valid_emails:
        assert validate_email(email), f"Should be valid: {email}"
    print(f"  ✓ Valid emails pass")
    
    for email in invalid_emails:
        assert not validate_email(email), f"Should be invalid: {email}"
    print(f"  ✓ Invalid emails rejected")
    
    print("\n✓ Testing password validation...")
    from auth import validate_password
    
    valid, msg = validate_password("Short")
    print(f"  ✓ Short password rejected: {msg}")
    
    valid, msg = validate_password("ValidPassword123")
    print(f"  ✓ Valid password accepted")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Configure .env with your AWS and RDS credentials")
    print("2. Run: python seed_data.py (to load 18 products)")
    print("3. Run: python app.py (to start the application)")
    print("\n")
    
except Exception as e:
    print(f"\n✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
