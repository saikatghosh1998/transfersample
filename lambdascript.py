import boto3
import json

def list_lambda_functions():
    client = boto3.client('lambda')
    zip_functions = []
    image_functions = []
    
    paginator = client.get_paginator('list_functions')
    for page in paginator.paginate():
        for function in page['Functions']:
            function_name = function['FunctionName']
            package_type = function.get('PackageType', 'Zip')
            runtime = function.get('Runtime', 'N/A')
            memory_size = function.get('MemorySize', 'N/A')
            timeout = function.get('Timeout', 'N/A')
            handler = function.get('Handler', 'N/A')

            function_info = {
                'FunctionName': function_name,
                'Runtime': runtime,
                'MemorySize': memory_size,
                'Timeout': timeout,
                'Handler': handler,
                'PackageType': package_type
            }

            # Classify based on package type
            if package_type == 'Image':
                image_functions.append(function_info)
            else:
                zip_functions.append(function_info)
    
    return zip_functions, image_functions

def write_to_file(zip_functions, image_functions, file_name="lambda_functions.json"):
    data = {
        'ZIP-based Lambda Functions': zip_functions,
        'Image-based Lambda Functions': image_functions
    }
    
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"Data has been written to {file_name}")

def main():
    zip_functions, image_functions = list_lambda_functions()
    write_to_file(zip_functions, image_functions)

if __name__ == "__main__":
    main()
