import requests

# Configuration
BITBUCKET_WORKSPACE = "your_workspace"  # Replace with your Bitbucket Cloud workspace
BITBUCKET_PROJECT = "your_project"  # Replace with your Bitbucket Cloud project key
BITBUCKET_USERNAME = "your_username"  # Replace with your Bitbucket username
BITBUCKET_APP_PASSWORD = "your_app_password"  # Replace with your Bitbucket app password

# Bitbucket API URL
BITBUCKET_API_URL = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}"

def list_repositories_in_project(project_key):
    """
    Fetch and list all repositories in a given Bitbucket Cloud project.
    """
    repo_list = []
    next_url = BITBUCKET_API_URL + f"?q=project.key=\"{project_key}\""

    while next_url:
        response = requests.get(next_url, auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))
        
        if response.status_code == 200:
            data = response.json()
            for repo in data.get("values", []):
                repo_list.append({
                    "name": repo["name"],
                    "slug": repo["slug"],
                    "url": repo["links"]["html"]["href"],
                })
            next_url = data.get("next")  # Handle pagination
        else:
            print(f"Failed to fetch repositories: {response.status_code}, {response.text}")
            break

    return repo_list

def main():
    print(f"Fetching repositories in project: {BITBUCKET_PROJECT}")
    repositories = list_repositories_in_project(BITBUCKET_PROJECT)
    
    if repositories:
        print(f"Found {len(repositories)} repositories:")
        for repo in repositories:
            print(f"- Name: {repo['name']}, Slug: {repo['slug']}, URL: {repo['url']}")
    else:
        print("No repositories found or failed to fetch.")

if __name__ == "__main__":
    main()
