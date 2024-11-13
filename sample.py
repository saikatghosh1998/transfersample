import requests
import json

# Configuration variables
BITBUCKET_WORKSPACE = "your_workspace"  # Bitbucket Cloud workspace ID
BITBUCKET_REPO = "your_bitbucket_repo"  # Bitbucket Cloud repository name
BITBUCKET_USERNAME = "your_bitbucket_username"
BITBUCKET_APP_PASSWORD = "your_bitbucket_app_password"  # Bitbucket Cloud app password
GITHUB_ORG = "your_github_organization"  # GitHub organization name
GITHUB_REPO = "your_github_repo"  # GitHub repository name on GitHub
GITHUB_TOKEN = "your_github_token"

# Bitbucket API endpoint to get PRs
BITBUCKET_API_URL = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}/{BITBUCKET_REPO}/pullrequests"

# GitHub API endpoint to create PRs
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_ORG}/{GITHUB_REPO}/pulls"

# Headers for GitHub authentication
github_headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# Function to get PRs from Bitbucket Cloud
def get_bitbucket_prs():
    prs = []
    url = BITBUCKET_API_URL
    while url:
        response = requests.get(url, auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))
        if response.status_code != 200:
            print(f"Failed to fetch PRs from Bitbucket: {response.status_code}, {response.text}")
            break
        data = response.json()
        prs.extend(data.get("values", []))
        url = data.get("next")  # Pagination support
    return prs

# Function to create a PR on GitHub
def create_github_pr(pr):
    title = pr["title"]
    body = pr.get("description", "")
    state = pr["state"]
    source_branch = pr["source"]["branch"]["name"]
    destination_branch = pr["destination"]["branch"]["name"]

    pr_payload = {
        "title": title,
        "body": body,
        "head": source_branch,  # GitHub head branch (source)
        "base": destination_branch  # GitHub base branch (destination)
    }

    print(f"Creating PR on GitHub: {title}")
    response = requests.post(GITHUB_API_URL, headers=github_headers, json=pr_payload)

    if response.status_code == 201:
        print(f"Successfully created PR '{title}' on GitHub.")
    else:
        print(f"Failed to create PR on GitHub: {response.status_code}, {response.text}")

    # Handle PR state on GitHub
    if state == "MERGED":
        print(f"Marking PR '{title}' as merged (not directly supported by GitHub API).")

# Main function to migrate PRs
def migrate_prs():
    print("Fetching PRs from Bitbucket Cloud...")
    bitbucket_prs = get_bitbucket_prs()

    for pr in bitbucket_prs:
        create_github_pr(pr)

    print("Migration of PRs complete.")

# Run the migration
migrate_prs()
