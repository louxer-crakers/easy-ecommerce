# System Architecture Documentation

## Overview

Cloud Store is implemented as a modern three-tier web application with serverless cloud integration. This document describes the system architecture, component interactions, data flows, and design decisions.

## Architectural Pattern

The application follows a **Three-Tier Architecture** pattern:

### 1. Presentation Tier (Frontend)
- **Technology**: HTML5, CSS3, JavaScript (ES6+)
- **Responsibilities**:
  - User interface rendering
  - Client-side state management
  - Input validation
  - API communication
  - Session management (JWT tokens in localStorage)

### 2. Application Tier (Backend)
- **Technology**: Python Flask
- **Responsibilities**:
  - RESTful API endpoints
  - Business logic processing
  - Authentication and authorization
  - Request validation
  - Data transformation
  - AWS service integration

### 3. Data Tier (Persistence)
- **Technology**: AWS DynamoDB
- **Responsibilities**:
  - Data persistence
  - Query execution
  - Data consistency
  - Scalability management

## Component Architecture

### Frontend Components

```
┌─────────────────────────────────────────┐
│         Browser Application             │
├─────────────────────────────────────────┤
│  - Product Catalog (index.html)         │
│  - Authentication (auth.html)           │
│  - Shopping Cart (cart.html)            │
│  - Checkout (checkout.html)             │
│  - Order History (orders.html)          │
├─────────────────────────────────────────┤
│  Shared Components:                     │
│  - Navigation Bar                       │
│  - Toast Notifications                  │
│  - Loading States                       │
└─────────────────────────────────────────┘
```

### Backend Components

```
┌─────────────────────────────────────────┐
│         Flask Application               │
├─────────────────────────────────────────┤
│  app.py (Main Application)              │
│  ├── Route Handlers                     │
│  ├── Request Processing                 │
│  └── Response Formatting                │
├─────────────────────────────────────────┤
│  auth.py (Authentication Module)        │
│  ├── JWT Token Management               │
│  ├── Password Hashing                   │
│  └── Authorization Decorators           │
├─────────────────────────────────────────┤
│  aws_dynamodb.py (Data Access Layer)    │
│  ├── Table Management                   │
│  ├── CRUD Operations                    │
│  └── Query Optimization                 │
├─────────────────────────────────────────┤
│  config.py (Configuration Management)   │
│  └── Environment Variables              │
└─────────────────────────────────────────┘
```

### AWS Integration

```
┌─────────────────────────────────────────┐
│         AWS DynamoDB                    │
├─────────────────────────────────────────┤
│  Products Table                         │
│  ├── Primary Key: product_id            │
│  └── GSI: category-index                │
├─────────────────────────────────────────┤
│  Users Table                            │
│  ├── Primary Key: user_id               │
│  └── GSI: email-index                   │
├─────────────────────────────────────────┤
│  Orders Table                           │
│  ├── Composite Key: order_id + created  │
│  └── GSI: user_id-index                 │
├─────────────────────────────────────────┤
│  Cart Table                             │
│  └── Primary Key: user_id               │
└─────────────────────────────────────────┘
```

## Data Flow Diagrams

### User Authentication Flow

```
1. User Submits Credentials
   ↓
2. POST /api/auth/login
   ↓
3. Query Users Table (email-index)
   ↓
4. Verify Password (bcrypt)
   ↓
5. Generate JWT Token
   ↓
6. Return Token + User Data
   ↓
7. Store Token in localStorage
   ↓
8. Include Token in Subsequent Requests
```

### Product Browsing Flow (Public)

```
1. User Visits Homepage
   ↓
2. GET /api/products
   ↓
3. Scan/Query Products Table
   ↓
4. Return Product List
   ↓
5. Frontend Renders Product Grid
   ↓
6. User Filters/Searches (Client-Side)
   ↓
7. User Adds to Cart (localStorage)
```

### Checkout Flow (Authenticated)

```
1. User Clicks Checkout
   ↓
2. Verify JWT Token
   ↓
3. Navigate to /checkout
   ↓
4. User Fills Shipping Info
   ↓
5. POST /api/orders
   ├── Verify JWT Token
   ├── Validate Order Data
   ├── Create Order in Orders Table
   └── Clear Cart in Cart Table
   ↓
6. Return Order Confirmation
   ↓
7. Redirect to Order History
```

## Security Architecture

### Authentication Layer

```
┌─────────────────────────────────────────┐
│         Client Request                  │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│    Authorization Header Check           │
│    (Bearer Token)                       │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│    JWT Token Validation                 │
│    ├── Signature Verification           │
│    ├── Expiry Check                     │
│    └── Payload Extraction               │
└──────────────┬──────────────────────────┘
               ↓
         ┌─────┴─────┐
    Valid?           Invalid
         │               │
         ↓               ↓
   Allow Request   Return 401
```

### Password Security

1. **Registration**:
   - User provides password
   - bcrypt generates salt
   - Password hashed with salt
   - Only hash stored in database

2. **Login**:
   - User provides password
   - Retrieve hash from database
   - bcrypt compares password with hash
   - Grant access if match

### AWS Credential Management

