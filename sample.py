import requests
import time

# Configuration variables
BITBUCKET_WORKSPACE = "your_workspace"
BITBUCKET_REPO = "your_bitbucket_repo"
BITBUCKET_USERNAME = "your_bitbucket_username"
BITBUCKET_APP_PASSWORD = "your_bitbucket_app_password"
GITHUB_ORG = "your_github_organization"
GITHUB_REPO = "your_github_repo"
GITHUB_TOKEN = "your_github_token"

# Bitbucket API endpoints
BITBUCKET_API_PR_URL = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}/{BITBUCKET_REPO}/pullrequests"
GITHUB_API_PR_URL = f"https://api.github.com/repos/{GITHUB_ORG}/{GITHUB_REPO}/pulls"
GITHUB_HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# Function to get PRs from Bitbucket Cloud
def get_bitbucket_prs():
    prs = []
    url = BITBUCKET_API_PR_URL
    while url:
        response = requests.get(url, auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))
        if response.status_code != 200:
            print(f"Failed to fetch PRs from Bitbucket: {response.status_code}, {response.text}")
            break
        data = response.json()
        prs.extend(data.get("values", []))
        url = data.get("next")  # Pagination support
    return prs

# Function to create a PR on GitHub with error handling and retry limit
def create_github_pr(pr, retries=5):
    title = pr["title"]
    body = pr.get("description", "")
    source_branch = pr["source"]["branch"]["name"]
    destination_branch = pr["destination"]["branch"]["name"]

    # PR payload
    pr_payload = {
        "title": title,
        "body": body,
        "head": source_branch,
        "base": destination_branch
    }

    print(f"Creating PR on GitHub: {title}")
    response = requests.post(GITHUB_API_PR_URL, headers=GITHUB_HEADERS, json=pr_payload)

    if response.status_code == 201:
        github_pr = response.json()
        print(f"Successfully created PR '{title}' on GitHub.")
        migrate_pr_comments(pr["id"], github_pr["number"])
    elif response.status_code == 422:
        print(f"PR '{title}' already exists on GitHub. Skipping.")
    elif response.status_code == 403 and "secondary rate limit" in response.text:
        if retries > 0:
            print(f"Rate limit exceeded. Retrying after delay... ({retries} retries left)")
            time.sleep(10)  # Adding delay if rate limited
            create_github_pr(pr, retries - 1)  # Retry with decremented retry count
        else:
            print("Max retries reached. Skipping PR creation for:", title)
    else:
        print(f"Failed to create PR on GitHub: {response.status_code}, {response.text}")

# Function to get comments from a Bitbucket PR and post them to the corresponding GitHub PR
def migrate_pr_comments(bitbucket_pr_id, github_pr_number):
    comments_url = f"{BITBUCKET_API_PR_URL}/{bitbucket_pr_id}/comments"
    while comments_url:
        response = requests.get(comments_url, auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))
        if response.status_code != 200:
            print(f"Failed to fetch comments for Bitbucket PR {bitbucket_pr_id}: {response.status_code}, {response.text}")
            break
        comments_data = response.json()
        for comment in comments_data.get("values", []):
            comment_text = comment["content"]["raw"]
            comment_author = comment["user"]["display_name"]
            comment_time = comment["created_on"]
            
            # Add timestamp and author info to the comment
            formatted_comment = f"**Comment by {comment_author} on {comment_time}**\n\n{comment_text}"
            
            # Post comment to GitHub PR
            github_comment_url = f"https://api.github.com/repos/{GITHUB_ORG}/{GITHUB_REPO}/issues/{github_pr_number}/comments"
            response = requests.post(github_comment_url, headers=GITHUB_HEADERS, json={"body": formatted_comment})
            
            if response.status_code == 201:
                print(f"Successfully migrated comment from Bitbucket PR {bitbucket_pr_id} to GitHub PR {github_pr_number}")
            else:
                print(f"Failed to migrate comment: {response.status_code}, {response.text}")
        
        # Pagination for comments
        comments_url = comments_data.get("next")

# Main function to migrate PRs
def migrate_prs():
    print("Fetching PRs from Bitbucket Cloud...")
    bitbucket_prs = get_bitbucket_prs()

    for pr in bitbucket_prs:
        create_github_pr(pr)

    print("Migration of PRs and comments complete.")

# Run the migration
migrate_prs()
