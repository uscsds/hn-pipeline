#!/bin/bash

BUCKET_NAME="your-bucket-name"
PREFIX="analysis/"
TMP_INDEX="index.json"

# Step 1: List objects in analysis folder and extract timestamps
aws s3api list-objects-v2 \
  --bucket "$BUCKET_NAME" \
  --prefix "$PREFIX" \
  --query "Contents[].Key" \
  --output text | \
  grep -oP '_\K[0-9]{8}T[0-9]{6}(?=\.json)' | \
  sort -u > timestamps.txt

# Step 2: Convert to JSON array
echo "[" > "$TMP_INDEX"
sed '$!s/$/,/' timestamps.txt >> "$TMP_INDEX"
echo "]" >> "$TMP_INDEX"

# Step 3: Upload to S3
aws s3 cp "$TMP_INDEX" "s3://$BUCKET_NAME/${PREFIX}index.json"

# Clean up
rm "$TMP_INDEX" timestamps.txt

echo "✅ index.json updated in S3."
