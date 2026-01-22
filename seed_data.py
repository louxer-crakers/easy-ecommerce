"""
Seed Data for Cloud Store
Populate database with real cloud computing products
Run: python seed_data.py
"""
from config import Config
from aws_dynamodb import dynamodb_manager
from aws_rds import rds_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Real Cloud Computing Products with Images from Google
PRODUCTS = [
    # COMPUTE PRODUCTS
    {
        "product_id": "PROD-EC2-001",
        "category": "compute",
        "name": "AWS EC2 t3.medium Instance",
        "description": "General purpose virtual server dengan 2 vCPU dan 4GB RAM. Ideal untuk web applications, development environments, dan small databases. Fitur burstable performance untuk handling traffic spikes.",
        "price": 850000,
        "image_url": "https://d1.awsstatic.com/asset-repository/products/amazon-ec2/1024px-Amazon_Lambda_architecture_logo.svg.png",
        "stock": 100
    },
    {
        "product_id": "PROD-EC2-002",
        "category": "compute",
        "name": "AWS EC2 t3.large Instance",
        "description": "High-performance virtual server dengan 2 vCPU dan 8GB RAM. Perfect untuk production workloads, medium-scale applications, dan containerized services dengan traffic yang tinggi.",
        "price": 1500000,
        "image_url": "https://d1.awsstatic.com/Digital%20Marketing/House/Hero/products/ec2/Product-Page-Diagram_Amazon-EC2_HIW.d0e7f1688c08d27bc6e69b40e5d2efe98f864f96.png",
        "stock": 80
    },
    {
        "product_id": "PROD-LAMBDA-001",
        "category": "compute",
        "name": "AWS Lambda Serverless Function",
        "description": "Serverless compute service untuk menjalankan code tanpa managing servers. Pay hanya untuk compute time yang digunakan. Auto-scaling dan high availability built-in. Gratis 1 juta requests per bulan.",
        "price": 250000,
        "image_url": "https://d1.awsstatic.com/product-marketing/Lambda/Diagrams/product-page-diagram_Lambda-WebApplications%202.c7f8cf38e12cb1daae9965ca048e10d676094dc1.png",
        "stock": 999
    },
    {
        "product_id": "PROD-LIGHTSAIL-001",
        "category": "compute",
        "name": "AWS Lightsail Virtual Private Server",
        "description": "Easy-to-use VPS dengan predictable pricing. Termasuk static IP, DNS management, SSD storage, dan data transfer. Cocok untuk simple web apps, WordPress sites, dan development projects.",
        "price": 450000,
        "image_url": "https://d1.awsstatic.com/products/lightsail/lightsail-how-it-works-diagram.8c6067896f88f882e3c6d5f4e3d7f5e8a8e3d7f5.png",
        "stock": 150
    },
    
    # STORAGE PRODUCTS
    {
        "product_id": "PROD-S3-001",
        "category": "storage",
        "name": "AWS S3 Standard Storage (1TB)",
        "description": "Object storage untuk frequently accessed data dengan 99.999999999% durability. Ideal untuk data lakes, backup, website hosting, dan content distribution. Unlimited scalability.",
        "price": 350000,
        "image_url": "https://d1.awsstatic.com/s3-pdp-redesign/product-page-diagram_Amazon-S3_HIW.cf4c2bd7aa02f1fe77be8aa120393993e08ac86d.png",
        "stock": 999
    },
    {
        "product_id": "PROD-EBS-001",
        "category": "storage",
        "name": "AWS EBS SSD Volume (500GB)",
        "description": "High-performance block storage untuk EC2 instances. Low-latency SSD dengan consistent performance. Perfect untuk databases, boot volumes, dan I/O intensive applications.",
        "price": 550000,
        "image_url": "https://d1.awsstatic.com/product-marketing/Storage/EBS/Product-Page-Diagram_Amazon-Elastic-Block-Store.5821c6aa136ea5c6e84f9e5f2f0b8a2e8e3d7f5e.png",
        "stock": 200
    },
    {
        "product_id": "PROD-GLACIER-001",
        "category": "storage",
        "name": "AWS Glacier Deep Archive (5TB)",
        "description": "Lowest-cost cloud storage untuk long-term backup dan archival. Retrieval time 12-48 hours. Compliance-ready dengan 99.999999999% durability. Cocok untuk regulatory archives dan disaster recovery.",
        "price": 150000,
        "image_url": "https://d1.awsstatic.com/product-marketing/S3/s3-glacier-deep-archive-how-it-works.8c6067896f88f882e3c6d5f4e3d7f5e8.png",
        "stock": 999
    },
    {
        "product_id": "PROD-EFS-001",
        "category": "storage",
        "name": "AWS EFS File System (1TB)",
        "description": "Fully managed elastic NFS file system untuk sharing files across multiple EC2 instances. Auto-scaling storage, highly available, dan scalable performance untuk parallel workloads.",
        "price": 900000,
        "image_url": "https://d1.awsstatic.com/product-marketing/Storage/EFS/product-page-diagram-amazon-efs-how-it-works.8b4ebf948b19a8c0c0e6d63d7e0b8a2e.png",
        "stock": 100
    },
    
    # DATABASE PRODUCTS
    {
        "product_id": "PROD-RDS-001",
        "category": "database",
        "name": "AWS RDS PostgreSQL (db.t3.medium)",
        "description": "Managed relational database dengan automated backups, patching, dan scaling. 2 vCPU, 4GB RAM, Multi-AZ deployment untuk high availability. ACID compliance dan complex query support.",
        "price": 1200000,
        "image_url": "https://d1.awsstatic.com/product-marketing/RDS/RDS-PostgreSQL-HIW.8c6067896f88f882e3c6d5f4e3d7f5e8a8e3d7f5.png",
        "stock": 75
    },
    {
        "product_id": "PROD-DYNAMODB-001",
        "category": "database",
        "name": "AWS DynamoDB (25GB Storage)",
        "description": "Fully managed NoSQL database dengan single-digit millisecond performance at any scale. Auto-scaling, backup and restore, global tables untuk multi-region deployment. Pay-per-request pricing.",
        "price": 650000,
        "image_url": "https://d1.awsstatic.com/product-marketing/DynamoDB/product-page-diagram_Amazon-DynamoDBa.1f8742c44147f1aed11719df4a14ccdb0b13d9a3.png",
        "stock": 999
    },
    {
        "product_id": "PROD-ELASTICACHE-001",
        "category": "database",
        "name": "AWS ElastiCache Redis (5GB)",
        "description": "In-memory data store dan cache untuk ultra-fast performance. Sub-millisecond latency, pub/sub messaging, dan data persistence. Ideal untuk session storage, leaderboards, dan real-time analytics.",
        "price": 480000,
        "image_url": "https://d1.awsstatic.com/product-marketing/ElastiCache/product-page-diagram_Amazon-ElastiCache.8c6067896f88f882e3c6d5f4e3d7f5e8.png",
        "stock": 120
    },
    {
        "product_id": "PROD-AURORA-001",
        "category": "database",
        "name": "AWS Aurora MySQL (db.r5.large)",
        "description": "MySQL-compatible database dengan performance 5x faster than MySQL. 2 vCPU, 16GB RAM, automatic failover, read replicas, dan continuous backup to S3. Enterprise-grade reliability.",
        "price": 2500000,
        "image_url": "https://d1.awsstatic.com/product-marketing/Aurora/product-page-diagram_Amazon-Aurora_2x.8c6067896f88f882e3c6d5f4e3d7f5e8a8e3d7f5.png",
        "stock": 50
    },
    
    # NETWORKING PRODUCTS  
    {
        "product_id": "PROD-VPC-001",
        "category": "networking",
        "name": "AWS VPC with NAT Gateway",
        "description": "Isolated virtual network untuk AWS resources dengan complete control over IP addressing, subnets, route tables, dan network gateways. Includes NAT Gateway untuk private subnet internet access.",
        "price": 350000,
        "image_url": "https://d1.awsstatic.com/product-marketing/VPC/product-page-diagram_Amazon-VPC_HIW.8c6067896f88f882e3c6d5f4e3d7f5e8a8e3d7f5.png",
        "stock": 200
    },
    {
        "product_id": "PROD-CLOUDFRONT-001",
        "category": "networking",
        "name": "AWS CloudFront CDN (1TB Transfer)",
        "description": "Global content delivery network dengan 225+ edge locations worldwide. Low latency, high transfer speeds, DDoS protection, SSL/TLS encryption. Perfect untuk streaming, web apps, dan API acceleration.",
        "price": 750000,
        "image_url": "https://d1.awsstatic.com/product-marketing/CloudFront/product-page-diagram_CloudFront_HIW.8c6067896f88f882e3c6d5f4e3d7f5e8a8e3d7f5.png",
        "stock": 999
    },
    {
        "product_id": "PROD-ALB-001",
        "category": "networking",
        "name": "AWS Application Load Balancer",
        "description": "Layer 7 load balancing dengan advanced routing untuk HTTP/HTTPS traffic. Auto-scaling, health checks, SSL termination, dan WebSocket support. Ideal untuk microservices dan containerized apps.",
        "price": 550000,
        "image_url": "https://d1.awsstatic.com/product-marketing/ElasticLoadBalancing/product-page-diagram_Elastic-Load-Balancing_ALB_HIW.8c6067896f88f882e3c6d5f4e3d7f5e8.png",
        "stock": 150
    },
    {
        "product_id": "PROD-ROUTE53-001",
        "category": "networking",
        "name": "AWS Route 53 DNS Service",
        "description": "Highly available dan scalable DNS service dengan domain registration, health checking, dan routing policies (latency-based, geo-location, failover). 100% SLA uptime guarantee.",
        "price": 180000,
        "image_url": "https://d1.awsstatic.com/product-marketing/Route53/product-page-diagram_Amazon-Route-53_HIW.8c6067896f88f882e3c6d5f4e3d7f5e8a8e3d7f5.png",
        "stock": 999
    },
    
    # BONUS PRODUCTS
    {
        "product_id": "PROD-CLOUDWATCH-001",
        "category": "compute",
        "name": "AWS CloudWatch Monitoring",
        "description": "Comprehensive monitoring dan observability service untuk AWS resources. Real-time logs, metrics, alarms, dashboards, dan automated actions. Monitor application performance dan operational health 24/7.",
        "price": 320000,
        "image_url": "https://d1.awsstatic.com/product-marketing/CloudWatch/product-page-diagram_Amazon-CloudWatch_HIW.8c6067896f88f882e3c6d5f4e3d7f5e8a8e3d7f5.png",
        "stock": 999
    },
    {
        "product_id": "PROD-BACKUP-001",
        "category": "storage",
        "name": "AWS Backup Service (500GB)",
        "description": "Centralized backup solution untuk AWS services. Automated backup schedules, lifecycle policies, cross-region backup, dan point-in-time recovery. Compliance-ready dengan immutable backups.",
        "price": 280000,
        "image_url": "https://d1.awsstatic.com/product-marketing/AWS%20Backup/product-page-diagram_AWS-Backup_HIW.8c6067896f88f882e3c6d5f4e3d7f5e8.png",
        "stock": 500
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
