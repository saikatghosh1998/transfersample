import boto3
import json

def list_codebuild_projects():
    client = boto3.client('codebuild')
    projects_data = []

    # Retrieve the list of CodeBuild project names
    project_names = client.list_projects()['projects']

    for project_name in project_names:
        # Get project details
        project_details = client.batch_get_projects(names=[project_name])['projects'][0]
        
        # Extract environment variables
        environment_variables = [
            {
                "Name": env_var['name'],
                "Value": env_var['value'],
                "Type": env_var.get('type', 'PLAINTEXT')  # Default type to PLAINTEXT if not specified
            }
            for env_var in project_details['environment']['environmentVariables']
        ]
        
        # Get buildspec (if specified in the project configuration)
        buildspec = project_details.get('source', {}).get('buildspec', 'Not specified in project')

        # Structure project data
        project_info = {
            'ProjectName': project_name,
            'EnvironmentVariables': environment_variables,
            'Buildspec': buildspec,
            'ServiceRole': project_details.get('serviceRole', 'N/A'),
            'EnvironmentType': project_details['environment']['type'],
            'Image': project_details['environment'].get('image', 'N/A'),
            'ComputeType': project_details['environment'].get('computeType', 'N/A')
        }

        projects_data.append(project_info)
    
    return projects_data

def write_to_file(projects_data, file_name="codebuild_projects.json"):
    with open(file_name, 'w') as f:
        json.dump(projects_data, f, indent=4)
    
    print(f"Data has been written to {file_name}")

def main():
    projects_data = list_codebuild_projects()
    write_to_file(projects_data)

if __name__ == "__main__":
    main()
