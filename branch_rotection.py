def extract_bitbucket_branch_names(response):
    branch_names = []
    
    # Ensure that 'values' is a list of dictionaries
    if isinstance(response, dict) and 'values' in response:
        for restriction in response['values']:
            # Ensure that each restriction is a dictionary
            if isinstance(restriction, dict):
                branch_type = restriction.get('branch_type', None)
                # If branch_type is found, add it to the list (avoid duplicates)
                if branch_type and branch_type not in branch_names:
                    branch_names.append(branch_type)
    
    return branch_names
