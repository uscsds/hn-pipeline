# System Architecture

## Overview

HN Pipeline is a serverless, event-driven ETL (Extract, Transform, Load) pipeline built on AWS. The system automatically retrieves Hacker News stories, preprocesses the data, performs natural language processing (NLP), and stores processed datasets for downstream visualization and analytics.

The architecture follows a modular design where each processing stage is implemented as an independent AWS Lambda function. Communication between stages is handled through Amazon S3 events, allowing each component to scale independently while remaining loosely coupled.

---

# High-Level Architecture

```

                    +--------------------+
                    | CloudWatch Events  |
                    |  (15-minute timer) |
                    +---------+----------+
                              |
                              v
                   +----------------------+
                   | fetch_hn_data Lambda |
                   +----------+-----------+
                              |
                              v
                     Raw Data S3 Bucket
                              |
                 S3 ObjectCreated Event
                              |
                              v
                   +----------------------+
                   | clean_hn_data Lambda |
                   +----------+-----------+
                              |
                              v
                  Cleaned Data S3 Bucket
                              |
                 S3 ObjectCreated Event
                              |
                              v
                 +-------------------------+
                 | process_hn_data Lambda  |
                 +------------+------------+
                              |
                              v
                 Processed Data S3 Bucket
                              |
                              v
                  Dashboard / Analytics

```

---

# Repository Architecture

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
│   │   └── *.tf
│   │
│   └── scripts/
│
├── dashboard/
│
├── tools/
│
└── docs/

```

---

# Processing Pipeline

The data processing workflow consists of three independent stages.

## Stage 1 — Data Collection

**Lambda Function**

`fetch_hn_data`

Responsibilities

- Connect to the Hacker News API
- Retrieve the latest stories
- Collect story metadata
- Store raw JSON files in Amazon S3

Output

```

raw/
    hn_top_raw_<timestamp>.json

```

CloudWatch automatically invokes this function every 15 minutes.

---

## Stage 2 — Data Cleaning

**Lambda Function**

`clean_hn_data`

Responsibilities

- Read raw datasets
- Remove duplicates
- Normalize text
- Remove HTML tags
- NLP preprocessing
- Update state files
- Save cleaned datasets

Output

```

cleaned/
    hn_top_cleaned_<timestamp>.json

```

This stage is automatically triggered by an S3 ObjectCreated event.

---

## Stage 3 — Data Processing

**Lambda Function**

`process_hn_data`

Responsibilities

- Perform additional processing
- Extract structured information
- Generate processed datasets
- Record processed file history

Output

```

processed/
    hn_top_processed_<timestamp>.json

```

This stage is also triggered automatically by Amazon S3 events.

---

# Event Flow

```

CloudWatch

↓

Fetch Lambda

↓

Raw Bucket

↓

S3 Notification

↓

Clean Lambda

↓

Clean Bucket

↓

S3 Notification

↓

Process Lambda

↓

Processed Bucket

↓

Dashboard

```

The pipeline requires no manual intervention after deployment.

---

# Amazon S3 Organization

The project uses multiple logical buckets (or prefixes, depending on deployment) to separate different stages of the ETL pipeline.

## Raw Data

Stores original Hacker News responses.

```

raw/

```

## Cleaned Data

Stores normalized datasets.

```

cleaned/

```

## Processed Data

Stores datasets ready for analysis.

```

processed/

```

## State Files

Stores pipeline state information.

Examples include:

```

state/
    global_seen_ids.json
    processed_files.json

```

State management enables incremental processing and prevents duplicate work.

---

# Lambda Layers

The project uses AWS Lambda Layers to share common dependencies across multiple Lambda functions. This approach reduces deployment package sizes, simplifies dependency management, and improves maintainability.

Current shared dependencies include:

| Layer | Purpose |
|--------|---------|
| nltk_layer | NLTK libraries and datasets |
| spacy_layer | SpaCy runtime and English language model |
| other_layer | Shared third-party Python packages |

Layers are built using Docker with an Amazon Linux environment compatible with the AWS Lambda Python 3.11 runtime.

Benefits include:

- Smaller Lambda deployment packages
- Faster deployments
- Shared dependencies across functions
- Independent layer versioning
- Simplified maintenance

---

# Terraform Organization

Infrastructure is managed using Terraform to enable reproducible and automated deployments.

The Terraform configuration is organized into reusable modules.

```

