import boto3
import json

def list_s3_buckets_with_policies(bucket_names):
    s3_client = boto3.client('s3')
    buckets_data = []

    for bucket_name in bucket_names:
        # Ensure we have a clean bucket name
        bucket_name = bucket_name.strip()  # Strip whitespace
        if not bucket_name:  # Skip empty lines
            continue
        
        bucket_info = {'BucketName': bucket_name}
        
        # Attempt to get the bucket policy, handle permission errors
        try:
            policy_response = s3_client.get_bucket_policy(Bucket=bucket_name)
            policy = policy_response['Policy']
            bucket_info['Policy'] = json.loads(policy)
        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                bucket_info['Policy'] = 'No policy attached'
            elif e.response['Error']['Code'] == 'AccessDenied':
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
    # Read bucket names from the provided text file
    input_file = "buckets.txt"  # Replace with your input file name
    try:
        with open(input_file, 'r') as f:
            bucket_names = f.readlines()
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        return
    
    # Process bucket names
    buckets_data = list_s3_buckets_with_policies(bucket_names)
    write_to_file(buckets_data)

if __name__ == "__main__":
    main()
