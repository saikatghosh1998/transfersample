def fetch_bitbucket_branch_rules(workspace, repo_name):
    branch_permission = []
    url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}/{repo_name}/branch-restrictions"
    while url:
            logger.info("Fetching Branch protection rules ...")
            #response = requests.get(url, auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                branch_permission.extend(data.get("values",[]))
                # print(url)
                # print(data.get("next"))
                url = data.get("next")
             
            else:
                break
    print("return")
    return branch_permission
    # response = requests.get(BITBUCKET_API_URL, auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))
    # if response.status_code == 200:
    #     return response.json().get("values", [])
    # else:
    #     print(f"Error")
    #     return []



def map_to_github_branch_rules(bitbucket_rules):
    github_rules = {
        "required_status_checks": {
            "strict": True,
            "contexts":[]
        },
        "enforce_admins":True,
        "required_pull_request_reviews":{
            "dismiss_stale_reviews": False,
            "require_code_owner_reviews": False,
            "required_approving_review_count": 3
        },
        "restrictions":None,
        "allow_force_pushes": False,
        "allow_deletions":False,
        "require_signed_commits":False
    }
    #Map specific Bitbucket rules
    for rule in bitbucket_rules:
        #print(f"{rule.get('kind')}-{rule.get('value')}")
        if rule.get("kind") == "require_approvals_to_merge":
            github_rules["required_pull_request_reviews"]["required_approving_review_count"] = rule.get("value", 1)
        if rule.get("kind") == "force_push":
            github_rules["allow_force_pushes"] = False
    

        # if "type" in rule and rule["type"] == "PullRequestApproval":
        #     github_rules["required_pull_requests_reviews"]["required_approving_review_count"] = rule.get("value",1)

        # if "type" in rule and rule["type"] == "FastForwardOnly":
        #     github_rules["allow_force_pushes"] = False
        
    return github_rules
    
def apply_github_branch_rules(github_repo, branch, rules):
    url = f"{GITHUB_BASE_URL}/repos/{GITHUB_ORG}/{github_repo}/branches/{branch}/protection"
    #response = requests.put(url,headers=headers,json=rules)
    response = requests.put(url,auth=(GITHUB_USERNAME, GITHUB_TOKEN), headers={'Accept': 'application/vnd.github.v3+json'}, json=rules)


    if response.status_code == 200:
        logger.info("successfully applied rules")
        updat_checkpoint(github_repo, "branch_protection", "completed")
        #print("successfully applied rules")
    else:
        logger.error(f"error: {response.status_code} - {response.text}")
        #print(f"error: {response.status_code} - {response.text}")

def migrate_branch_protection_rules(project_key, repo_name, github_org, github_repo, branch):
    bitbucket_rules = fetch_bitbucket_branch_rules(project_key, repo_name)
    if not bitbucket_rules:
        logger.info("no brnch protection rules")
        #print("no brnch protection rules")
        return
    github_rules = map_to_github_branch_rules(bitbucket_rules)
    apply_github_branch_rules(github_repo,branch,github_rules)

def main(repo_name):
    updat_checkpoint(repo_name, "branch_protection", "started")
    
    migrate_branch_protection_rules(
        BITBUCKET_WORKSPACE,
        repo_name,
        GITHUB_ORG,
        repo_name,
        "master"
        )


if __name__ == "__main__":
    main("ts")
