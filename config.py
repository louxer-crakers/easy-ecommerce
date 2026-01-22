"""
Configuration management for E-Commerce application
Reads settings from environment variables for security
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # AWS General Settings
    AWS_REGION = os.getenv('AWS_REGION', 'ap-southeast-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN', None)  # For temporary credentials
    
    # RDS PostgreSQL Settings (for Users)
    RDS_HOST = os.getenv('RDS_HOST', 'your-rds-endpoint.region.rds.amazonaws.com')
    RDS_PORT = int(os.getenv('RDS_PORT', 5432))
    RDS_DATABASE = os.getenv('RDS_DATABASE', 'ecommerce')
    RDS_USERNAME = os.getenv('RDS_USERNAME', 'postgres')
    RDS_PASSWORD = os.getenv('RDS_PASSWORD', '')
    
    # DynamoDB Settings (for Products, Orders, Cart)
    DYNAMODB_ENDPOINT = os.getenv('DYNAMODB_ENDPOINT', None)  # None for AWS, set URL for local
    
    # Table Names
    DYNAMODB_PRODUCTS_TABLE = os.getenv('DYNAMODB_PRODUCTS_TABLE', 'Products')
    DYNAMODB_ORDERS_TABLE = os.getenv('DYNAMODB_ORDERS_TABLE', 'Orders')
    DYNAMODB_CART_TABLE = os.getenv('DYNAMODB_CART_TABLE', 'Cart')
    
    # JWT Settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_EXPIRY_HOURS = int(os.getenv('JWT_EXPIRY_HOURS', 24))
    
    # E-Commerce Settings
    ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 12))
    CURRENCY = os.getenv('CURRENCY', 'IDR')
    TAX_RATE = float(os.getenv('TAX_RATE', 0.11))  # 11% PPN
    
    @staticmethod
    def validate():
        """Validate that required configuration is present"""
        required_vars = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'RDS_HOST',
            'RDS_PASSWORD'
        ]
        
        missing = []
        for var in required_vars:
            value = getattr(Config, var)
            if not value or value == '':
                missing.append(var)
        
        if missing:
            print(f"Warning: Missing configuration: {', '.join(missing)}")
            print("Application may not function properly without proper credentials.")
            return False
        return True
