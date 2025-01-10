import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BITBUCKET_SERVER_URL = "https://bitbucket.example.com"
BITBUCKET_USERNAME = "your-bitbucket-username"
BITBUCKET_APP_PASSWORD = "your-bitbucket-app-password"  # Or use an API token
GITHUB_BASE_URL = "https://api.github.com"
GITHUB_USERNAME = "your-github-username"
GITHUB_TOKEN = "your-github-token"
BITBUCKET_WORKSPACE = "your-bitbucket-workspace"
GITHUB_ORG = "your-github-org"

def fetch_bitbucket_branch_rules(workspace, repo_name):
    branch_permission = []
    url = f"{BITBUCKET_SERVER_URL}/rest/branch-permissions/latest/projects/{workspace}/repos/{repo_name}/restrictions"
    
    while url:
        logger.info("Fetching branch protection rules from Bitbucket...")
        response = requests.get(url, auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))
        if response.status_code == 200:
            data = response.json()
            branch_permission.extend(data.get("values", []))
            url = data.get("next")  # Paginated API support
        else:
            logger.error(f"Failed to fetch branch rules: {response.status_code} - {response.text}")
            break
    
    return branch_permission

def map_to_github_branch_rules(bitbucket_rules):
    github_rules = {
        "required_status_checks": {
            "strict": True,
            "contexts": []  # Add required status checks if needed
        },
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": False,
            "require_code_owner_reviews": False,
            "required_approving_review_count": 1
        },
        "restrictions": None,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "require_signed_commits": False
    }

    # Map specific Bitbucket rules
    for rule in bitbucket_rules:
        if rule.get("type") == "PullRequestApproval":
            github_rules["required_pull_request_reviews"]["required_approving_review_count"] = rule.get("value", 1)
        if rule.get("type") == "FastForwardOnly":
            github_rules["allow_force_pushes"] = False
    
    return github_rules

def apply_github_branch_rules(github_repo, branch, rules):
    url = f"{GITHUB_BASE_URL}/repos/{GITHUB_ORG}/{github_repo}/branches/{branch}/protection"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.put(url, headers=headers, json=rules)

    if response.status_code in (200, 201):
        logger.info("Successfully applied branch protection rules.")
    else:
        logger.error(f"Failed to apply branch rules: {response.status_code} - {response.text}")

def migrate_branch_protection_rules(workspace, repo_name, github_org, github_repo, branch):
    bitbucket_rules = fetch_bitbucket_branch_rules(workspace, repo_name)
    if not bitbucket_rules:
        logger.info("No branch protection rules found.")
        return

    github_rules = map_to_github_branch_rules(bitbucket_rules)
    apply_github_branch_rules(github_repo, branch, github_rules)

def main(repo_name):
    logger.info(f"Starting branch protection rules migration for {repo_name}...")
    migrate_branch_protection_rules(
        BITBUCKET_WORKSPACE,
        repo_name,
        GITHUB_ORG,
        repo_name,  # Assuming the same repo name in GitHub
        "master"  # Default branch, update as needed
    )

if __name__ == "__main__":
    main("your-repo-name")
