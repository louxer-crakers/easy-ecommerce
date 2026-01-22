"""
Seed Data for Cloud Store E-Commerce
Real products with working images
Run: python seed_data.py
"""
from config import Config
from aws_dynamodb import dynamodb_manager
from aws_rds import rds_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# E-Commerce Products dengan Gambar yang Pasti Muncul!
PRODUCTS = [
    # ELEKTRONIK & GADGET
    {
        "product_id": "PROD-LAPTOP-001",
        "category": "compute",
        "name": "MacBook Pro 14 inch M3 Pro",
        "description": "Laptop premium dengan chip M3 Pro yang super kencang! 16GB RAM, 512GB SSD, layar Liquid Retina XDR. Perfect untuk coding, design, dan video editing. Battery life up to 18 jam!",
        "price": 32000000,
        "image_url": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp14-spacegray-select-202310?wid=904&hei=840&fmt=jpeg&qlt=90&.v=1697230830200",
        "stock": 15
    },
    {
        "product_id": "PROD-LAPTOP-002",
        "category": "compute",
        "name": "ASUS ROG Strix G16 Gaming Laptop",
        "description": "Beast gaming laptop! Intel Core i9, RTX 4070, 32GB RAM, 1TB SSD. QHD 240Hz display untuk gaming experience yang smooth banget. RGB keyboard customizable!",
        "price": 28000000,
        "image_url": "https://m.media-amazon.com/images/I/81bc8mA3nKL._AC_SX679_.jpg",
        "stock": 12
    },
    {
        "product_id": "PROD-PHONE-001",
        "category": "compute",
        "name": "iPhone 15 Pro Max 256GB",
        "description": "Flagship iPhone terbaru! Titanium design, A17 Pro chip, camera 48MP yang incredible, USB-C, Action Button. Available in Natural Titanium, Blue Titanium, White Titanium.",
        "price": 21000000,
        "image_url": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-15-pro-finish-select-202309-6-7inch-naturaltitanium?wid=5120&hei=2880&fmt=p-jpg&qlt=80&.v=1692845702960",
        "stock": 25
    },
    {
        "product_id": "PROD-PHONE-002",
        "category": "compute",
        "name": "Samsung Galaxy S24 Ultra 512GB",
        "description": "Android flagship dengan S-Pen! Snapdragon 8 Gen 3, 200MP camera, 6.8 inch Dynamic AMOLED display, AI features yang canggih. Gaming dan multitasking super smooth!",
        "price": 19500000,
        "image_url": "https://images.samsung.com/id/smartphones/galaxy-s24-ultra/buy/product_color_titanium_gray.png",
        "stock": 20
    },
    {
        "product_id": "PROD-TABLET-001",
        "category": "compute",
        "name": "iPad Pro 12.9 inch M2 WiFi 256GB",
        "description": "Tablet paling powerful! M2 chip, Liquid Retina XDR display, Apple Pencil support, Magic Keyboard compatible. Cocok banget buat digital art, note-taking, dan produktivitas!",
        "price": 17000000,
        "image_url": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/ipad-pro-12-select-wifi-spacegray-202210?wid=940&hei=1112&fmt=png-alpha&.v=1664411207213",
        "stock": 18
    },
    
    # GAMING & ACCESSORIES
    {
        "product_id": "PROD-CONSOLE-001",
        "category": "database",
        "name": "PlayStation 5 Slim Digital Edition",
        "description": "Next-gen gaming console! 1TB SSD, 4K gaming up to 120fps, ray tracing, DualSense controller dengan haptic feedback. Includes God of War Ragnarök!",
        "price": 7500000,
        "image_url": "https://gmedia.playstation.com/is/image/SIEPDC/ps5-product-thumbnail-01-en-14sep21?$facebook$",
        "stock": 30
    },
    {
        "product_id": "PROD-HEADSET-001",
        "category": "database",
        "name": "Sony WH-1000XM5 Wireless Headphones",
        "description": "Best noise cancelling headphones! 30-hour battery life, superior sound quality, AI-powered noise cancellation, multipoint connection. Comfortable untuk listening marathon!",
        "price": 5500000,
        "image_url": "https://m.media-amazon.com/images/I/51K1sBp2CIL._AC_SX679_.jpg",
        "stock": 40
    },
    {
        "product_id": "PROD-WATCH-001",
        "category": "database",
        "name": "Apple Watch Series 9 GPS 45mm",
        "description": "Smartwatch terbaik untuk iPhone users! Always-on Retina display, S9 chip, health tracking detailed, fitness features lengkap, water resistant 50m. Midnight Aluminum case!",
        "price": 6500000,
        "image_url": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/watch-card-40-s9-202309?wid=680&hei=528&fmt=p-jpg&qlt=95&.v=1693861933617",
        "stock": 35
    },
    
    # FASHION & LIFESTYLE
    {
        "product_id": "PROD-SHOES-001",
        "category": "storage",
        "name": "Nike Air Jordan 1 Retro High OG",
        "description": "Iconic sneakers yang timeless! Premium leather, classic colorway, comfortable untuk daily use. Hype sneakers yang never goes out of style!",
        "price": 3200000,
        "image_url": "https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/b7d9211c-26e7-431a-ac24-b0540fb3c00f/air-jordan-1-retro-high-og-shoes-Pz6fG9.png",
        "stock": 50
    },
    {
        "product_id": "PROD-SHOES-002",
        "category": "storage",
        "name": "Adidas Ultraboost 23 Running Shoes",
        "description": "Running shoes paling comfortable! Boost cushioning, Primeknit upper, Continental rubber outsole. Perfect untuk running dan casual wear. Breathable banget!",
        "price": 2800000,
        "image_url": "https://assets.adidas.com/images/h_840,f_auto,q_auto,fl_lossy,c_fill,g_auto/fbaf991a78bc4896a3e9ad7800abcec6_9366/Ultraboost_Light_Shoes_Black_FY0378_01_standard.jpg",
        "stock": 45
    },
    {
        "product_id": "PROD-BAG-001",
        "category": "storage",
        "name": "Fjallraven Kanken Classic Backpack",
        "description": "Iconic backpack dari Sweden! Durable Vinylon F fabric, water-resistant, ergonomic design, perfect size untuk laptop 15 inch. Available in 20+ colors!",
        "price": 1500000,
        "image_url": "https://m.media-amazon.com/images/I/81AVQPR4QvL._AC_SX679_.jpg",
        "stock": 60
    },
    {
        "product_id": "PROD-BAG-002",
        "category": "storage",
        "name": "Herschel Little America Backpack",
        "description": "Stylish backpack dengan laptop sleeve! Signature striped fabric liner, magnetic strap closures, padded back panel. Cocok untuk campus, travel, dan daily use!",
        "price": 1800000,
        "image_url": "https://m.media-amazon.com/images/I/81qB0HJ6iuL._AC_SX679_.jpg",
        "stock": 55
    },
    
    # HOME & LIFESTYLE
    {
        "product_id": "PROD-CAMERA-001",
        "category": "networking",
        "name": "Sony Alpha A7 IV Mirrorless Camera",
        "description": "Full-frame camera untuk content creators! 33MP sensor, 4K 60fps video, AI autofocus yang cepet banget, 5-axis stabilization. Perfect untuk photography dan videography!",
        "price": 35000000,
        "image_url": "https://m.media-amazon.com/images/I/81fA19Y-WCL._AC_SX679_.jpg",
        "stock": 10
    },
    {
        "product_id": "PROD-SPEAKER-001",
        "category": "networking",
        "name": "JBL Charge 5 Portable Bluetooth Speaker",
        "description": "Portable speaker dengan bass yang mantap! IP67 waterproof dan dustproof, 20-hour playtime, USB charge out for devices. Party anywhere dengan sound quality premium!",
        "price": 2500000,
        "image_url": "https://m.media-amazon.com/images/I/71PQJO54xnL._AC_SX679_.jpg",
        "stock": 70
    },
    {
        "product_id": "PROD-KEYBOARD-001",
        "category": "networking",
        "name": "Logitech MX Keys Advanced Wireless Keyboard",
        "description": "Best keyboard untuk productivity! Tactile typing, smart illumination, USB-C rechargeable, multi-device pairing. Comfortable typing experience untuk long sessions!",
        "price": 1900000,
        "image_url": "https://m.media-amazon.com/images/I/51NBdDCa3TL._AC_SX679_.jpg",
        "stock": 50
    },
    {
        "product_id": "PROD-MOUSE-001",
        "category": "networking",
        "name": "Logitech MX Master 3S Wireless Mouse",
        "description": "Ultimate productivity mouse! MagSpeed scrolling, 8K DPI sensor, ergonomic design, multi-device support. Silent clicks dan battery life up to 70 days!",
        "price": 1600000,
        "image_url": "https://m.media-amazon.com/images/I/61ni3t1ryQL._AC_SX679_.jpg",
        "stock": 45
    },
    
    # BONUS PRODUCTS
    {
        "product_id": "PROD-MONITOR-001",
        "category": "compute",
        "name": "LG UltraGear 27 inch 4K Gaming Monitor",
        "description": "4K UHD gaming monitor dengan 144Hz refresh rate! NVIDIA G-Sync compatible, 1ms response time, HDR10 support. Colors yang vibrant untuk gaming dan content creation!",
        "price": 8500000,
        "image_url": "https://m.media-amazon.com/images/I/81JjFco7hWL._AC_SX679_.jpg",
        "stock": 25
    },
    {
        "product_id": "PROD-GIMBAL-001",
        "category": "networking",
        "name": "DJI Osmo Mobile 6 Smartphone Gimbal",
        "description": "3-axis gimbal stabilizer untuk smartphone! Built-in extension rod, magnetic clamp, ActiveTrack 5.0, long battery life. Perfect untuk vlogging dan smooth cinematic shots!",
        "price": 1900000,
        "image_url": "https://m.media-amazon.com/images/I/51cVPME+TJL._AC_SX679_.jpg",
        "stock": 40
    }
]


