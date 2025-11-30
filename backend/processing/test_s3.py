import os
import sys
sys.path.append('backend/processing')

from s3_storage import S3Storage

def test_s3_connection():
    S3_BUCKET_NAME = "smart-clipboard-downloads"
    AWS_ACCESS_KEY_ID = "-retracted-"
    AWS_SECRET_ACCESS_KEY = "-retracted-"
    AWS_REGION = "us-east-1"
    bucket_name=S3_BUCKET_NAME,
    access_key=AWS_ACCESS_KEY_ID,
    secret_key=AWS_SECRET_ACCESS_KEY,
    region=AWS_REGION
    if not access_key or not secret_key:
        print("AWS credentials not found in environment variables")
        print("Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return False
    
    print(f"Testing S3 connection to bucket: {bucket_name}")
    print(f"Region: {region}")
    
    try:
        s3_storage = S3Storage(
            bucket_name=bucket_name,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        test_output_data = {
            "message": "Test latex conversion successful",
            "latex_conversion": "\\begin{equation}\nE = mc^2\n\\end{equation}",
            "is_math": True,
            "classification": {"math": True, "link": False, "date": False, "address": False},
            "status": "success"
        }
        test_metadata = {"test": True, "source": "test_script", "processing_type": "test"}
        
        print("Configuring bucket for public access...")
        bucket_result = s3_storage.setup_public_bucket()
        if bucket_result["success"]:
            print("Bucket configured for public access")
        else:
            print(f"Bucket configuration warning: {bucket_result['error']}")
        
        result = s3_storage.upload_json_output(test_output_data, test_metadata)
        
        if result["success"]:
            print("S3 JSON upload test successful!")
            print(f"   Public URL: {result['url']}")
            print(f"   S3 URI: {result['s3_uri']}")
            print(f"   Content Type: {result['content_type']}")
            return True
        else:
            print(f"S3 upload test failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"S3 connection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_s3_connection()
