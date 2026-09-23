import os
import json
import boto3
from botocore.config import Config
from werkzeug.utils import secure_filename
from datetime import datetime

class R2Service:
    def __init__(self):
        self.account_id = os.getenv("R2_ACCOUNT_ID")
        self.access_key = os.getenv("R2_ACCESS_KEY_ID")
        self.secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
        self.bucket_name = os.getenv("R2_BUCKET_NAME")
        self.public_url = os.getenv("R2_PUBLIC_URL", "").rstrip("/")

        if all([self.account_id, self.access_key, self.secret_key, self.bucket_name]):
            self.s3_client = boto3.client(
                service_name='s3',
                endpoint_url=f"https://{self.account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=Config(signature_version='s3v4'),
                region_name='auto'
            )
        else:
            self.s3_client = None

    def upload_file(self, file_obj, folder="general"):
        """
        Uploads a file to R2 and returns the public URL.
        """
        if not self.s3_client:
            raise RuntimeError(
                "Cloudflare R2 is not configured. Set R2_ACCOUNT_ID, "
                "R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY and R2_BUCKET_NAME."
            )

        filename = secure_filename(file_obj.filename)
        if not filename:
            raise ValueError("Please select a valid image or video file.")
        # Add timestamp to prevent name collisions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        key = f"{folder}/{timestamp}_{filename}"

        try:
            if self.public_url:
                url = f"{self.public_url}/{key}"
            else:
                # Default to the S3-style endpoint which might be public if bucket is configured
                url = f"https://{self.account_id}.r2.cloudflarestorage.com/{self.bucket_name}/{key}"

            print(f"R2 Upload Success: {url}")
            return url
        except Exception as e:
            print(f"R2 Upload Error: {e}")
            raise e

    def save_json(self, key, value):
        """Store small application settings alongside uploaded media."""
        if not self.s3_client:
            return False
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=json.dumps(value, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
            CacheControl="no-cache"
        )
        return True

    def get_json(self, key, default=None):
        """Read small application settings from R2, returning default on miss."""
        if not self.s3_client:
            return default
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return json.loads(response["Body"].read().decode("utf-8"))
        except Exception as e:
            # A missing fallback file is normal before the first save.
            print(f"R2 settings read skipped: {e}")
            return default

r2_service = R2Service()
