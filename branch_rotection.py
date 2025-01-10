def extract_bitbucket_branch_names(response):
    branch_names = []
    
    # Iterate through the 'values' list in the response
    for restriction in response.get('values', []):
        branch_type = restriction.get('branch_type', None)
        
        # If branch_type is found, add it to the list
        if branch_type and branch_type not in branch_names:
            branch_names.append(branch_type)
    
    return branch_names
