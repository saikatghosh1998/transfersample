import requests
from requests.auth import HTTPBasicAuth

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

if __name__ == "__main__":
    projects = list_bitbucket_projects(BITBUCKET_USERNAME, BITBUCKET_API_TOKEN, WORKSPACE)
    if projects:
        print(f"Found {len(projects)} projects in workspace '{WORKSPACE}':")
        for project in projects:
            print(f"- {project['name']} (Key: {project['key']})")
    else:
        print("No projects found or failed to fetch projects.")
