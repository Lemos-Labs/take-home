def validate_policy(policy):
    block_validation = check_block_amount(policy)
    if  block_validation is not None:
        return block_validation

    return None

def check_block_amount(policy):
    """
    Validates that a poilicy has exactly one Start block and at least
    one Conditional block, otherwise, the policy will not be issued.
    """
    start_blocks = 0
    conditional_blocks = 0

    for block in policy.get("blocks", []):
        block_type = block.get("block_type")

        if block_type == "StartBlock":
            start_blocks += 1
        elif block_type == "ConditionalBlock":
            conditional_blocks += 1

    if start_blocks != 1:
        return "Policy must have exactly one Start block."

    if conditional_blocks < 1:
        return "Policy must have at least one Conditional block."

    return None     # Policy is valid

def check_passed_variables(policy, args):
    """
    Checks if the provided variables in query parameters 
    match the expected policy variables.
    """
    variables = policy.get("variables", [])

    for var in variables:
        if var not in args:
            return f"Expected variable '{var}' in query parameters but variable was not found.",

    for arg in args:
        if arg not in variables:
            return f"Unexpected variable '{arg}' in query parameters."

    return None
