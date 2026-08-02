# HN Pipeline

> **Serverless Event-Driven Data Engineering Pipeline on AWS**

HN Pipeline is a cloud-native, serverless data engineering project that automatically collects, cleans, processes, and prepares Hacker News data for downstream analytics and visualization.

The project demonstrates modern cloud engineering practices by combining **AWS Lambda**, **Amazon S3**, **CloudWatch**, **Terraform**, **Docker**, and **Natural Language Processing (NLP)** into an automated event-driven ETL pipeline.

Rather than focusing solely on data collection, the project emphasizes production-oriented software engineering concepts including Infrastructure as Code (IaC), modular serverless architecture, reusable Lambda Layers, automated deployment, and scalable pipeline design.

---

## Key Features

- Fully serverless event-driven architecture
- Infrastructure as Code (Terraform)
- Automated Hacker News data ingestion
- Multi-stage ETL pipeline
- Amazon S3 event-driven processing
- CloudWatch scheduled execution
- Modular AWS Lambda functions
- Docker-based Lambda Layer builds
- Shared Lambda dependency management
- NLP preprocessing using SpaCy and NLTK
- Incremental processing with state management
- Dashboard-ready processed datasets

---

# Architecture Overview

The pipeline consists of three independent AWS Lambda functions connected through Amazon S3 events.

```

CloudWatch Scheduler
        │
        ▼
┌──────────────────┐
│ Fetch Lambda     │
└──────────────────┘
        │
        ▼
 Raw Data Bucket
        │
 S3 ObjectCreated
        │
        ▼
┌──────────────────┐
│ Clean Lambda     │
└──────────────────┘
        │
        ▼
 Cleaned Data Bucket
        │
 S3 ObjectCreated
        │
        ▼
┌──────────────────┐
│ Process Lambda   │
└──────────────────┘
        │
        ▼
Processed Data Bucket
        │
        ▼
 Dashboard / Analytics

```

Each stage performs a single responsibility, making the pipeline modular, maintainable, and independently scalable.

---

# Technology Stack

## Cloud Services

- AWS Lambda
- Amazon S3
- Amazon CloudWatch
- AWS IAM

## Infrastructure

- Terraform
- Docker

## Programming

- Python 3.11

## NLP Libraries

- SpaCy
- NLTK
- Requests
- BeautifulSoup
- Pandas

---

# Repository Structure

```

hn-pipeline/

├── infrastructure/
│
├── lambda/
│   ├── terraform/
│   │   ├── fetch_hn_data/
│   │   ├── clean_hn_data/
│   │   ├── process_hn_data/
│   │   ├── shared_layer/
│   │   ├── modules/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   └── scripts/
│       ├── build_lambda.sh
│       ├── build_layers.sh
│       └── Dockerfile
│
├── dashboard/
│
├── tools/
│
├── docs/
│
└── README.md

```

### Directory Overview

| Directory | Description |
|------------|-------------|
| infrastructure | AWS infrastructure resources and configuration |
| lambda | Lambda source code, Terraform configuration, and build scripts |
| dashboard | Dashboard application for visualizing processed Hacker News data |
| tools | Local utilities and supporting scripts |
| docs | Project documentation |

---

# Pipeline Workflow

The pipeline follows an event-driven architecture where each stage is automatically triggered by AWS events.

## 1. Fetch Stage

**Trigger**

- Amazon CloudWatch scheduled event (default: every 15 minutes)

**Responsibilities**

- Retrieve the latest Hacker News stories using the Hacker News API.
- Collect story metadata and content.
- Store the raw JSON dataset in Amazon S3.

**Output**

```
raw/
└── hn_top_raw_<timestamp>.json
```

---

## 2. Clean Stage

**Trigger**

- Amazon S3 ObjectCreated event from the Raw Data bucket.

**Responsibilities**

- Read newly uploaded raw datasets.
- Remove duplicate records.
- Normalize and clean text fields.
- Perform NLP preprocessing.
- Maintain processing state to avoid duplicate work.
- Save cleaned datasets.

**Output**

```
cleaned/
└── hn_top_cleaned_<timestamp>.json
```

---

## 3. Processing Stage

**Trigger**

- Amazon S3 ObjectCreated event from the Cleaned Data bucket.

**Responsibilities**

- Perform additional text processing.
- Extract structured information.
- Generate processed datasets for downstream analytics.
- Record processed file history.

**Output**

```
processed/
└── hn_top_processed_<timestamp>.json
```

---

# Infrastructure Overview

Infrastructure provisioning is fully automated using Terraform.

Major AWS resources include:

- Amazon S3 Buckets
- AWS Lambda Functions
- Lambda Layers
- IAM Roles and Policies
- CloudWatch Event Rules
- CloudWatch Event Targets
- Lambda Permissions
- S3 Bucket Notifications

Infrastructure is organized under

```
lambda/
└── terraform/
```

