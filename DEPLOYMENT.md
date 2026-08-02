# Deployment Guide

This document describes how to deploy the HN Pipeline on AWS.

The deployment process provisions AWS infrastructure using Terraform, builds Lambda deployment packages and shared Lambda Layers, and configures an automated event-driven ETL pipeline.

---

# Deployment Overview

Deployment consists of the following stages:

1. Clone the repository
2. Configure AWS credentials
3. Build Lambda deployment packages
4. Build Lambda Layers
5. Upload Lambda Layers
6. Deploy infrastructure using Terraform
7. Verify deployment

---

# Prerequisites

## AWS

- AWS Account
- IAM user or role with permissions to create:
  - Lambda
  - IAM
  - S3
  - CloudWatch
  - Lambda Layers

---

## Local Software

Required tools:

- Git
- Docker
- Python 3.11
- Terraform
- AWS CLI

Verify installation

```bash
git --version
docker --version
python3 --version
terraform --version
aws --version
```

---

# Repository

Clone the repository.

```bash
git clone https://github.com/uscsds/hn-pipeline.git

cd hn-pipeline
```

---

# Configure AWS Credentials

Configure AWS CLI.

```bash
aws configure
```

Provide

```
AWS Access Key ID

AWS Secret Access Key

Default Region

Output Format
```

Verify

```bash
aws sts get-caller-identity
```

---

# Build Lambda Deployment Packages

Navigate to the build scripts.

```bash
cd lambda/scripts
```

Build deployment packages.

```bash
./build_lambda.sh
```

This script packages the Lambda source code into deployment ZIP files.

---

# Build Lambda Layers

Shared dependencies are packaged separately as Lambda Layers.

Build all layers.

```bash
./build_layers.sh
```

Depending on the layer, Docker may be used to ensure compatibility with the AWS Lambda Python runtime.

The generated ZIP files are uploaded as Lambda Layer versions before Terraform deployment.

---

# Upload Lambda Layers

The build scripts generate ZIP packages for the shared Lambda Layers.

Typical layers include:

| Layer | Purpose |
|--------|---------|
| nltk_layer | NLTK libraries and datasets |
| spacy_layer | SpaCy runtime and English language model |
| other_layer | Shared third-party Python dependencies |

After building the layers, publish them to AWS Lambda.

Example:

```bash
aws lambda publish-layer-version \
    --layer-name hn-spacy-layer \
    --zip-file fileb://spacy_layer.zip \
    --compatible-runtimes python3.11
```

Repeat for each layer.

After publishing, note the generated Layer Version ARN.

Example

```
arn:aws:lambda:us-east-1:123456789012:layer:hn-spacy-layer:3
```

Update the corresponding Terraform variables or configuration files before deployment.

---

# Deploy Infrastructure

Navigate to the Terraform directory.

```bash
cd lambda/terraform
```

Initialize Terraform.

```bash
terraform init
```

Review the execution plan.

```bash
terraform plan
```

Deploy the infrastructure.

```bash
terraform apply
```

Terraform provisions the required AWS resources, including:

- IAM Roles
- Lambda Functions
- Lambda Permissions
- CloudWatch Event Rules
- CloudWatch Targets
- Amazon S3 Event Notifications

Deployment typically takes several minutes depending on the AWS account and region.

---

# Verify Deployment

After deployment, verify the following resources have been created successfully.

## Lambda Functions

- fetch_hn_data
- clean_hn_data
- process_hn_data

## Lambda Layers

- nltk_layer
- spacy_layer
- other_layer

## Amazon S3

Verify that the required buckets exist.

Check that folders such as

```
raw/
cleaned/
processed/
state/
```

are created as expected after pipeline execution.

## CloudWatch

Confirm that the scheduled Event Rule has been created and enabled.

## IAM

Verify that the Lambda execution role has been attached successfully.

---

# Test the Pipeline

The pipeline should execute automatically after deployment.

Typical execution flow:

```
CloudWatch
        │
        ▼
Fetch Lambda
        │
        ▼
Raw Bucket
        │
        ▼
Clean Lambda
        │
        ▼
Clean Bucket
        │
        ▼
Process Lambda
        │
        ▼
Processed Bucket
```

Alternatively, individual Lambda functions can be tested from the AWS Console using sample test events.

---

# Updating Lambda Code

After modifying a Lambda function:

1. Rebuild the deployment package.

```bash
./build_lambda.sh
```

2. Redeploy using Terraform.

```bash
terraform apply
```

---

# Updating Lambda Layers

When dependencies change:

1. Rebuild the layer.

```bash
./build_layers.sh
```

2. Publish a new Lambda Layer version.

3. Update the Layer ARN in Terraform.

4. Run

```bash
terraform apply
```

AWS Lambda Layers are immutable, so publishing a new version is required whenever layer contents change.

---

# Destroy Infrastructure

To remove all provisioned AWS resources:

```bash
terraform destroy
```

Always review the execution plan before confirming resource deletion.

---

# Troubleshooting

## Layer version does not exist

Verify that the referenced Layer Version ARN exists in the configured AWS Region.

---

## Lambda cannot import Python packages

Common causes include:

- Incorrect Python runtime version
- Layer built on an incompatible operating system
- Incorrect Lambda Layer directory structure
- Missing shared libraries

Recommendation:

Build layers using Docker with an Amazon Linux environment compatible with the AWS Lambda Python 3.11 runtime.

---

## Terraform deployment fails

Check:

- AWS credentials
- IAM permissions
- Bucket names
- Terraform variables
- Existing AWS resources with conflicting names

---

## Lambda timeout

Possible causes:

- Network connectivity
- Long-running processing
- Insufficient Lambda timeout configuration

Increase the Lambda timeout if necessary.

---

## Amazon S3 notification errors

Verify:

- Lambda permission exists
- Bucket notification configuration is valid
- Correct bucket ARN is configured

---

## Docker build issues

Common causes include:

- ARM vs AMD64 architecture mismatch
- Incorrect Docker base image
- Missing build dependencies
- Python runtime incompatibility

---

# Additional Resources

- AWS Lambda Documentation
- Terraform Documentation
- Hacker News API Documentation
- Docker Documentation
- SpaCy Documentation
- NLTK Documentation

---

# Summary

The deployment workflow consists of four primary stages:

1. Build Lambda deployment packages.
2. Build and publish Lambda Layers.
3. Deploy AWS infrastructure using Terraform.
4. Verify automated pipeline execution.

Once deployed successfully, the pipeline operates automatically using CloudWatch scheduling and Amazon S3 event notifications without requiring manual intervention.




