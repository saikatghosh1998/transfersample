import boto3
import json
import os

def get_codebuild_projects_info():
    codebuild_client = boto3.client('codebuild')
    project_info_list = []

    # Create a folder named 'build' if it doesn't exist
    os.makedirs('build', exist_ok=True)

    # List all CodeBuild project names
    try:
        projects = codebuild_client.list_projects()
    except Exception as e:
        print(f"Error listing CodeBuild projects: {e}")
        return []

    for project_name in projects['projects']:
        try:
            # Get detailed information for each project
            project_details = codebuild_client.batch_get_projects(names=[project_name])
            project = project_details['projects'][0]

            # Extract environment variables and primary source
            project_info = {
                'ProjectName': project['name'],
                'EnvironmentVariables': [
                    {'Name': env['name'], 'Value': env['value']} for env in project.get('environment', {}).get('environmentVariables', [])
                ],
                'PrimarySource': {
                    'Type': project.get('source', {}).get('type', 'Unknown'),
                    'Location': project.get('source', {}).get('location', 'No location specified')
                }
            }

            # Handle the buildspec file
            buildspec_content = project.get('source', {}).get('buildspec')
            if buildspec_content:
                # Save the buildspec content to a file in the 'build' folder
                buildspec_file_path = f'build/{project["name"]}_buildspec.yml'
                with open(buildspec_file_path, 'w') as buildspec_file:
                    buildspec_file.write(buildspec_content)
                project_info['BuildSpecFile'] = buildspec_file_path
            else:
                project_info['BuildSpecFile'] = "No inline buildspec specified or external buildspec used"

            project_info_list.append(project_info)

        except Exception as e:
            print(f"Error getting details for project {project_name}: {e}")

    return project_info_list

def write_to_file(project_info_list, file_name='codebuild_projects_info.json'):
    try:
        with open(file_name, 'w') as f:
            json.dump(project_info_list, f, indent=4)
        print(f"CodeBuild project details written to {file_name}")
    except Exception as e:
        print(f"Error writing to file: {e}")

def main():
    project_info_list = get_codebuild_projects_info()
    write_to_file(project_info_list)

if __name__ == "__main__":
    main()
