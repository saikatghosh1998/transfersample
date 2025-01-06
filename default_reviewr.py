import requests
from requests.auth import HTTPBasicAuth

# Bitbucket Server details
BITBUCKET_URL = "https://bitbucket.example.com"  # Replace with your Bitbucket base URL
PROJECT_KEY = "PROJECT_KEY"  # Replace with your project key
REPO_SLUG = "REPO_SLUG"      # Replace with your repository slug
USERNAME = "bitbucket_username"  # Replace with your Bitbucket username
PASSWORD = "bitbucket_password"  # Replace with your Bitbucket password or token

# API endpoint to get default reviewers
API_URL = f"{BITBUCKET_URL}/rest/default-reviewers/1.0/projects/{PROJECT_KEY}/repos/{REPO_SLUG}/conditions"


def get_default_reviewers():
    """Fetch default reviewers from the Bitbucket Server repository."""
    try:
        response = requests.get(
            API_URL,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
        )

        # Check if the response is successful
        if response.status_code == 200:
            conditions = response.json().get("values", [])
            print(f"Found {len(conditions)} default reviewer conditions.")
            
            for condition in conditions:
                print("\nCondition:")
                print(f"- Source Branch: {condition.get('sourceMatcher', {}).get('id', 'Any')}")
                print(f"- Target Branch: {condition.get('targetMatcher', {}).get('id', 'Any')}")
                
                reviewers = condition.get("reviewers", [])
                reviewer_names = [reviewer["user"]["displayName"] for reviewer in reviewers]
                print(f"- Default Reviewers: {', '.join(reviewer_names) if reviewer_names else 'None'}")
        else:
            print(f"Failed to fetch default reviewers. Status Code: {response.status_code}, Response: {response.text}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    get_default_reviewers()
