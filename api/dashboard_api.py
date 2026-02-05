from flask import Blueprint, jsonify
from data.hydration_history import log_hydration

dashboard_api = Blueprint("dashboard_api", __name__)

@dashboard_api.route("/log/<int:score>")
def log(score):
    log_hydration(score)
    return jsonify({"status": "logged"})
