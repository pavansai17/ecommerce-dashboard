## Overview

An interactive cloud-based data visualization dashboard built for
e-commerce analytics. Users can upload any e-commerce dataset in
CSV or Excel format and instantly get meaningful visual insights
including sales trends, product performance, category breakdowns
and inventory tracking — all powered by AWS cloud infrastructure.
## Features

- Upload any e-commerce CSV or Excel file
- Auto-detects columns (sales, date, category, region, product)
- 5 analysis tabs:
  - Overview — data preview and column mapping
  - Sales Analysis — revenue trends and category breakdown
  - Product Analysis — top products and price distribution
  - AI Summary — auto-generated insights and data quality report
  - Download Report — export CSV and TXT reports
- Every uploaded file automatically backed up to AWS S3
- Sidebar filters for category, region, date range and price
- Interactive charts with zoom, filter and export (Plotly)
- Works with Amazon, Flipkart, Shopify, WooCommerce exports

---

## Tech Stack

| Technology | Usage |
|------------|-------|
| Python 3.11 | Core programming language |
| Streamlit | Frontend dashboard framework |
| Plotly Express | Interactive charts and graphs |
| Pandas | Data processing and analysis |
| boto3 | AWS SDK for Python |
| AWS S3 | Cloud storage for datasets |
| AWS EC2 | Cloud server hosting dashboard |
| AWS IAM | Access management and security |
| Docker | Application containerization |
| GitHub Actions | CI/CD pipeline |

---

## AWS Architecture
User (Browser)
↓
AWS EC2 t2.micro (us-east-1)
↓
Docker Container
↓
Streamlit Dashboard (port 8501)
↓
AWS S3 Bucket
(ecommerce-dashboard-pavansai)
↓
Permanent CSV Storage

---

## Project Structure
ECOMMERCE-DASHBOARD/
│
├── app.py                  # Main Streamlit application
├── s3_helper.py            # AWS S3 integration helper
├── Dockerfile              # Docker container configuration
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore rules
├── README.md               # Project documentation
│
├── pages/                  # Streamlit pages (optional)
│   ├── sales.py
│   ├── products.py
│   └── inventory.py
│
└── data/                   # Local dataset (not pushed to GitHub)
├── olist_orders_dataset.csv
├── olist_products_dataset.csv
├── olist_customers_dataset.csv
└── ...

---

## Dataset

This project uses the **Olist Brazilian E-Commerce Dataset** from Kaggle.

- Source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- Size: ~130MB
- Records: 100,000+ orders
- Files: 9 CSV files covering orders, products,
  customers, payments, reviews and sellers

---

## Installation and Setup

### Prerequisites
- Python 3.11+
- Docker Desktop
- AWS Account with IAM access
- Mac/Linux terminal

### Local Setup

```bash
# Clone the repository
git clone https://github.com/pavansaitejaankala/ecommerce-dashboard.git
cd ecommerce-dashboard
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py
```

Open browser at `http://localhost:8501`

---

### Docker Setup

```bash
# Build Docker image
docker build -t ecommerce-dashboard .

# Run container
docker run -p 8501:8501 \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -e S3_BUCKET_NAME=your-bucket-name \
  ecommerce-dashboard
```

---

### AWS Deployment

#### Step 1 — Configure AWS CLI
```bash
aws configure
# Enter Access Key, Secret Key, Region: us-east-1
```

#### Step 2 — Create S3 Bucket
```bash
aws s3 mb s3://your-bucket-name --region us-east-1
aws s3 sync data/ s3://your-bucket-name/uploads/
```

#### Step 3 — Launch EC2 Instance
```bash
# Create key pair
aws ec2 create-key-pair \
  --key-name dashboard-key \
  --query 'KeyMaterial' \
  --output text > ~/Downloads/dashboard-key.pem

chmod 400 ~/Downloads/dashboard-key.pem

# Create security group
aws ec2 create-security-group \
  --group-name dashboard-sg \
  --description "Dashboard Security Group"

aws ec2 authorize-security-group-ingress \
  --group-name dashboard-sg \
  --protocol tcp --port 22 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name dashboard-sg \
  --protocol tcp --port 8501 --cidr 0.0.0.0/0

# Launch instance
aws ec2 run-instances \
  --image-id ami-0c7217cdde317cfec \
  --instance-type t2.micro \
  --key-name dashboard-key \
  --security-groups dashboard-sg \
  --count 1
```

#### Step 4 — Deploy on EC2
```bash
# SSH into EC2
ssh -i ~/Downloads/dashboard-key.pem ubuntu@YOUR_EC2_IP

# Install Docker on EC2
sudo apt update -y
sudo apt install -y docker.io
sudo systemctl start docker
sudo usermod -aG docker ubuntu
newgrp docker

# Pull and run dashboard
docker pull pavansaitejaankala/ecommerce-dashboard:latest

docker run -d \
  --name ecommerce-dashboard \
  --restart always \
  -p 8501:8501 \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -e S3_BUCKET_NAME=your-bucket-name \
  pavansaitejaankala/ecommerce-dashboard:latest
```

#### Step 5 — Access Dashboard
http://YOUR_EC2_IP:8501

---

## Managing EC2 Instance

```bash
# Start instance (before presentation)
aws ec2 start-instances --instance-ids YOUR_INSTANCE_ID

# Get public IP after starting
aws ec2 describe-instances \
  --instance-ids YOUR_INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text

# Stop instance (after presentation - saves costs)
aws ec2 stop-instances --instance-ids YOUR_INSTANCE_ID
```

> Always stop EC2 after use to avoid unnecessary charges

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| AWS_DEFAULT_REGION | AWS region (us-east-1) |
| AWS_ACCESS_KEY_ID | IAM access key |
| AWS_SECRET_ACCESS_KEY | IAM secret key |
| S3_BUCKET_NAME | Your S3 bucket name |

> Never commit .env file to GitHub

---

## Dashboard Screenshots

### Home Screen
Upload any e-commerce CSV or Excel file to get started

### Sales Analysis
- Monthly revenue trend line chart
- Top 10 categories by revenue
- Revenue by region pie chart
- Payment methods breakdown

### Product Analysis
- Top 15 products by revenue
- Category distribution pie chart
- Price distribution box plot

### Download Report
- Text report (.txt)
- Filtered dataset (.csv)
- Full dataset (.csv)

---

## Why AWS Cloud

| Feature | Localhost | AWS Cloud |
|---------|-----------|-----------|
| Accessibility | Only your laptop | Anyone, anywhere |
| Data Storage | Lost on session end | Permanent in S3 |
| Availability | Mac must be on | 24/7 on EC2 |
| Scalability | Single user | Multiple users |
| URL | localhost:8501 | Public IP:8501 |

---

## Future Enhancements

- Lambda function for automatic ETL processing
- CloudWatch monitoring and alerts
- RDS database for structured storage
- Authentication system for multi-user access
- Terraform for infrastructure as code
- Automated CI/CD with GitHub Actions

---

## Author

**Pavan Sai Tejaankala**
- GitHub: [@pavansaitejaankala](https://github.com/pavansai17/ECOMMERCE-DASHBOARD)
- Project: Final Year B.Tech — AWS Cloud Data Visualization

---

## Acknowledgements

- Kaggle — Olist Brazilian E-Commerce Dataset
- AWS Free Tier — EC2, S3, IAM
- Streamlit — Open source dashboard framework
- Plotly — Interactive visualization library
- Docker — Containerization platform

---

## License

This project is licensed under the MIT License.





