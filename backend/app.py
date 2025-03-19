import os
import json
import uuid
import execution_engine
from flask import Flask, request, jsonify
from validations.policy_validations import validate_policy, check_passed_variables

app = Flask(__name__)

POLICY_DB_DIR = "policies"

os.makedirs(POLICY_DB_DIR, exist_ok=True)

def get_policy_path(policy_id: str) -> str:
    return os.path.join(POLICY_DB_DIR, f"{policy_id}.json")

@app.route("/policies/new", methods=["POST"])
def policies():
    # Creates new policy
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
    return jsonify({"message": f"Policy {policy_id} deleted successfully."})

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

    passed_variables = check_passed_variables(policy, args)
    if passed_variables:
        return jsonify({"error": passed_variables}), 400

    args = request.args.to_dict(flat=True)
    print(args)
    decision = execution_engine.execute_policy(policy,args)

    return jsonify({"decision": decision}), 200

if __name__ == "__main__":
    app.run(debug=True)
    