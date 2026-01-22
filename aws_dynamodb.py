"""
AWS DynamoDB utilities for E-Commerce Application
Handles Products, Orders, and Cart (NO GSI - using sort keys)
Users are stored in RDS PostgreSQL
"""
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from config import Config
import logging
from decimal import Decimal
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert DynamoDB Decimal to JSON"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


class DynamoDBManager:
    """Manages DynamoDB for Products, Orders, and Cart"""
    
    def __init__(self):
        """Initialize DynamoDB client and resource"""
        self.dynamodb_client = None
        self.dynamodb_resource = None
        self._initialize_dynamodb()
    
    def _initialize_dynamodb(self):
        """Initialize DynamoDB with session token support"""
        try:
            session_params = {
                'aws_access_key_id': Config.AWS_ACCESS_KEY_ID,
                'aws_secret_access_key': Config.AWS_SECRET_ACCESS_KEY,
                'region_name': Config.AWS_REGION
            }
            
            if Config.AWS_SESSION_TOKEN:
                session_params['aws_session_token'] = Config.AWS_SESSION_TOKEN
            
            session = boto3.Session(**session_params)
            
            if Config.DYNAMODB_ENDPOINT:
                self.dynamodb_client = session.client('dynamodb', endpoint_url=Config.DYNAMODB_ENDPOINT)
                self.dynamodb_resource = session.resource('dynamodb', endpoint_url=Config.DYNAMODB_ENDPOINT)
            else:
                self.dynamodb_client = session.client('dynamodb')
                self.dynamodb_resource = session.resource('dynamodb')
            
            logger.info("DynamoDB client initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing DynamoDB: {e}")
            raise
    
    def create_tables_if_not_exist(self):
        """Create DynamoDB tables for Products, Orders, and Cart"""
        try:
            self._create_products_table()
            self._create_orders_table()
            self._create_cart_table()
            logger.info("All DynamoDB tables created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating DynamoDB tables: {e}")
            raise
    
    def _create_products_table(self):
        """Create Products table with sort key (NO GSI)"""
        table_name = Config.DYNAMODB_PRODUCTS_TABLE
        
        try:
            existing_tables = self.dynamodb_client.list_tables()['TableNames']
            if table_name in existing_tables:
                logger.info(f"Table '{table_name}' already exists")
                return
            
            table = self.dynamodb_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'product_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'category', 'KeyType': 'RANGE'}  # Sort key instead of GSI
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'product_id', 'AttributeType': 'S'},
                    {'AttributeName': 'category', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            logger.info(f"Table '{table_name}' created successfully")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                logger.info(f"Table '{table_name}' already exists")
            else:
                raise
    
    def _create_orders_table(self):
        """Create Orders table with composite key (NO GSI)"""
        table_name = Config.DYNAMODB_ORDERS_TABLE
        
        try:
            existing_tables = self.dynamodb_client.list_tables()['TableNames']
            if table_name in existing_tables:
                logger.info(f"Table '{table_name}' already exists")
                return
            
            table = self.dynamodb_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'},  # Partition key
                    {'AttributeName': 'order_id', 'KeyType': 'RANGE'}  # Sort key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    {'AttributeName': 'order_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            logger.info(f"Table '{table_name}' created successfully")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                logger.info(f"Table '{table_name}' already exists")
            else:
                raise
    
    def _create_cart_table(self):
        """Create Cart table (simple key)"""
        table_name = Config.DYNAMODB_CART_TABLE
        
        try:
            existing_tables = self.dynamodb_client.list_tables()['TableNames']
            if table_name in existing_tables:
                logger.info(f"Table '{table_name}' already exists")
                return
            
            table = self.dynamodb_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'user_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            logger.info(f"Table '{table_name}' created successfully")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                logger.info(f"Table '{table_name}' already exists")
            else:
                raise
    
    # PRODUCTS CRUD Operations
    
    def create_product(self, product_id, name, description, price, category, image_url='', stock=0):
        """Create a new product"""
        try:
            table = self.dynamodb_resource.Table(Config.DYNAMODB_PRODUCTS_TABLE)
            
            item = {
                'product_id': product_id,
                'category': category,  # Sort key
                'name': name,
                'description': description,
                'price': Decimal(str(price)),
                'image_url': image_url,
                'stock': stock,
                'created_at': datetime.now().isoformat()
            }
            
            table.put_item(Item=item)
            logger.info(f"Product created: {product_id}")
            
            item['price'] = float(item['price'])
            return item
            
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            raise
    
    def get_all_products(self, category=None):
        """Get all products, optionally filtered by category"""
        try:
            table = self.dynamodb_resource.Table(Config.DYNAMODB_PRODUCTS_TABLE)
            
            if category:
                # Scan with filter (since we don't have GSI)
                response = table.scan(
                    FilterExpression=Attr('category').eq(category)
                )
            else:
                response = table.scan()
            
            items = response.get('Items', [])
            
            for item in items:
                if 'price' in item:
                    item['price'] = float(item['price'])
            
            return items
            
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            raise
    
    def get_product(self, product_id, category):
        """Get a single product"""
        try:
            table = self.dynamodb_resource.Table(Config.DYNAMODB_PRODUCTS_TABLE)
            response = table.get_item(Key={
                'product_id': product_id,
                'category': category
            })
            
            item = response.get('Item')
            if item and 'price' in item:
                item['price'] = float(item['price'])
            
            return item
            
        except Exception as e:
            logger.error(f"Error getting product: {e}")
            raise
    
    def update_product(self, product_id, category, **kwargs):
        """Update a product"""
        try:
            table = self.dynamodb_resource.Table(Config.DYNAMODB_PRODUCTS_TABLE)
            
            update_expr = []
            expr_attr_values = {}
            expr_attr_names = {}
            
            for key, value in kwargs.items():
                if value is not None and key not in ['product_id', 'category']:
                    if key == 'name':
                        update_expr.append("#n = :name")
                        expr_attr_values[':name'] = value
                        expr_attr_names['#n'] = 'name'
                    elif key == 'price':
                        update_expr.append("price = :price")
                        expr_attr_values[':price'] = Decimal(str(value))
                    else:
                        update_expr.append(f"{key} = :{key}")
                        expr_attr_values[f':{key}'] = value
            
            if not update_expr:
                raise ValueError("No fields to update")
            
            response = table.update_item(
                Key={'product_id': product_id, 'category': category},
                UpdateExpression="SET " + ", ".join(update_expr),
                ExpressionAttributeValues=expr_attr_values,
                ExpressionAttributeNames=expr_attr_names if expr_attr_names else None,
                ReturnValues="ALL_NEW"
            )
            
            item = response.get('Attributes')
            if item and 'price' in item:
                item['price'] = float(item['price'])
            
            logger.info(f"Product updated: {product_id}")
            return item
            
        except Exception as e:
            logger.error(f"Error updating product: {e}")
            raise
    
    def delete_product(self, product_id, category):
        """Delete a product"""
        try:
            table = self.dynamodb_resource.Table(Config.DYNAMODB_PRODUCTS_TABLE)
            response = table.delete_item(
                Key={'product_id': product_id, 'category': category},
                ReturnValues='ALL_OLD'
            )
            
            deleted = 'Attributes' in response
            if deleted:
                logger.info(f"Product deleted: {product_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            raise
    
    # ORDERS CRUD Operations
    
    def create_order(self, order_id, user_id, items, total_amount, shipping_address, status='pending'):
        """Create a new order"""
        try:
            table = self.dynamodb_resource.Table(Config.DYNAMODB_ORDERS_TABLE)
            
            item = {
                'user_id': user_id,  # Partition key
                'order_id': order_id,  # Sort key
                'items': items,
                'total_amount': Decimal(str(total_amount)),
                'shipping_address': shipping_address,
                'status': status,
                'created_at': datetime.now().isoformat()
            }
            
            table.put_item(Item=item)
            logger.info(f"Order created: {order_id}")
            
            item['total_amount'] = float(item['total_amount'])
            return item
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise
    
    def get_user_orders(self, user_id):
        """Get all orders for a user using partition key"""
        try:
            table = self.dynamodb_resource.Table(Config.DYNAMODB_ORDERS_TABLE)
            response = table.query(
                KeyConditionExpression=Key('user_id').eq(user_id),
                ScanIndexForward=False  # Most recent first
            )
            
            items = response.get('Items', [])
            
            for item in items:
                if 'total_amount' in item:
                    item['total_amount'] = float(item['total_amount'])
            
            return items
            
        except Exception as e:
            logger.error(f"Error getting user orders: {e}")
            raise
    
    def get_order(self, user_id, order_id):
        """Get a specific order"""
        try:
            table = self.dynamodb_resource.Table(Config.DYNAMODB_ORDERS_TABLE)
            response = table.get_item(Key={
                'user_id': user_id,
                'order_id': order_id
            })
            
            item = response.get('Item')
            if item and 'total_amount' in item:
                item['total_amount'] = float(item['total_amount'])
            
            return item
            
        except Exception as e:
            logger.error(f"Error getting order: {e}")
            raise
    
    # CART Operations
    
    def save_cart(self, user_id, items):
        """Save or update cart"""
        try:
            table = self.dynamodb_resource.Table(Config.DYNAMODB_CART_TABLE)
            
            item = {
                'user_id': user_id,
                'items': items,
                'updated_at': datetime.now().isoformat()
            }
            
            table.put_item(Item=item)
            logger.info(f"Cart saved for user: {user_id}")
            return item
            
        except Exception as e:
            logger.error(f"Error saving cart: {e}")
            raise
    
    def get_cart(self, user_id):
        """Get user's cart"""
        try:
            table = self.dynamodb_resource.Table(Config.DYNAMODB_CART_TABLE)
            response = table.get_item(Key={'user_id': user_id})
            return response.get('Item')
            
        except Exception as e:
            logger.error(f"Error getting cart: {e}")
            raise
    
    def clear_cart(self, user_id):
        """Clear user's cart"""
        try:
            table = self.dynamodb_resource.Table(Config.DYNAMODB_CART_TABLE)
            table.delete_item(Key={'user_id': user_id})
            logger.info(f"Cart cleared for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cart: {e}")
            raise


# Singleton instance
dynamodb_manager = DynamoDBManager()
