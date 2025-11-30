import boto3
import json
import os
from datetime import datetime
from botocore.exceptions import ClientError

class S3Storage:
    def __init__(self, bucket_name, aws_access_key_id=None, aws_secret_access_key=None, region_name='us-east-1'):
        self.bucket_name = bucket_name
        self.region_name = region_name
        
        if aws_access_key_id and aws_secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name
            )
        else:
            self.s3_client = boto3.client('s3', region_name=region_name)
    
    def setup_public_bucket(self):
        """setup bucket for public access"""
        try:
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                    }
                ]
            }
            
            self.s3_client.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            
            cors_configuration = {
                'CORSRules': [
                    {
                        'AllowedHeaders': ['*'],
                        'AllowedMethods': ['GET', 'HEAD'],
                        'AllowedOrigins': ['*'],
                        'ExposeHeaders': ['ETag'],
                        'MaxAgeSeconds': 3000
                    }
                ]
            }
            
            self.s3_client.put_bucket_cors(
                Bucket=self.bucket_name,
                CORSConfiguration=cors_configuration
            )
            
            self.s3_client.put_public_access_block(
                Bucket=self.bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': False,
                    'IgnorePublicAcls': False,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            )
            
            return {"success": True, "message": "Bucket configured for public access with CORS"}
            
        except ClientError as e:
            return {"success": False, "error": f"Failed to configure bucket: {str(e)}"}
    
    def upload_json_output(self, output_data, metadata=None):
        """upload output data as JSON to S3"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_key = f"outputs/{timestamp}_result.json"
            
            json_data = {
                "timestamp": timestamp,
                "processing_result": output_data,
                "metadata": metadata or {}
            }
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=json.dumps(json_data, indent=2),
                ContentType='application/json'
            )
            
            public_url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{file_key}"
            
            return {
                "success": True,
                "s3_key": file_key,
                "bucket": self.bucket_name,
                "url": public_url,
                "s3_uri": f"s3://{self.bucket_name}/{file_key}",
                "content_type": "application/json"
            }
            
        except ClientError as e:
            return {
                "success": False,
                "error": f"S3 upload failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    def upload_latex_output(self, latex_content, metadata=None):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_key = f"latex_outputs/{timestamp}_output.txt"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=latex_content,
                ContentType='text/plain'
            )
            
            public_url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{file_key}"
            
            return {
                "success": True,
                "s3_key": file_key,
                "bucket": self.bucket_name,
                "url": public_url,
                "s3_uri": f"s3://{self.bucket_name}/{file_key}"
            }
            
        except ClientError as e:
            return {
                "success": False,
                "error": f"S3 upload failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def generate_presigned_url(self, object_key, expiration=3600):
        """generate presigned URL for S3 access"""
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=expiration
            )
            return {"success": True, "url": response}
        except ClientError as e:
            return {"success": False, "error": f"Failed to generate presigned URL: {str(e)}"}
    
    def upload_image_with_latex(self, image_path, latex_content, metadata=None):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            image_key = f"images/{timestamp}_input.png"
            latex_key = f"latex_outputs/{timestamp}_output.txt"
            
            with open(image_path, 'rb') as image_file:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=image_key,
                    Body=image_file,
                    ContentType='image/png'
                )
            
            image_public_url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{image_key}"
            latex_public_url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{latex_key}"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=latex_key,
                Body=latex_content,
                ContentType='text/plain'
            )
            
            return {
                "success": True,
                "image_s3_key": image_key,
                "latex_s3_key": latex_key,
                "bucket": self.bucket_name,
                "image_url": image_public_url,
                "latex_url": latex_public_url,
                "image_s3_uri": f"s3://{self.bucket_name}/{image_key}",
                "latex_s3_uri": f"s3://{self.bucket_name}/{latex_key}"
            }
            
        except ClientError as e:
            return {
                "success": False,
                "error": f"S3 upload failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }