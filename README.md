# Cloud Store - E-Commerce Web Application

## Project Overview

Cloud Store is a full-stack e-commerce web application built with Flask, AWS RDS PostgreSQL, and AWS DynamoDB. The application allows users to browse products publicly, add items to cart without authentication, and complete purchases after logging in or registering. 

**Database Architecture:**
- **RDS PostgreSQL**: User accounts and authentication
- **DynamoDB**: Products catalog, orders, and shopping cart

## Architecture

![System Architecture](architecture/architecture.png)

### System Components

The application follows a three-tier architecture with hybrid database storage:

1. **Presentation Layer**: HTML/CSS/JavaScript frontend with responsive design
2. **Application Layer**: Python Flask REST API with JWT authentication
3. **Data Layer**: 
   - AWS RDS PostgreSQL for user management
   - AWS DynamoDB for e-commerce data (products, orders, cart)

### Database Distribution

#### RDS PostgreSQL (Relational Data)
Stores user accounts and authentication:
- **Users Table**: user_id, email, password_hash, name, timestamps
- Why RDS: Strong consistency for authentication, ACID compliance, complex queries

#### DynamoDB (E-Commerce Data)
Stores products and transactional data:
- **Products Table**: product_id (PK), category (SK), name, price, stock
- **Orders Table**: user_id (PK), order_id (SK), items, total, shipping
- **Cart Table**: user_id (PK), items, updated_at
- Why DynamoDB: High scalability, fast reads/writes, no GSI needed with sort keys

## Technology Stack

### Backend
- **Python 3.12+**: Primary programming language
- **Flask 3.0**: Web framework for RESTful API
- **boto3**: AWS SDK for DynamoDB integration
- **psycopg2**: PostgreSQL adapter for RDS
- **PyJWT**: JSON Web Token implementation
- **bcrypt**: Password hashing and verification
- **Flask-CORS**: Cross-Origin Resource Sharing support

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with glassmorphism effects
- **JavaScript ES6+**: Interactive functionality
- **Font Awesome**: Icon library
- **Google Fonts (Inter)**: Typography

### Cloud Services
- **AWS RDS PostgreSQL**: User management database
- **AWS DynamoDB**: Products, orders, and cart storage
- **AWS IAM**: Identity and access management

## Features

### Public Features (No Authentication Required)
- Browse complete product catalog
- View product details
- Search products by name or description
- Filter products by category
- Add products to shopping cart
- View and modify shopping cart

### Authenticated Features (Login Required)
- User registration and login
- Complete checkout process
- View order history
- Secure session management

### Administrative Features
- Create new products
- Update product information
- Delete products
- Manage inventory

## Database Schema

### RDS PostgreSQL Schema

#### Users Table

**Structure:**
- `user_id` (VARCHAR 50, Primary Key)
- `email` (VARCHAR 255, Unique, Indexed)
- `password_hash` (VARCHAR 255)
- `name` (VARCHAR 255)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Note:** Table is automatically created on first run by `aws_rds.py`

### DynamoDB Schema

#### Products Table
```
Partition Key: product_id (String)
Sort Key: category (String)

Attributes:
- product_id: Unique product identifier
- category: Product category (also sort key)
- name: Product name
- description: Product description
- price: Product price (Decimal)
- image_url: Product image URL
- stock: Available quantity
- created_at: Creation timestamp
```

#### Orders Table
```
Partition Key: user_id (String)
Sort Key: order_id (String)

Attributes:
- user_id: Reference to user (partition key)
- order_id: Unique order identifier (sort key)
- items: List of order items
- total_amount: Order total (Decimal)
- shipping_address: Delivery address (Map)
- status: Order status
- created_at: Order timestamp
```

#### Cart Table
```
Partition Key: user_id (String)

Attributes:
- user_id: Reference to user
- items: List of cart items
- updated_at: Last update timestamp
```

## API Endpoints