allowing reproducible deployments and Infrastructure as Code (IaC).

---

# Lambda Functions

The project contains three independent Lambda functions.

| Function | Responsibility |
|----------|----------------|
| fetch_hn_data | Retrieve Hacker News data from the public API |
| clean_hn_data | Clean, normalize, and preprocess raw datasets |
| process_hn_data | Generate processed datasets for analytics and visualization |

Each Lambda performs a single responsibility, making the pipeline easier to maintain and extend.

---

# Lambda Layers

Shared Python dependencies are packaged as Lambda Layers to reduce deployment package sizes and improve maintainability.

The project currently uses shared layers located under

```
lambda/terraform/shared_layer/
```

Layer packages are built using Docker with an Amazon Linux environment compatible with the AWS Lambda Python 3.11 runtime.

Benefits include:

- Smaller Lambda deployment packages
- Shared dependencies across multiple functions
- Faster deployments
- Simplified dependency management

---

# Getting Started

## Prerequisites

Before deploying the project, ensure the following tools are installed:

- Python 3.11
- Docker
- Terraform
- AWS CLI
- Git

An AWS account with appropriate permissions is also required.

---

## Clone Repository

```bash
git clone https://github.com/uscsds/hn-pipeline.git

cd hn-pipeline
```

---

## Build Lambda Packages

Navigate to the build scripts directory.

```bash
cd lambda/scripts
```

Build Lambda deployment packages.

```bash
./build_lambda.sh
```

---

## Build Lambda Layers

```bash
./build_layers.sh
```

---

## Deploy Infrastructure

```bash
cd ../terraform

terraform init

terraform plan

terraform apply
```

For complete deployment instructions, see:

```
docs/DEPLOYMENT.md
```
---

# Engineering Highlights

This project demonstrates practical cloud engineering and modern software development practices, including:

- **Serverless Architecture** using AWS Lambda
- **Event-Driven Processing** with Amazon S3 notifications
- **Infrastructure as Code (IaC)** using Terraform
- **Modular Lambda Design** with reusable Terraform modules
- **Shared Lambda Layers** for dependency management
- **Docker-Based Build Environment** for Lambda compatibility
- **Incremental Processing** using state management
- **Natural Language Processing (NLP)** with SpaCy and NLTK
- **Cloud-Native Deployment** using AWS managed services
- **Scalable Multi-Stage ETL Pipeline**

---

# Current Project Status

Current implementation includes:

- ✅ Automated Hacker News data ingestion
- ✅ Event-driven serverless ETL pipeline
- ✅ Infrastructure deployment using Terraform
- ✅ Modular Lambda functions
- ✅ Shared Lambda Layers
- ✅ NLP preprocessing pipeline
- ✅ Dashboard integration
- ✅ Docker-based build automation

The project is under active development, with additional features planned to improve automation, monitoring, and analytics.

---

# Roadmap

Future enhancements include:

## Infrastructure

- GitHub Actions CI/CD
- Terraform remote state
- Automated deployment pipeline
- Infrastructure validation

## Data Engineering

- Data quality validation
- Athena integration
- AWS Glue Data Catalog
- Amazon EventBridge enhancements

## Monitoring

- CloudWatch Dashboard
- CloudWatch Alarms
- Centralized logging
- Cost monitoring

## Analytics

- Enhanced dashboard visualizations
- Historical trend analysis
- Topic modeling
- Sentiment analysis

## Software Engineering

- Unit tests
- Integration tests
- Code quality automation
- Performance optimization

---

# Documentation

Additional documentation is available in the `docs/` directory.

| Document | Description |
|----------|-------------|
| ARCHITECTURE.md | System architecture and component overview |
| DEPLOYMENT.md | Complete deployment guide |

Additional documentation will be added in future releases.

---

# Why This Project?

This project was developed to explore modern cloud-native data engineering practices using AWS serverless services.

Rather than building a monolithic application, the solution demonstrates how an event-driven architecture can be used to construct scalable, maintainable, and modular data pipelines with minimal operational overhead.

The project also serves as a portfolio example showcasing:

- Cloud Engineering
- Serverless Computing
- Infrastructure as Code
- Event-Driven Architecture
- Data Engineering
- Natural Language Processing
- AWS Automation

---

# Contributing

Contributions, suggestions, and feedback are welcome.

If you discover an issue or have ideas for improvements, please open an Issue or submit a Pull Request.

---

# License

This project is licensed under the MIT License.

See the LICENSE file for details.

---

# Acknowledgements

This project uses publicly available data from the Hacker News API.

- Hacker News
- Firebase Hacker News API

Special thanks to the open-source community and the maintainers of:

- Terraform
- AWS Lambda
- SpaCy
- NLTK
- Docker

---

## Author

**Ho, Anh Thu**

Master of Computer and Information Science (Data Science)

Cloud Engineering • Data Engineering • AI • Software Engineering

GitHub: https://github.com/uscsds
---