```
Environment Variables (.env)
  ↓
config.py Loads Variables
  ↓
boto3 Session Creation
  ↓
  ├── Access Key ID
  ├── Secret Access Key
  └── Session Token (if temporary)
  ↓
DynamoDB Client/Resource
```

## Scalability Considerations

### Database Scalability (DynamoDB)

- **Pay-per-Request Billing**: Automatically scales with load
- **Global Secondary Indexes**: Optimized query patterns
- **Partition Key Design**: Distributed data access
- **No Schema Migrations**: Schema-less design allows flexibility

### Application Scal ability

- **Stateless Design**: JWT tokens eliminate server session storage
- **Horizontal Scaling**: Multiple Flask instances can run concurrently
- **Load Balancing**: Can be deployed behind AWS ALB
- **Caching**: Client-side caching reduces API calls

### Frontend Scalability

- **Static Assets**: Can be served from CDN
- **Client-Side Rendering**: Reduces server load
- **LocalStorage**: Reduces server round-trips for cart

## Deployment Architecture

### Recommended AWS Deployment

```
┌──────────────────────────────────────────────┐
│            Internet Gateway                  │
└────────────────┬─────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────┐
│        Application Load Balancer             │
│        (HTTPS Termination)                   │
└────────────────┬─────────────────────────────┘
                 ↓
       ┌─────────┴─────────┐
       ↓                   ↓
┌─────────────┐    ┌─────────────┐
│  EC2/ECS    │    │  EC2/ECS    │
│  Instance 1 │    │  Instance 2 │
│  (Flask App)│    │  (Flask App)│
└──────┬──────┘    └──────┬──────┘
       │                  │
       └─────────┬────────┘
                 ↓
       ┌─────────────────┐
       │  AWS DynamoDB   │
       │  (All Tables)   │
       └─────────────────┘
```

### Alternative Deployment (Serverless)

- **AWS Lambda**: Serverless compute for Flask app
- **API Gateway**: RESTful API management
- **S3 + CloudFront**: Static frontend hosting
- **DynamoDB**: Database (same)

## Design Decisions

### Why DynamoDB Over RDS

1. **Scalability**: Auto-scaling without manual intervention
2. **Performance**: Consistent single-digit millisecond latency
3. **Cost**: Pay-per-request pricing for variable workloads
4. **Maintenance**: Fully managed, no server patching
5. **Flexibility**: Schema-less design for rapid development

### Why JWT Over Sessions

1. **Stateless**: No server-side session storage required
2. **Scalable**: Works across multiple server instances
3. **Mobile-Friendly**: Easy integration with mobile apps
4. **Decoupled**: Frontend and backend can be deployed separately

### Why Flask Over Django

1. **Lightweight**: Minimal overhead for API-only application
2. **Flexibility**: Easy to customize and extend
3. **RESTful**: Natural fit for REST API design
4. **Learning Curve**: Simpler for focused e-commerce API

## Performance Optimization

### Database Optimization

- **Global Secondary Indexes**: Fast lookups for common queries
- **Efficient Key Design**: Optimized partition distribution
- **Projection**: Only fetch required attributes
- **Batch Operations**: Reduce API calls when possible

### API Optimization

- **Response Caching**: Cache frequently accessed data
- **Pagination**: Limit result set sizes
- **Compression**: Enable gzip for responses
- **Connection Pooling**: Reuse DynamoDB connections

### Frontend Optimization

- **Lazy Loading**: Load images on demand
- **Debouncing**: Reduce search API calls
- **Minification**: Compress CSS/JS files
- **CDN**: Serve static assets from edge locations

## Monitoring and Logging

### Application Logging

- **Python logging**: Structured log output
- **Log Levels**: INFO for operations, ERROR for failures
- **CloudWatch Integration**: Send logs to AWS CloudWatch

### Metrics to Monitor

- **API Latency**: Response time per endpoint
- **DynamoDB Metrics**: Read/write capacity, throttling
- **Authentication**: Login success/failure rates
- **Orders**: Checkout conversion rate
- **Errors**: Application error rates

## Disaster Recovery

### Backup Strategy

- **DynamoDB Point-in-Time Recovery**: Enable on all tables
- **On-Demand Backups**: Scheduled daily backups
- **Cross-Region Replication**: For critical data

### Recovery Procedures

1. **Data Loss**: Restore from point-in-time recovery
2. **Table Corruption**: Restore from latest backup
3. **Regional Outage**: Failover to replica region

## Future Enhancements

### Potential Improvements

1. **Payment Integration**: Stripe, PayPal, etc.
2. **Image Upload**: S3 integration for product images
3. **Email Notifications**: SES for order confirmations
4. **Advanced Search**: ElasticSearch integration
5. **Analytics**: CloudWatch dashboards and metrics
6. **Admin Panel**: Dedicated UI for product management
7. **Inventory Management**: Real-time stock tracking
8. **Reviews and Ratings**: Customer feedback system

## Conclusion

This architecture provides a solid foundation for a scalable, secure, and maintainable e-commerce platform. The use of AWS DynamoDB ensures excellent performance and scalability, while the JWT-based authentication system allows for flexible deployment options.

The modular design allows for easy extension and modification as business requirements evolve.
