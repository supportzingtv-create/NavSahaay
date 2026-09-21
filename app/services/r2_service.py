import os
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

        if all([self.account_id, self.access_key, self.secret_key]):
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
            raise Exception("R2 credentials not configured properly.")

        filename = secure_filename(file_obj.filename)
        # Add timestamp to prevent name collisions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        key = f"{folder}/{timestamp}_{filename}"

        try:
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                key,
                ExtraArgs={'ContentType': file_obj.content_type}
            )

            if self.public_url:
                return f"{self.public_url}/{key}"
            else:
                return f"https://{self.account_id}.r2.cloudflarestorage.com/{self.bucket_name}/{key}"
        except Exception as e:
            print(f"R2 Upload Error: {e}")
            raise e

r2_service = R2Service()
