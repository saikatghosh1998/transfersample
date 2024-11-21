import requests

# Configuration
BITBUCKET_WORKSPACE = "your_bitbucket_workspace"
BITBUCKET_REPO_SLUG = "your_bitbucket_repo_slug"
BITBUCKET_USERNAME = "your_bitbucket_username"
BITBUCKET_APP_PASSWORD = "your_bitbucket_app_password"

GITHUB_ORG = "your_github_org"
GITHUB_REPO = "your_github_repo"
GITHUB_TOKEN = "your_github_token"

BITBUCKET_API_URL = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}/{BITBUCKET_REPO_SLUG}/pullrequests"
GITHUB_ISSUES_URL = f"https://api.github.com/repos/{GITHUB_ORG}/{GITHUB_REPO}/issues"
GITHUB_COMMENTS_URL = f"https://api.github.com/repos/{GITHUB_ORG}/{GITHUB_REPO}/issues/{{}}/comments"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

# Fetch PRs from Bitbucket
def fetch_bitbucket_prs(state="MERGED"):
    pr_list = []
    next_url = BITBUCKET_API_URL + f"?state={state}"
    
    while next_url:
        response = requests.get(next_url, auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))
        if response.status_code == 200:
            data = response.json()
            pr_list.extend(data.get("values", []))
            next_url = data.get("next")  # Pagination
        else:
            print(f"Failed to fetch PRs from Bitbucket: {response.status_code}, {response.text}")
            break
    return pr_list

# Fetch PR comments from Bitbucket
def fetch_pr_comments(pr_id):
    comments_url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}/{BITBUCKET_REPO_SLUG}/pullrequests/{pr_id}/comments"
    comments = []
    next_url = comments_url

    while next_url:
        response = requests.get(next_url, auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))
        if response.status_code == 200:
            data = response.json()
            comments.extend(data.get("values", []))
            next_url = data.get("next")  # Pagination
        else:
            print(f"Failed to fetch comments for PR {pr_id}: {response.status_code}, {response.text}")
            break
    return comments

# Create a GitHub issue to simulate a PR
def create_github_issue(title, body, labels):
    payload = {
        "title": title,
        "body": body,
        "labels": labels,
    }
    response = requests.post(GITHUB_ISSUES_URL, json=payload, headers=HEADERS)
    if response.status_code == 201:
        issue_number = response.json()["number"]
        print(f"Created issue for PR: {title}")
        return issue_number
    else:
        print(f"Failed to create issue: {response.status_code}, {response.text}")
        return None

# Post comments to the GitHub issue
def post_github_comments(issue_number, comments):
    for comment in comments:
        comment_body = f"**{comment['user']['display_name']}** on {comment['created_on']}:\n{comment['content']['raw']}"
        payload = {
            "body": comment_body
        }
        response = requests.post(GITHUB_COMMENTS_URL.format(issue_number), json=payload, headers=HEADERS)
        if response.status_code == 201:
            print(f"Comment posted on GitHub issue: {issue_number}")
        else:
            print(f"Failed to post comment: {response.status_code}, {response.text}")

# Migrate PRs as issues
def migrate_prs_to_github():
    # Fetch merged PRs
    merged_prs = fetch_bitbucket_prs(state="MERGED")
    print(f"Fetched {len(merged_prs)} merged PRs.")

    for pr in merged_prs:
        title = f"[Migrated PR] {pr['title']}"
        author = pr["author"]["display_name"]
        created_on = pr["created_on"]
        body = pr.get("description", "No description provided.")
        destination_branch = pr["destination"]["branch"]["name"]
        source_branch = pr["source"]["branch"]["name"]

        # Fetch comments for the PR
        comments = fetch_pr_comments(pr["id"])
        comments_text = "\n\n".join(
            [
                f"**{comment['user']['display_name']}** on {comment['created_on']}:\n{comment['content']['raw']}"
                for comment in comments
            ]
        )

        # Add PR metadata and comments to the issue body
        issue_body = (
            f"**Author:** {author}\n"
            f"**Created On:** {created_on}\n"
            f"**Source Branch:** {source_branch}\n"
            f"**Destination Branch:** {destination_branch}\n\n"
            f"{body}\n\n"
            f"**Comments:**\n{comments_text}"
        )

        # Use labels to differentiate migrated PRs
        issue_number = create_github_issue(title, issue_body, labels=["migrated-PR", "merged-PR"])

        if issue_number:
            # Post comments to GitHub issue
            post_github_comments(issue_number, comments)

if __name__ == "__main__":
    migrate_prs_to_github()
