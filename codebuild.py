import boto3
import json

def list_codebuild_projects():
    client = boto3.client('codebuild')
    projects_info = []
    
    # List all CodeBuild project names
    project_names = client.list_projects()['projects']
    
    for project_name in project_names:
        # Fetch detailed information for each project
        project_info = client.batch_get_projects(names=[project_name])['projects'][0]
        
        # Extract relevant details
        environment_variables = project_info['environment'].get('environmentVariables', [])
        
        project_details = {
            'ProjectName': project_info['name'],
            'ServiceRole': project_info.get('serviceRole', 'N/A'),
            'EnvironmentVariables': [
                {
                    'Name': var.get('name'),
                    'Value': var.get('value'),
                    'Type': var.get('type', 'PLAINTEXT')
                } for var in environment_variables
            ]
        }
        
        projects_info.append(project_details)
    
    return projects_info

def write_to_file(projects_info, file_name="codebuild_projects.json"):
    with open(file_name, 'w') as f:
        json.dump(projects_info, f, indent=4)
    
    print(f"Data has been written to {file_name}")

def main():
    projects_info = list_codebuild_projects()
    write_to_file(projects_info)

if __name__ == "__main__":
    main()