terraform/

├── modules/
│   └── lambda_function/
│
├── fetch_hn_data/
├── clean_hn_data/
├── process_hn_data/
├── shared_layer/
│
├── main.tf
├── variables.tf
├── outputs.tf
└── terraform.tfvars

```

Terraform provisions:

- AWS Lambda Functions
- IAM Roles and Policies
- Amazon S3 resources
- CloudWatch Event Rules
- CloudWatch Event Targets
- Lambda Permissions
- S3 Bucket Notifications

Using Infrastructure as Code (IaC) makes deployments repeatable, version-controlled, and easier to maintain.

---

# State Management

The pipeline is designed to support incremental processing.

Instead of reprocessing every file during each execution, state information is stored in Amazon S3.

Examples include:

```

state/
├── global_seen_ids.json
└── processed_files.json

```

These state files enable the pipeline to:

- Avoid duplicate processing
- Track previously processed datasets
- Resume processing after interruptions
- Improve overall efficiency

---

# Security

AWS Identity and Access Management (IAM) is used to grant each Lambda function only the permissions required to perform its tasks.

Typical permissions include:

- Read and write objects in Amazon S3
- Write execution logs to CloudWatch
- Invoke Lambda functions through configured event sources

This follows the principle of least privilege by limiting access to only the resources required for execution.

---

# Deployment Architecture

The project follows a serverless deployment model.

```

Developer

↓

Terraform

↓

AWS Infrastructure

↓

CloudWatch Scheduler

↓

Lambda Functions

↓

Amazon S3

↓

Dashboard

```

Application deployment consists of two primary steps:

1. Build Lambda deployment packages and shared layers.
2. Deploy infrastructure using Terraform.

Once deployed, the pipeline operates automatically without manual intervention.

---

# Design Decisions

## Why Serverless?

AWS Lambda eliminates the need to manage servers while automatically scaling with workload.

Benefits include:

- Reduced operational overhead
- Automatic scaling
- Pay-per-use pricing
- High availability

---

## Why Event-Driven Processing?

Each pipeline stage is triggered by events rather than direct function calls.

Advantages include:

- Loose coupling
- Independent scaling
- Simplified maintenance
- Improved fault isolation

---

## Why Separate Lambda Functions?

Each Lambda function performs a single responsibility.

Benefits include:

- Clear separation of concerns
- Independent development and testing
- Easier debugging
- Simplified deployment

---

## Why Lambda Layers?

Many Python dependencies are shared across multiple functions.

Using Lambda Layers avoids duplicating these dependencies in every deployment package and simplifies updates.

---

## Why Terraform?

Terraform enables the infrastructure to be defined as code.

Advantages include:

- Version-controlled infrastructure
- Reproducible deployments
- Easier collaboration
- Automated provisioning

---

# Scalability

The architecture supports horizontal scaling because each processing stage operates independently.

Potential future enhancements include:

- Amazon SQS buffering
- AWS Step Functions orchestration
- Amazon EventBridge integration
- Parallel data processing
- Dead Letter Queues (DLQs)
- CloudWatch alarms and monitoring

---

# Error Handling

Current error handling includes:

- Lambda execution logging through CloudWatch
- State tracking to reduce duplicate processing
- Independent processing stages to isolate failures

Future improvements may include:

- Automatic retries
- Dead Letter Queues
- Centralized monitoring
- Alerting
- Pipeline health dashboards

---

# Summary

HN Pipeline demonstrates a practical implementation of modern cloud-native data engineering using AWS serverless services.

Key architectural characteristics include:

- Serverless computing
- Event-driven processing
- Infrastructure as Code
- Modular Lambda design
- Shared dependency management
- Incremental ETL processing
- Cloud-native deployment
- NLP integration

The modular architecture allows each component to evolve independently while maintaining a simple, scalable, and maintainable overall system.





