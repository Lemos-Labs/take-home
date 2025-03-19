import os
import json
import uuid
import execution_engine
from flask import Flask, request, jsonify

app = Flask(__name__)

POLICY_DB_DIR = "policies"

os.makedirs(POLICY_DB_DIR, exist_ok=True)

def get_policy_path(policy_id: str) -> str:
    return os.path.join(POLICY_DB_DIR, f"{policy_id}.json")

def validate_policy(policy, args):
    block_validation = check_block_amount(policy)
    if  block_validation is not None:
        return block_validation

    passed_variables = check_passed_variables(policy, args)
    if passed_variables is not None:
        return passed_variables
    
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

    for arg in args:
        if arg not in variables:
            return " Unexpected variable '{arg}' in query parameters"

    return None

@app.route("/policies", methods=["GET", "POST"])
def policies():
    if request.method == "POST":
        data = request.get_json()

        if not data or "blocks" not in data:
            return jsonify({"error": "Invalid policy format"}), 400

        policy_id = str(uuid.uuid4())
        policy_path = get_policy_path(policy_id)

        validation_err = validate_policy(data)
        if validation_err:
            return jsonify({"error": validation_err}), 400

        policy_data = {
            "id": policy_id,
            "name": data["name"],
            "variables": data["variables"],
            "blocks": data["blocks"]
        }

        with open(policy_path, "w") as f:
            json.dump(policy_data, f, indent=4)

        return jsonify({"message": "Successfully created policy", "policy_id": policy_id}), 201
    
    else:  # GET request
        """List all stored policies"""
        policies = [f.replace(".json", "") for f in os.listdir(POLICY_DB_DIR) if f.endswith(".json")]
        return jsonify({"policies": policies})

@app.route("/policies/<policy_id>", methods=["GET"])
def get_policy(policy_id: str):
    policy_path = get_policy_path(policy_id)

    if not os.path.exists(policy_path):
        return jsonify({"error": "Policy not found"}), 404

    with open(policy_path, "r") as f:
        policy_data = json.load(f)

    return jsonify(policy_data)

@app.route("/policies/<policy_id>", methods=["DELETE"])
def delete_policy(policy_id):
    policy_path = get_policy_path(policy_id)

    if not os.path.exists(policy_path):
        return jsonify({"error": "Policy not found"}), 404

    os.remove(policy_path)
    return jsonify({"message": f"Policy {policy_id} deleted successfully"})

@app.route("/execute/<policy_id>", methods=["POST"])
def execute_policy(policy_id):
    """
    Executes a stored policy using provided variables.
    Expects JSON payload with variable values.
    """
    policy_path = get_policy_path(policy_id)

    if not os.path.exists(policy_path):
        return jsonify({"error": "Policy not found"}), 404

    with open(policy_path, "r") as f:
        policy = json.load(f)

    # Extract query parameters
    args = request.args

    print(args.to_dict(flat=True))

    validation = validate_policy(policy, args)
    if validation:
        return jsonify({"error": validation}), 400

    args = request.args.to_dict(flat=True)
    print(args)
    decision = execution_engine.execute_policy(policy,args)

    return jsonify({"decision": decision}), 200

if __name__ == "__main__":
    app.run(debug=True)
    