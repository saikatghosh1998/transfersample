import requests
import json
import os

# Environment variables for sensitive information
BITBUCKET_USERNAME = os.getenv('BITBUCKET_USERNAME')
BITBUCKET_APP_PASSWORD = os.getenv('BITBUCKET_APP_PASSWORD')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GITHUB_PAT = os.getenv('GITHUB_PAT')
GITHUB_ORG = os.getenv('GITHUB_ORG')
GITHUB_REPO = os.getenv('GITHUB_REPO')

# Bitbucket API endpoint to get pull requests
bitbucket_pr_url = f"https://dev.code.saikat.com/rest/api/1.0/projects/asx/repos/{GITHUB_REPO}/pull-requests"

# Fetch pull requests from Bitbucket
response = requests.get(
    bitbucket_pr_url,
    auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD),
    headers={'Accept': 'application/json'}
)

# Check for successful response
if response.status_code != 200:
    print(f"Failed to fetch Bitbucket PRs: {response.status_code} - {response.text}")
    exit()

bitbucket_prs = response.json().get('values', [])

# Loop over each PR and extract data
for pr in bitbucket_prs:
    pr_id = pr['id']
    pr_title = pr['title']
    pr_body = pr['description']
    pr_branch = pr['fromRef']['displayId']
    pr_base_branch = pr['toRef']['displayId']

    print(f"Creating PR: {pr_title} from {pr_branch} to {pr_base_branch}: PR ID is: {pr_id}")

    # Create the PR on GitHub
    json_payload = {
        "title": pr_title,
        "body": pr_body,
        "head": pr_branch,
        "base": pr_base_branch
    }

    github_pr_url = f"https://api.github.com/repos/{GITHUB_ORG}/{GITHUB_REPO}/pulls"
    github_response = requests.post(
        github_pr_url,
        json=json_payload,
        auth=(GITHUB_USERNAME, GITHUB_PAT),
        headers={'Accept': 'application/vnd.github.v3+json'}
    )

    if github_response.status_code != 201:
        print(f"Failed to create PR on GitHub: {github_response.status_code} - {github_response.text}")
        continue

    github_pr_number = github_response.json().get('number')
    print(f"GitHub PR created with number: {github_pr_number}")

    # Fetch comments from Bitbucket using the PR_ID
    bitbucket_comments_url = f"https://dev.code.saikat.com/rest/api/latest/projects/asx/repos/{GITHUB_REPO}/pull-requests/{pr_id}/activities"
    print(f"Fetching comments from: {bitbucket_comments_url}")

    activities_response = requests.get(
        bitbucket_comments_url,
        auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD),
        headers={'Accept': 'application/json'}
    )

    if activities_response.status_code != 200:
        print(f"Failed to fetch comments: {activities_response.status_code} - {activities_response.text}")
        continue

    comments = activities_response.json().get('values', [])
    
    # Extract and push comments to GitHub
    for activity in comments:
        comment = activity['comment']['text']
        author = activity['comment']['author']['name']
        comment_payload = {
            "body": f"Comment by {author}: {comment}"
        }

        github_comment_url = f"https://api.github.com/repos/{GITHUB_ORG}/{GITHUB_REPO}/issues/{github_pr_number}/comments"
        comment_response = requests.post(
            github_comment_url,
            json=comment_payload,
            auth=(GITHUB_USERNAME, GITHUB_PAT),
            headers={'Accept': 'application/vnd.github.v3+json'}
        )

        if comment_response.status_code != 201:
            print(f"Failed to add comment on GitHub: {comment_response.status_code} - {comment_response.text}")
        else:
            print(f"Comment added on GitHub for PR {github_pr_number}: {comment_payload['body']}")
