import boto3
import pandas as pd
import io
import os

BUCKET = "ecommerce-dashboard-pavansai"
REGION = "us-east-1"

def get_s3_client():
    return boto3.client('s3', region_name=REGION)

def upload_csv_to_s3(df, filename):
    """When user uploads CSV → save it to S3 automatically."""
    try:
        s3 = get_s3_client()
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        key = f"uploads/{filename}"
        s3.put_object(
            Bucket=BUCKET,
            Key=key,
            Body=buffer.getvalue(),
            ContentType='text/csv'
        )
        return True, key
    except Exception as e:
        return False, str(e)

def list_files_in_s3():
    """Show all CSV files stored in S3."""
    try:
        s3 = get_s3_client()
        response = s3.list_objects_v2(
            Bucket=BUCKET,
            Prefix='uploads/'
        )
        files = []
        for obj in response.get('Contents', []):
            name = obj['Key'].replace('uploads/', '')
            size_kb = round(obj['Size'] / 1024, 1)
            files.append(f"{name} ({size_kb} KB)")
        return files
    except Exception as e:
        return []
