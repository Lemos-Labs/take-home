def execute_policy(policy_json, args):
    """
    Executes a stored policy using user-provided variables.
    Traverses through blocks based on conditions until reaching an EndBlock.
    """
    blocks = {block["block_id"]: block for block in policy_json["blocks"]}

    # Convert input variables into the correct format
    variables = {var_name: parse_value(value) for var_name, value in args.items()}
    
    start_block = next(
        (block for block in blocks.values() if block["block_type"] == "StartBlock"), None
    )

    if not start_block:
        raise ValueError("Policy is missing a StartBlock.")

    current_block = start_block

    while current_block["block_type"] != "EndBlock":
        if current_block["block_type"] == "StartBlock":
            current_block = blocks[current_block["next_block"]]
        elif current_block["block_type"] == "ConditionalBlock":
            var_name = current_block["variable"]
            operator = current_block["operator"]
            compare_value = current_block["cmp_value"]

            # Evaluate the condition with the provided variables
            if evaluate_condition(variables[var_name], operator, parse_value(compare_value)):
                next_block_id = current_block["true_branch"]
            else:
                next_block_id = current_block["false_branch"]

            current_block = blocks[next_block_id]
        else:
            raise ValueError(f"Unexpected block type: {current_block['block_type']}")

    return current_block["decision_value"]

def parse_value(val):
    """Attempts to parse numeric values, otherwise returns the original string."""
    try:
        return float(val) if "." in str(val) or str(val).isdigit() else int(val)
    except ValueError:
        return val
    
def evaluate_condition(var, operator, cmp):
    match operator:
        case "=":
            return var == cmp
        case "!=":
            return var != cmp
        case ">":
            return var > cmp
        case "<":
            return var < cmp
        case ">=":
            return var >= cmp
        case "<=":
            return var <= cmp
        case _:
            raise ValueError(f"Unsupported operator: {operator}")
        