### Authentication Endpoints
```
POST /api/auth/register
- Register new user
- Request Body: {name, email, password}
- Response: {success, token, user}

POST /api/auth/login
- User login
- Request Body: {email, password}
- Response: {success, token, user}

GET /api/auth/verify
- Verify JWT token
- Headers: Authorization: Bearer {token}
- Response: {success, user}
```

### Product Endpoints (Public)
```
GET /api/products
- Get all products
- Query Parameters: category (optional)
- Response: {success, data, count}

GET /api/products/{product_id}
- Get single product
- Response: {success, data}
```

### Product Management (Admin, Authenticated)
```
POST /api/admin/products
- Create new product
- Headers: Authorization: Bearer {token}
- Request Body: {name, description, price, category, image_url, stock}
- Response: {success, data}

PUT /api/admin/products/{product_id}
- Update product
- Headers: Authorization: Bearer {token}
- Request Body: {fields to update}
- Response: {success, data}

DELETE /api/admin/products/{product_id}
- Delete product
- Headers: Authorization: Bearer {token}
- Response: {success, message}
```

### Cart Endpoints (Authenticated)
```
GET /api/cart
- Get user cart
- Headers: Authorization: Bearer {token}
- Response: {success, data}

POST /api/cart
- Save cart items
- Headers: Authorization: Bearer {token}
- Request Body: {items}
- Response: {success, data}

DELETE /api/cart
- Clear cart
- Headers: Authorization: Bearer {token}
- Response: {success, message}
```

### Order Endpoints (Authenticated)
```
POST /api/orders
- Create new order (checkout)
- Headers: Authorization: Bearer {token}
- Request Body: {items, total_amount, shipping_address}
- Response: {success, data}

GET /api/orders
- Get user order history
- Headers: Authorization: Bearer {token}
- Response: {success, data, count}
```

## Installation and Setup

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- AWS Account with RDS and DynamoDB access
- AWS IAM credentials with appropriate permissions

### Step 1: Clone and Setup Environment

