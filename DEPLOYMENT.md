# DocIQ Deployment Guide

This guide covers deploying DocIQ to production environments using Docker, cloud platforms, and traditional servers.

## 🚀 Quick Deployment Options

### 1. Docker Compose (Recommended)

The easiest way to deploy DocIQ is using Docker Compose:

```bash
# Clone the repository
git clone <repository-url>
cd assignment

# Set environment variables
export GEMINI_API_KEY="your_api_key_here"
export USE_MOCK_GEMINI="false"

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 2. Manual Deployment

#### Backend Setup

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip tesseract-ocr tesseract-ocr-eng

# Create virtual environment
cd doc_pipeline
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_api_key_here"
export USE_MOCK_GEMINI="false"

# Start backend
python main.py
```

#### Frontend Setup

```bash
# Install Node.js dependencies
cd dociq-ui
npm install

# Build for production
npm run build

# Serve with nginx or any web server
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS ECS

1. **Create ECR repositories:**
```bash
aws ecr create-repository --repository-name dociq-backend
aws ecr create-repository --repository-name dociq-frontend
```

2. **Build and push images:**
```bash
# Backend
docker build -f Dockerfile.backend -t dociq-backend .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag dociq-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/dociq-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/dociq-backend:latest

# Frontend
docker build -f Dockerfile.frontend -t dociq-frontend .
docker tag dociq-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/dociq-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/dociq-frontend:latest
```

3. **Create ECS cluster and services**
4. **Set up Application Load Balancer**
5. **Configure environment variables**

#### Using AWS EC2

```bash
# Launch EC2 instance
# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and deploy
git clone <repository-url>
cd assignment
export GEMINI_API_KEY="your_api_key_here"
docker-compose up -d
```

### Google Cloud Platform

#### Using Google Cloud Run

```bash
# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push images
gcloud builds submit --tag gcr.io/PROJECT_ID/dociq-backend
gcloud builds submit --tag gcr.io/PROJECT_ID/dociq-frontend

# Deploy to Cloud Run
gcloud run deploy dociq-backend \
  --image gcr.io/PROJECT_ID/dociq-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_api_key_here

gcloud run deploy dociq-frontend \
  --image gcr.io/PROJECT_ID/dociq-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Deployment

#### Using Azure Container Instances

```bash
# Build and push to Azure Container Registry
az acr build --registry <registry-name> --image dociq-backend .
az acr build --registry <registry-name> --image dociq-frontend .

# Deploy to Container Instances
az container create \
  --resource-group <resource-group> \
  --name dociq-backend \
  --image <registry-name>.azurecr.io/dociq-backend:latest \
  --dns-name-label dociq-backend \
  --ports 8000 \
  --environment-variables GEMINI_API_KEY=your_api_key_here
```

## 🔧 Production Configuration

### Environment Variables

Create a `.env` file for production:

```bash
# API Configuration
GEMINI_API_KEY=your_production_api_key_here
USE_MOCK_GEMINI=false
LOG_LEVEL=INFO

# Database (if using)
DATABASE_URL=postgresql://user:password@localhost/dociq

# Security
SECRET_KEY=your_secret_key_here
CORS_ORIGINS=https://yourdomain.com

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
```

### SSL/TLS Configuration

#### Using Let's Encrypt with Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Monitoring and Logging

#### Using Prometheus and Grafana

Add monitoring to your `docker-compose.yml`:

```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
```

#### Using ELK Stack

```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:7.17.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:7.17.0
    ports:
      - "5601:5601"
```

## 🔒 Security Best Practices

### 1. API Key Management

- Use environment variables for API keys
- Rotate API keys regularly
- Use different keys for development and production

### 2. Network Security

- Use HTTPS in production
- Configure CORS properly
- Implement rate limiting
- Use firewalls and security groups

### 3. Container Security

- Run containers as non-root users
- Scan images for vulnerabilities
- Keep base images updated
- Use multi-stage builds

### 4. Data Protection

- Encrypt data at rest
- Use secure file upload validation
- Implement proper access controls
- Regular security audits

## 📊 Performance Optimization

### 1. Caching

```python
# Redis caching for API responses
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_response(key, data, expire=3600):
    redis_client.setex(key, expire, json.dumps(data))

def get_cached_response(key):
    data = redis_client.get(key)
    return json.loads(data) if data else None
```

### 2. Load Balancing

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /api/ {
        proxy_pass http://backend;
    }
}
```

### 3. Database Optimization

- Use connection pooling
- Implement proper indexing
- Regular database maintenance
- Monitor query performance

## 🚨 Troubleshooting

### Common Issues

1. **API Quota Exceeded**
   - Switch to mock mode temporarily
   - Upgrade API plan
   - Implement rate limiting

2. **OCR Failures**
   - Check Tesseract installation
   - Verify image quality
   - Review OCR logs

3. **Memory Issues**
   - Monitor container memory usage
   - Implement image preprocessing
   - Use streaming for large files

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend health
curl http://localhost:3000/health

# Check Docker services
docker-compose ps
docker-compose logs backend
docker-compose logs frontend
```

### Log Analysis

```bash
# View real-time logs
docker-compose logs -f

# Search for errors
docker-compose logs | grep ERROR

# Monitor resource usage
docker stats
```

## 📈 Scaling

### Horizontal Scaling

```yaml
services:
  backend:
    deploy:
      replicas: 3
    environment:
      - REDIS_URL=redis://redis:6379

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

### Vertical Scaling

- Monitor resource usage
- Adjust container limits
- Optimize application code
- Use CDN for static assets

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build and push Docker images
        run: |
          docker build -f Dockerfile.backend -t dociq-backend .
          docker build -f Dockerfile.frontend -t dociq-frontend .
          # Push to registry
      
      - name: Deploy to production
        run: |
          # Deploy using your preferred method
```

---

For more detailed information, refer to the main README.md file. 