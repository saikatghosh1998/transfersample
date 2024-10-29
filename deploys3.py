import boto3
import json
from botocore.exceptions import ClientError

def create_s3_buckets(buckets_data, target_account_session):
    s3_client = target_account_session.client('s3')
    
    for bucket_info in buckets_data:
        bucket_name = bucket_info['BucketName']
        print(f"Creating bucket: {bucket_name}")
        
        # Create the S3 bucket
        try:
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
            
            # Set bucket policy if it exists
            if 'Policy' in bucket_info and bucket_info['Policy'] != 'No policy attached':
                policy = json.dumps(bucket_info['Policy'])
                s3_client.put_bucket_policy(Bucket=bucket_name, Policy=policy)
                print(f"Policy applied to bucket '{bucket_name}'.")
        
        except ClientError as e:
            print(f"Error creating bucket '{bucket_name}': {e.response['Error']['Message']}")

def main():
    input_file = "s3_buckets_with_policies.json"  # Replace with your output file name
    
    # Load the buckets data from the JSON file
    try:
        with open(input_file, 'r') as f:
            buckets_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file '{input_file}' is not a valid JSON.")
        return
    
    # Create a session for the target account (specify the correct region and credentials)
    target_account_session = boto3.Session(
        aws_access_key_id='YOUR_TARGET_ACCOUNT_ACCESS_KEY',
        aws_secret_access_key='YOUR_TARGET_ACCOUNT_SECRET_KEY',
        region_name='YOUR_TARGET_REGION'  # e.g., 'us-east-1'
    )
    
    create_s3_buckets(buckets_data, target_account_session)

if __name__ == "__main__":
    main()
