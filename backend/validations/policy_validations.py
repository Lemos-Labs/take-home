def validate_policy(policy):
    block_validation = check_block_amount(policy)
    if  block_validation is not None:
        return block_validation

    return None

def check_block_amount(policy):
    """
    Validates that a policy has exactly one Start block, at least
    one Conditional block, and ensures Conditional blocks have valid true/false branches.
    """
    start_blocks = 0
    conditional_blocks = 0

    # Collect all block IDs to verify branch references later
    block_ids = set()
    conditional_branches = []

    for block in policy.get("blocks", []):
        block_type = block.get("block_type")
        block_id = block.get("block_id")

        if not block_id:
            return "Each block must have a unique 'block_id'."

        block_ids.add(block_id)

        if block_type == "StartBlock":
            start_blocks += 1
        elif block_type == "ConditionalBlock":
            conditional_blocks += 1

            true_branch = block.get("true_branch")
            false_branch = block.get("false_branch")

            if not true_branch or not false_branch:
                return f"ConditionalBlock '{block_id}' must have both 'true_branch' and 'false_branch'."
            
            conditional_branches.append((block_id, true_branch, false_branch))

    # Check if the start block count is correct
    if start_blocks != 1:
        return "Policy must have exactly one Start block."

    # Check if there is at least one conditional block
    if conditional_blocks < 1:
        return "Policy must have at least one Conditional block."

    # Validate that all branches in conditional blocks point to valid block IDs
    for block_id, true_branch, false_branch in conditional_branches:
        if true_branch not in block_ids:
            return f"ConditionalBlock '{block_id}' has an invalid 'true_branch' reference: '{true_branch}' does not exist."
        if false_branch not in block_ids:
            return f"ConditionalBlock '{block_id}' has an invalid 'false_branch' reference: '{false_branch}' does not exist."

    return None  # Policy is valid

def check_passed_variables(policy, args):
    """
    Checks if the provided variables in query parameters 
    match the expected policy variables.
    """
    variables = policy.get("variables", [])

    for var in variables:
        if var not in args:
            return f"Expected variable '{var}' in query parameters but variable was not found."  # ✅ Fixed: No comma

    for arg in args:
        if arg not in variables:
            return f"Unexpected variable '{arg}' in query parameters."

    return None
