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
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

# Fetch merged PRs from Bitbucket
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

# Create a closed PR in GitHub
def create_closed_pr(repo_id, base_ref_name, title, body):
    query = """
    mutation($repoId: ID!, $baseRefName: String!, $title: String!, $body: String!) {
        createPullRequest(input: {
            repositoryId: $repoId,
            baseRefName: $baseRefName,
            headRefName: "nonexistent-branch",
            title: $title,
            body: $body,
            state: CLOSED
        }) {
            pullRequest {
                id
                title
                state
            }
        }
    }
    """
    variables = {
        "repoId": repo_id,
        "baseRefName": base_ref_name,
        "title": title,
        "body": body
    }

    response = requests.post(GITHUB_GRAPHQL_URL, json={"query": query, "variables": variables}, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to create PR: {response.status_code}, {response.text}")
        return None

# Add a comment to the PR
def add_comment(pr_id, comment_body):
    query = """
    mutation($prId: ID!, $body: String!) {
        addComment(input: {subjectId: $prId, body: $body}) {
            commentEdge {
                node {
                    body
                    createdAt
                }
            }
        }
    }
    """
    variables = {
        "prId": pr_id,
        "body": comment_body
    }

    response = requests.post(GITHUB_GRAPHQL_URL, json={"query": query, "variables": variables}, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to add comment: {response.status_code}, {response.text}")
        return None

# Main Migration Logic
def migrate_prs_to_github():
    # Fetch merged PRs from Bitbucket
    prs = fetch_bitbucket_prs(state="MERGED")
    print(f"Fetched {len(prs)} merged PRs from Bitbucket.")

    # Get GitHub repository ID
    repo_query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            id
        }
    }
    """
    variables = {"owner": GITHUB_ORG, "name": GITHUB_REPO}
    response = requests.post(GITHUB_GRAPHQL_URL, json={"query": repo_query, "variables": variables}, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch GitHub repository ID: {response.status_code}, {response.text}")
        return
    repo_id = response.json()["data"]["repository"]["id"]

    # Migrate each PR
    for pr in prs:
        title = pr["title"]
        body = pr.get("description", "")
        base_ref = pr["destination"]["branch"]["name"]
        author = pr["author"]["display_name"]
        created_on = pr["created_on"]

        # Create a closed PR in GitHub
        pr_response = create_closed_pr(repo_id, base_ref, title, body)
        if pr_response:
            pr_id = pr_response["data"]["createPullRequest"]["pullRequest"]["id"]
            print(f"Created PR '{title}' as closed in GitHub.")

            # Add a comment indicating the author and creation date
            comment_body = f"This PR was created by {author} on {created_on} and was merged in Bitbucket."
            add_comment(pr_id, comment_body)

if __name__ == "__main__":
    migrate_prs_to_github()
