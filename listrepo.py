import requests
from requests.auth import HTTPBasicAuth
import csv

# Replace with your Bitbucket Cloud credentials
BITBUCKET_USERNAME = "your_username"  # Replace with your Bitbucket Cloud username
BITBUCKET_API_TOKEN = "your_api_token"  # Replace with your API token
WORKSPACE = "your_workspace"  # Replace with your workspace ID

def list_bitbucket_projects(username, api_token, workspace):
    url = f"https://api.bitbucket.org/2.0/workspaces/{workspace}/projects"
    projects = []
    params = {'pagelen': 100}  # Fetch 100 projects per page

    while url:
        response = requests.get(url, auth=HTTPBasicAuth(username, api_token), params=params)
        if response.status_code != 200:
            print(f"Failed to fetch projects: {response.status_code} - {response.text}")
            return []

        data = response.json()
        projects.extend(data.get("values", []))
        url = data.get("next")  # Get the next page URL if available

    return projects

def list_repositories_in_project(username, api_token, workspace, project_key):
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}"
    repositories = []
    params = {'q': f'project.key="{project_key}"', 'pagelen': 100}  # Filter by project key

    while url:
        response = requests.get(url, auth=HTTPBasicAuth(username, api_token), params=params)
        if response.status_code != 200:
            print(f"Failed to fetch repositories for project {project_key}: {response.status_code} - {response.text}")
            return []

        data = response.json()
        repositories.extend(data.get("values", []))
        url = data.get("next")  # Get the next page URL if available

    return repositories

def write_to_csv(data, file_name):
    headers = ["Project Name", "Project Key", "Repository Name", "Repository URL"]
    with open(file_name, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(data)

if __name__ == "__main__":
    # Fetch all projects in the workspace
    projects = list_bitbucket_projects(BITBUCKET_USERNAME, BITBUCKET_API_TOKEN, WORKSPACE)

    if not projects:
        print("No projects found or failed to fetch projects.")
    else:
        print(f"Found {len(projects)} projects. Fetching repositories...")

        # Prepare data for CSV
        csv_data = []
        for project in projects:
            project_name = project.get("name", "Unknown")
            project_key = project.get("key", "Unknown")

            print(f"Fetching repositories for project: {project_name} (Key: {project_key})")
            repositories = list_repositories_in_project(BITBUCKET_USERNAME, BITBUCKET_API_TOKEN, WORKSPACE, project_key)

            for repo in repositories:
                repo_name = repo.get("name", "Unknown")
                repo_url = repo.get("links", {}).get("html", {}).get("href", "Unknown")
                csv_data.append([project_name, project_key, repo_name, repo_url])

        # Write to CSV file
        csv_file_name = "bitbucket_projects_and_repositories.csv"
        write_to_csv(csv_data, csv_file_name)
        print(f"Data written to {csv_file_name}")
