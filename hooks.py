import requests
from requests.auth import HTTPBasicAuth

# Bitbucket Server details
BITBUCKET_URL = "https://bitbucket.example.com"  # Replace with your Bitbucket base URL
BITBUCKET_USERNAME = "bitbucket_username"  # Replace with your Bitbucket username
BITBUCKET_PASSWORD = "bitbucket_password"  # Replace with your Bitbucket password or token
BITBUCKET_PROJECT = "PROJECT_KEY"  # Replace with your project key
BITBUCKET_REPO = "REPO_SLUG"  # Replace with your repository slug

# GitHub details
GITHUB_URL = "https://api.github.com"
GITHUB_TOKEN = "github_personal_access_token"  # Replace with your GitHub token
GITHUB_OWNER = "github_owner"  # Replace with your GitHub organization/user
GITHUB_REPO = "github_repo"  # Replace with your GitHub repository

# Bitbucket API endpoint to fetch webhooks
BITBUCKET_WEBHOOKS_API = f"{BITBUCKET_URL}/rest/api/1.0/projects/{BITBUCKET_PROJECT}/repos/{BITBUCKET_REPO}/webhooks"

# GitHub API endpoint to create webhooks
GITHUB_WEBHOOKS_API = f"{GITHUB_URL}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/hooks"

# Event mapping between Bitbucket and GitHub
EVENT_MAPPING = {
    "repo:push": "push",
    "pullrequest:created": "pull_request",
    "pullrequest:updated": "pull_request",
    "pullrequest:fulfilled": "pull_request",
    "pullrequest:rejected": "pull_request",
    "issue:created": "issues",
    "issue:updated": "issues",
    "issue:comment_created": "issue_comment",
    "fork": "fork",
    "repo:updated": "repository",
}


def map_events(bitbucket_events):
    """Map Bitbucket events to GitHub events."""
    github_events = set()
    for event in bitbucket_events:
        if event in EVENT_MAPPING:
            github_events.add(EVENT_MAPPING[event])
        else:
            print(f"Warning: No mapping for Bitbucket event '{event}'")
    return list(github_events)


def get_bitbucket_webhooks():
    """Fetch all webhooks from the Bitbucket repository."""
    response = requests.get(
        BITBUCKET_WEBHOOKS_API,
        auth=HTTPBasicAuth(BITBUCKET_USERNAME, BITBUCKET_PASSWORD),
    )
    if response.status_code == 200:
        return response.json().get("values", [])
    else:
        print(f"Failed to fetch webhooks from Bitbucket. Status: {response.status_code}, Response: {response.text}")
        return []


def create_github_webhook(hook):
    """Create a webhook in the GitHub repository."""
    github_events = map_events(hook.get("events", []))
    if not github_events:
        print(f"Skipping webhook '{hook['url']}' as no valid GitHub events are mapped.")
        return

    payload = {
        "name": "web",
        "active": hook.get("enabled", True),
        "events": github_events,
        "config": {
            "url": hook["url"],
            "content_type": "json",
            "insecure_ssl": "1" if not hook.get("secure", True) else "0",
        },
    }

    response = requests.post(
        GITHUB_WEBHOOKS_API,
        headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        },
        json=payload,
    )

    if response.status_code == 201:
        print(f"Webhook migrated successfully: {hook['url']}")
    else:
        print(f"Failed to create webhook in GitHub. Status: {response.status_code}, Response: {response.text}")


def migrate_webhooks():
    """Migrate webhooks from Bitbucket Server to GitHub."""
    bitbucket_hooks = get_bitbucket_webhooks()
    print(f"Found {len(bitbucket_hooks)} webhooks in Bitbucket.")

    for hook in bitbucket_hooks:
        create_github_webhook(hook)


if __name__ == "__main__":
    migrate_webhooks()
