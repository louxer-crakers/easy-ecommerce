"""
AWS RDS PostgreSQL utilities for User Management
Handles user authentication and profile data
"""
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RDSManager:
    """Manages RDS PostgreSQL connections for Users"""
    
    def __init__(self):
        """Initialize connection pool"""
        self.connection_pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Create connection pool"""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1,  # minconn
                20,  # maxconn
                host=Config.RDS_HOST,
                port=Config.RDS_PORT,
                database=Config.RDS_DATABASE,
                user=Config.RDS_USERNAME,
                password=Config.RDS_PASSWORD
            )
            logger.info("RDS connection pool created successfully")
        except Exception as e:
            logger.error(f"Error creating RDS connection pool: {e}")
            raise
    
    def get_connection(self):
        """Get a connection from the pool"""
        try:
            return self.connection_pool.getconn()
        except Exception as e:
            logger.error(f"Error getting connection: {e}")
            raise
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        try:
            self.connection_pool.putconn(conn)
        except Exception as e:
            logger.error(f"Error returning connection: {e}")
    
    def create_tables_if_not_exist(self):
        """Create users table in RDS if it doesn't exist"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create users table with shipping address fields
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(50) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    phone VARCHAR(50),
                    address_street VARCHAR(500),
                    address_city VARCHAR(100),
                    address_state VARCHAR(100),
                    address_postal_code VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for email lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
            """)
            
            conn.commit()
            logger.info("RDS users table created/verified successfully")
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error creating tables: {e}")
            raise
        finally:
            if conn:
                cursor.close()
                self.return_connection(conn)
    
    # USER CRUD Operations
    
    def create_user(self, user_id, email, password_hash, name):
        """Create a new user"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                INSERT INTO users (user_id, email, password_hash, name)
                VALUES (%s, %s, %s, %s)
                RETURNING user_id, email, name, created_at, updated_at
            """, (user_id, email, password_hash, name))
            
            result = cursor.fetchone()
            conn.commit()
            logger.info(f"User created: {email}")
            return dict(result)
            
        except psycopg2.IntegrityError:
            if conn:
                conn.rollback()
            raise ValueError(f"User with email {email} already exists")
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error creating user: {e}")
            raise
        finally:
            if conn:
                cursor.close()
                self.return_connection(conn)
    
    def get_user_by_email(self, email):
        """Get user by email"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT user_id, email, password_hash, name, created_at, updated_at
                FROM users
                WHERE email = %s
            """, (email,))
            
            result = cursor.fetchone()
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            raise
        finally:
            if conn:
                cursor.close()
                self.return_connection(conn)
    
    def get_user(self, user_id):
        """Get user by ID"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT user_id, email, name, created_at, updated_at
                FROM users
                WHERE user_id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            raise
        finally:
            if conn:
                cursor.close()
                self.return_connection(conn)
    
    def close_all_connections(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("All RDS connections closed")


# Singleton instance
rds_manager = RDSManager()
    def update_user_address(self, user_id, phone, address_street, address_city, address_state, address_postal_code):
        """Update user shipping address"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                UPDATE users
                SET phone = %s,
                    address_street = %s,
                    address_city = %s,
                    address_state = %s,
                    address_postal_code = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                RETURNING user_id, email, name, phone, address_street, address_city, address_state, address_postal_code, created_at, updated_at
            """, (phone, address_street, address_city, address_state, address_postal_code, user_id))
            
            result = cursor.fetchone()
            conn.commit()
            logger.info(f"User address updated: {user_id}")
            return dict(result) if result else None
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error updating user address: {e}")
            raise
        finally:
            if conn:
                cursor.close()
                self.return_connection(conn)