```bash
cd /path/to/project
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and configure the following:

#### AWS Credentials
```
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_SESSION_TOKEN=your-session-token  # Optional, for temporary credentials
AWS_REGION=ap-southeast-1
```

#### RDS Configuration
```
RDS_HOST=your-rds-endpoint.ap-southeast-1.rds.amazonaws.com
RDS_PORT=5432
RDS_DATABASE=ecommerce
RDS_USERNAME=postgres
RDS_PASSWORD=your-secure-password
```

#### JWT Secret Key
Generate a secure JWT secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and set it in `.env`:
```
JWT_SECRET_KEY=your-generated-secret-key-here
```

### Step 3: Initialize Database Tables

The application automatically creates tables on first run:
- **RDS**: Creates `users` table with index
- **DynamoDB**: Creates `Products`, `Orders`, and `Cart` tables

No manual table creation is required.

### Step 4: Seed Database with Products (Optional but Recommended)

Populate the database with 18 real AWS cloud computing products:

```bash
python seed_data.py
```

This will create:
- **4 Compute products**: EC2 instances, Lambda, Lightsail, CloudWatch
- **4 Storage products**: S3, EBS, Glacier, EFS, Backup
- **4 Database products**: RDS PostgreSQL, DynamoDB, ElastiCache, Aurora
- **4 Networking products**: VPC, CloudFront, Load Balancer, Route 53

All products include:
- Real product images from AWS
- Detailed descriptions in Indonesian
- Realistic pricing in IDR
- Stock availability

### Step 5: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

Access the application in your web browser at the above URL.

## AWS Configuration

### RDS PostgreSQL Setup

1. Create RDS PostgreSQL instance (t3.micro or higher)
2. Configure security group to allow connections from EC2 (port 5432)
3. Create database named `ecommerce`
4. Note the endpoint URL, username, and password

### DynamoDB Setup

DynamoDB tables are created automatically with Pay-Per-Request billing mode. No manual configuration needed.

### AWS Session Token Support

For temporary credentials (AWS STS, EC2 instance roles, etc.), set the `AWS_SESSION_TOKEN` environment variable. The application automatically includes this token in AWS API requests.

## Application Workflow

### Customer Journey

1. **Browse Products**
   - User visits homepage
   - Views product grid with filters
   - Can search by keyword

2. **Add to Cart**
   - Click "Add to Cart" on products
   - Cart stored in browser localStorage
   - Cart count updated in navigation

3. **View Cart**
   - Navigate to cart page
   - Modify quantities or remove items
   - View order summary with tax

4. **Checkout**
   - Click "Proceed to Checkout"
   - Redirected to login if not authenticated
   - Fill shipping information
   - Place order

5. **Order Confirmation**
   - Order saved to DynamoDB
   - Cart cleared
   - Order appears in order history

## Security Features

### Password Security
- Passwords hashed using bcrypt with salt
- Passwords never stored in plain text
- Minimum 6-character requirement

### Authentication
- JWT tokens for session management
- 24-hour token expiry (configurable)
- Tokens stored in browser localStorage
- Protected routes require valid JWT

### AWS Security
- Credentials stored in environment variables
- Session token support for temporary credentials
- No hardcoded credentials in code

## EC2 Deployment Guide

### Recommended Instance Type: t3.medium

**Specifications:**
- **vCPUs**: 2
- **Memory**: 4 GB
- **Network Performance**: Up to 5 Gbps
- **EBS-Optimized**: Yes

**Why t3.medium:**
- Sufficient memory for Flask application and database connections
- Burstable CPU credits for handling traffic spikes
- Cost-effective for small to medium e-commerce sites
- Good balance between performance and cost

### Deployment Steps

1. **Launch EC2 Instance**
```bash
# Instance Type: t3.medium
# AMI: Ubuntu Server 22.04 LTS
# Storage: 20 GB GP3
# Security Group: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)
```

2. **Connect and Setup**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv nginx -y

# Clone your repository
git clone your-repo-url
cd your-project

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
# Copy and edit .env
cp .env.example .env
nano .env

# Set all credentials and configuration
```

4. **Setup Systemd Service**
```bash
sudo nano /etc/systemd/system/cloudstore.service
```

Add:
```ini
[Unit]
Description=Cloud Store E-Commerce Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/your-project
Environment="PATH=/home/ubuntu/your-project/venv/bin"
ExecStart=/home/ubuntu/your-project/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Start Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable cloudstore
sudo systemctl start cloudstore
sudo systemctl status cloudstore
```

6. **Configure Nginx (Optional)**
```bash
sudo nano /etc/nginx/sites-available/cloudstore
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/cloudstore /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Development

### Adding Products

Products can be added via API endpoint or directly in DynamoDB console. Example product:

```json
{
  "product_id": "PROD-ABC123",
  "category": "compute",
  "name": "AWS EC2 Instance",
  "description": "Virtual server in the cloud",
  "price": 500000,
  "image_url": "https://example.com/ec2.png",
  "stock": 10
}
```

### Categories

Standard categories:
- compute
- storage
- database
- networking

## Troubleshooting

### RDS Connection Issues

**Problem**: Cannot connect to RDS
**Solution**: 
- Verify RDS security group allows connections from EC2
- Check RDS endpoint and credentials
- Ensure database exists
- Test connection: `psql -h RDS_HOST -U postgres -d ecommerce`

### DynamoDB Connection Issues

**Problem**: Cannot connect to DynamoDB
**Solution**: 
- Verify AWS credentials are correct
- Check IAM permissions
- Ensure correct AWS region is set

### Authentication Errors

**Problem**: Token expired or invalid
**Solution**:
- Clear browser localStorage
- Login again
- Check JWT_SECRET_KEY is consistent
- Verify token expiry settings


## License

This project is created for educational and portfolio purposes.

## Contact

For questions or support, please refer to project documentation or contact the development team.
