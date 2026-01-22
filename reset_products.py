"""
Clear all products from DynamoDB and reseed with new data
"""
from aws_dynamodb import dynamodb_manager
from seed_data import seed_products, PRODUCTS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clear_all_products():
    """Delete all existing products"""
    try:
        logger.info("Fetching all existing products...")
        products = dynamodb_manager.get_all_products()
        
        if not products:
            logger.info("No products to delete")
            return
        
        logger.info(f"Found {len(products)} products to delete")
        
        for product in products:
            try:
                dynamodb_manager.delete_product(
                    product['product_id'],
                    product['category']
                )
                logger.info(f"✓ Deleted: {product['name']}")
            except Exception as e:
                logger.warning(f"✗ Failed to delete {product['name']}: {e}")
        
        logger.info(f"\n✓ Cleared {len(products)} old products!")
        
    except Exception as e:
        logger.error(f"Error clearing products: {e}")
        raise


def main():
    try:
        logger.info("=" * 60)
        logger.info("Product Reset & Reseed")
        logger.info("=" * 60)
        
        # Clear old products
        logger.info("\n[1/2] Clearing old products...")
        clear_all_products()
        
        # Seed new products
        logger.info("\n[2/2] Loading new products...")
        seed_products()
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ RESET COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"\nTotal products now: {len(PRODUCTS)}")
        logger.info("Refresh your browser to see the new products!")
        
    except Exception as e:
        logger.error(f"\n✗ Reset failed: {e}")
        raise


if __name__ == "__main__":
    main()
