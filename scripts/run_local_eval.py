#!/usr/bin/env python3
"""
Local evaluation script with optional S3 upload
Usage:
    python scripts/run_local_eval.py              # Run eval locally only
    python scripts/run_local_eval.py --upload-s3  # Run eval and upload to S3
"""
import argparse
import requests
import json
import boto3
from datetime import datetime
import sys
import os

def run_eval(backend_url="http://localhost:8000"):
    """Run evaluation against local backend"""
    print("🔄 Running evaluation...")
    print(f"   Backend: {backend_url}")

    try:
        response = requests.get(f"{backend_url}/eval/quick", timeout=300)
        response.raise_for_status()
        results = response.json()

        print(f"✅ Evaluation complete!")
        print(f"   Items: {results.get('items', 0)}")
        print(f"   Precision: {results.get('codes_precision', 0):.2f}")
        print(f"   Recall: {results.get('codes_recall', 0):.2f}")
        print(f"   F1 Score: {results.get('codes_f1', 0):.2f}")

        return results

    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        sys.exit(1)


def upload_to_s3(results, bucket="med-docs-dev", region="ap-south-1"):
    """Upload evaluation results to S3"""
    print("\n☁️  Uploading to S3...")
    print(f"   Bucket: {bucket}")

    try:
        # Add metadata
        results["metadata"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "source": "local-development",
            "uploaded_by": os.getenv("USER", "local-dev"),
        }

        s3 = boto3.client("s3", region_name=region)

        # Upload as latest
        s3.put_object(
            Bucket=bucket,
            Key="eval-results/latest.json",
            Body=json.dumps(results, indent=2),
            ContentType="application/json",
            CacheControl="no-cache"
        )
        print(f"✅ Uploaded: s3://{bucket}/eval-results/latest.json")

        # Also upload with timestamp for history
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_key = f"eval-results/local-dev_{timestamp}.json"
        s3.put_object(
            Bucket=bucket,
            Key=history_key,
            Body=json.dumps(results, indent=2),
            ContentType="application/json"
        )
        print(f"✅ Uploaded: s3://{bucket}/{history_key}")

        return True

    except Exception as e:
        print(f"❌ S3 upload failed: {e}")
        print(f"   Make sure AWS credentials are configured:")
        print(f"   - aws configure")
        print(f"   - or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run local evaluation with optional S3 upload")
    parser.add_argument("--upload-s3", action="store_true", help="Upload results to S3")
    parser.add_argument("--backend", default="http://localhost:8000", help="Backend URL")
    parser.add_argument("--bucket", default="med-docs-dev", help="S3 bucket name")
    args = parser.parse_args()

    print("=" * 60)
    print("🧪 Local Evaluation Script")
    print("=" * 60)

    # Run evaluation
    results = run_eval(args.backend)

    # Optionally upload to S3
    if args.upload_s3:
        success = upload_to_s3(results, args.bucket)
        if not success:
            sys.exit(1)
    else:
        print("\n💡 Tip: Use --upload-s3 to upload results to S3")

    print("\n✅ Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
