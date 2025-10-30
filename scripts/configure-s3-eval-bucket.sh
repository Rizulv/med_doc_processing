#!/bin/bash
set -e

BUCKET="med-docs-dev"
REGION="ap-south-1"

echo "Configuring S3 bucket for eval results..."

# Create bucket policy for public read access to eval-results/*
cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadEvalResults",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${BUCKET}/eval-results/*"
    }
  ]
}
EOF

# Apply bucket policy
aws s3api put-bucket-policy \
  --bucket $BUCKET \
  --policy file:///tmp/bucket-policy.json \
  --region $REGION

echo "✅ Bucket policy applied"

# Enable CORS for browser access
cat > /tmp/cors-config.json <<EOF
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "HEAD"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3600
    }
  ]
}
EOF

aws s3api put-bucket-cors \
  --bucket $BUCKET \
  --cors-configuration file:///tmp/cors-config.json \
  --region $REGION

echo "✅ CORS configuration applied"
echo ""
echo "S3 bucket configured successfully!"
echo "Eval results will be publicly readable at:"
echo "  https://${BUCKET}.s3.${REGION}.amazonaws.com/eval-results/latest.json"
