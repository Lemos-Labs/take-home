import pytest
from validations.policy_validations import validate_policy, check_passed_variables

# ==================================
# Test cases for `validate_policy`
# ==================================

def test_validate_policy_valid():
    """ Test policy with correct block structure """
    policy = {
        "blocks": [
            {"block_type": "StartBlock", "block_id": "1", "next_block": "2"},
            {
                "block_type": "ConditionalBlock",
                "block_id": "2",
                "variable": "age",
                "cmp_value": "18",
                "operator": ">=",
                "true_branch": "3",
                "false_branch": "4"
            },
            {"block_type": "EndBlock", "block_id": "3", "decision_value": "Approved"},
            {"block_type": "EndBlock", "block_id": "4", "decision_value": "Denied"},
        ]
    }
    assert validate_policy(policy) is None

def test_validate_policy_missing_start():
    """ Test policy with no StartBlock """
    policy = {
        "blocks": [
            {"block_type": "ConditionalBlock",
             "block_id": "2",
             "variable": "age",
             "cmp_value": "18",
             "operator": ">=",
             "true_branch": "3",
             "false_branch": "4"
            },
            {"block_type": "EndBlock", "block_id": "3", "decision_value": "Approved"},
            {"block_type": "EndBlock", "block_id": "4", "decision_value": "Denied"},
        ]
    }
    assert validate_policy(policy) == "Policy must have exactly one Start block."

def test_validate_policy_missing_conditional():
    """ Test policy with no ConditionalBlock """
    policy = {
        "blocks": [
            {"block_id": "1", "block_type": "StartBlock", "next_block": "3"},
            {"block_id": "3", "block_type": "EndBlock", "decision_value": "Approved"},
        ]
    }
    assert validate_policy(policy) == "Policy must have at least one Conditional block."

def test_validate_policy_missing_block_id():
    """ Test policy where a block is missing a block_id """
    policy = {
        "blocks": [
            {"block_type": "StartBlock", "next_block": "2"},
            {
                "block_id": "2",
                "block_type": "ConditionalBlock",
                "variable": "age",
                "cmp_value": "18",
                "operator": ">=",
                "true_branch": "3",
                "false_branch": "4"
            },
            {"block_id": "3", "block_type": "EndBlock", "decision_value": "Approved"},
            {"block_id": "4", "block_type": "EndBlock", "decision_value": "Denied"},
        ]
    }
    assert validate_policy(policy) == "Each block must have a unique 'block_id'."

def test_validate_policy_conditional_missing_branch():
    """ Test policy where a ConditionalBlock is missing true_branch or false_branch """
    policy = {
        "blocks": [
            {"block_id": "1", "block_type": "StartBlock", "next_block": "2"},
            {
                "block_id": "2",
                "block_type": "ConditionalBlock",
                "variable": "age",
                "cmp_value": "18",
                "operator": ">=",
                "true_branch": "3"
            },
            {"block_id": "3", "block_type": "EndBlock", "decision_value": "Approved"},
        ]
    }
    assert validate_policy(policy) == "ConditionalBlock '2' must have both 'true_branch' and 'false_branch'."

def test_validate_policy_invalid_branch_reference():
    """ Test policy where a ConditionalBlock points to a non-existing block """
    policy = {
        "blocks": [
            {"block_id": "1", "block_type": "StartBlock", "next_block": "2"},
            {
                "block_id": "2",
                "block_type": "ConditionalBlock",
                "variable": "age",
                "cmp_value": "18",
                "operator": ">=",
                "true_branch": "3",
                "false_branch": "99"
            },
            {"block_id": "3", "block_type": "EndBlock", "decision_value": "Approved"},
        ]
    }
    assert validate_policy(policy) == "ConditionalBlock '2' has an invalid 'false_branch' reference: '99' does not exist."

# =======================================
# Test cases for `check_passed_variables`
# =======================================

def test_check_passed_variables_valid():
    """ Test when passed variables match the expected ones """
    policy = {"variables": ["age", "income"]}
    args = {"age": "25", "income": "5000"}
    assert check_passed_variables(policy, args) is None

def test_check_passed_variables_unexpected():
    """ Test when an unexpected variable is passed """
    policy = {"variables": ["age"]}
    args = {"age": "25", "income": "5000"}
    assert check_passed_variables(policy, args) == "Unexpected variable 'income' in query parameters."

def test_check_passed_variables_missing():
    """ Test when a required variable is missing """
    policy = {"variables": ["age", "income"]}
    args = {"age": "25"}
    assert check_passed_variables(policy, args) == "Expected variable 'income' in query parameters but variable was not found."
