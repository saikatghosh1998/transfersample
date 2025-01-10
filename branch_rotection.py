import requests

# Configuration
BITBUCKET_SERVER_URL = "https://bitbucket.example.com"
BITBUCKET_TOKEN = "your-bitbucket-token"
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = "your-github-token"

# Mapping between Bitbucket and GitHub repositories
REPO_MAPPING = {
    "bitbucket-project/repo1": "github-org/repo1",
    "bitbucket-project/repo2": "github-org/repo2",
}

# Headers for API requests
bitbucket_headers = {"Authorization": f"Bearer {BITBUCKET_TOKEN}"}
github_headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

def get_bitbucket_branch_permissions(project, repo):
    url = f"{BITBUCKET_SERVER_URL}/rest/branch-permissions/latest/projects/{project}/repos/{repo}/restrictions"
    response = requests.get(url, headers=bitbucket_headers)
    response.raise_for_status()
    return response.json()

def create_github_branch_protection(owner, repo, branch, rules):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/branches/{branch}/protection"
    response = requests.put(url, headers=github_headers, json=rules)
    response.raise_for_status()

def migrate_branch_rules():
    for bitbucket_repo, github_repo in REPO_MAPPING.items():
        bitbucket_project, bitbucket_repo_name = bitbucket_repo.split("/")
        github_org, github_repo_name = github_repo.split("/")
        
        print(f"Migrating branch rules from {bitbucket_repo} to {github_repo}...")

        # Fetch branch permissions from Bitbucket
        permissions = get_bitbucket_branch_permissions(bitbucket_project, bitbucket_repo_name)
        
        for permission in permissions:
            branch = permission.get("matcher", {}).get("displayId")
            if not branch:
                continue

            # Transform Bitbucket rules to GitHub rules
            github_rules = {
                "required_status_checks": {
                    "strict": True,
                    "contexts": [],  # Add required status checks if any
                },
                "enforce_admins": True,
                "required_pull_request_reviews": {
                    "dismiss_stale_reviews": True,
                    "require_code_owner_reviews": permission.get("type") == "pull-request-only",
                },
                "restrictions": {
                    "users": [],  # Add specific users if applicable
                    "teams": [],  # Add specific teams if applicable
                },
                "required_linear_history": False,
                "allow_force_pushes": permission.get("type") == "fast-forward-only",
                "allow_deletions": False,
            }

            # Apply rules to GitHub
            try:
                create_github_branch_protection(
                    github_org, github_repo_name, branch, github_rules
                )
                print(f"  Migrated branch: {branch}")
            except requests.exceptions.RequestException as e:
                print(f"  Failed to migrate branch {branch}: {e}")

if __name__ == "__main__":
    migrate_branch_rules()