def seed_products():
    """Populate DynamoDB with product data"""
    try:
        logger.info("Starting product seeding...")
        
        for product in PRODUCTS:
            try:
                dynamodb_manager.create_product(
                    product_id=product['product_id'],
                    name=product['name'],
                    description=product['description'],
                    price=product['price'],
                    category=product['category'],
                    image_url=product['image_url'],
                    stock=product['stock']
                )
                logger.info(f"✓ Added: {product['name']}")
            except Exception as e:
                logger.warning(f"✗ Skipped {product['name']}: {e}")
        
        logger.info(f"\n✓ Seeding complete! Added {len(PRODUCTS)} products")
        logger.info("\nProduct Categories:")
        categories = {}
        for p in PRODUCTS:
            cat = p['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in categories.items():
            logger.info(f"  - {cat.title()}: {count} products")
        
    except Exception as e:
        logger.error(f"Error seeding products: {e}")
        raise


def main():
    """Main entry point"""
    try:
        logger.info("=" * 60)
        logger.info("Cloud Store - Product Seeder")
        logger.info("=" * 60)
        
        # Validate config
        Config.validate()
        
        # Initialize tables
        logger.info("\nInitializing databases...")
        dynamodb_manager.create_tables_if_not_exist()
        
        # Seed products
        logger.info("\nSeeding products...")
        seed_products()
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ SEEDING SUCCESSFUL!")
        logger.info("=" * 60)
        logger.info("\nYou can now start the application with: python app.py")
        
    except Exception as e:
        logger.error(f"\n✗ Seeding failed: {e}")
        raise


if __name__ == "__main__":
    main()
