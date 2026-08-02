#!/bin/bash

# Configuration
BUCKET_NAME="hn-dashboard-3214147"
SOURCE_DIR="./dist"

echo "🔄 Syncing $SOURCE_DIR to s3://$BUCKET_NAME ..."

aws s3 sync "$SOURCE_DIR" "s3://$BUCKET_NAME/" \
  --delete \
  --cache-control "max-age=0,no-cache,no-store,must-revalidate"

echo "✅ Deployment complete!"
echo "🌍 Visit your dashboard at:"
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document index.html
