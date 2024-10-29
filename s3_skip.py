import boto3
import json

def list_s3_buckets_with_policies():
    s3_client = boto3.client('s3')
    buckets_data = []

    # Get the list of all S3 buckets
    buckets = s3_client.list_buckets()['Buckets']
    
    for bucket in buckets:
        bucket_name = bucket['Name']
        bucket_info = {'BucketName': bucket_name}
        
        # Attempt to get the bucket policy, handle permission errors
        try:
            policy = s3_client.get_bucket_policy(Bucket=bucket_name)['Policy']
            bucket_info['Policy'] = json.loads(policy)
        except s3_client.exceptions.NoSuchBucketPolicy:
            bucket_info['Policy'] = 'No policy attached'
        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                bucket_info['Policy'] = 'No permission to access'
            else:
                bucket_info['Policy'] = f"Error: {e.response['Error']['Message']}"
        
        buckets_data.append(bucket_info)
    
    return buckets_data

def write_to_file(buckets_data, file_name="s3_buckets_with_policies.json"):
    with open(file_name, 'w') as f:
        json.dump(buckets_data, f, indent=4)
    
    print(f"Data has been written to {file_name}")

def main():
    buckets_data = list_s3_buckets_with_policies()
    write_to_file(buckets_data)

if __name__ == "__main__":
    main()
