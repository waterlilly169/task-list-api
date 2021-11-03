from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, request, make_response
from datetime import datetime
from sqlalchemy import desc
import json
import os
import requests
from dotenv import load_dotenv
load_dotenv()


tasks_bp = Blueprint("tasks", __name__, url_prefix ="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix ="/goals")

@tasks_bp.route("", methods=["POST"])
def create_new_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return {"details": "Invalid data"}, 400

    new_task = Task(title=request_body["title"],
                    description=request_body["description"],
                    completed_at=request_body["completed_at"]
                    )
    db.session.add(new_task)
    db.session.commit()
    
    return make_response({"task": {"id":new_task.task_id, "title":new_task.title, "description":new_task.description, "is_complete":bool(new_task.completed_at)}}), 201

@tasks_bp.route("", methods=["GET"])
def get_all_tasks():
    sort_query = request.args.get("sort")

    if sort_query == "asc":
        tasks = Task.query.order_by("title")
    elif sort_query == "desc":
        tasks = Task.query.order_by(desc("title"))
    else:
        tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])

@tasks_bp.route("/<task_id>", methods=["GET"])
def get_single_task(task_id):  
    task = Task.query.get(task_id)
    if task:
        return {
            "task":{
                "id": task.task_id, 
                "title": task.title, 
                "description": task.description, 
                "is_complete": bool(task.completed_at)
                }}, 200
    else:
        return jsonify(None), 404

@tasks_bp.route("/<task_id>", methods=["PUT"])
def change_data(task_id):
    task = Task.query.get(task_id)
    form_data = request.get_json()
    
    if task:
        task.title = form_data["title"]
        task.description = form_data["description"]
        # task.completed_at = form_data["completed_at"]

        db.session.commit()
        return {
            "task":{
                "id": task.task_id, 
                "title": task.title, 
                "description": task.description, 
                "is_complete": bool(task.completed_at)
                }}
    else:
        return jsonify(None), 404

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_planet(task_id):
    """Defines an endpoint DELETE to delete planet out of existence"""
    task = Task.query.get(task_id)

    if task:
        db.session.delete(task)
        db.session.commit()
        return {"details": "Task 1 \"Go on my daily walk 🏞\" successfully deleted"}
    else:
        return jsonify(None), 404

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def task_incomplete(task_id):
    task = Task.query.get(task_id)
    if task == None:
        return "", 404
    task.completed_at = None
    return {"task": task.to_dict()}


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def task_complete(task_id):
    task = Task.query.get(task_id)
    
    if task == None:
        return "", 404
    task.completed_at = datetime.now()
    post_message_to_slack(f"Someone just completed the task {task.title}")

    return {"task": task.to_dict()}


def post_message_to_slack(text):
    slack_token = os.environ.get('SLACK_BOT_TOKEN')
    slack_channel = os.environ.get('slack_channel_num')
    return requests.post('https://slack.com/api/chat.postMessage', {
        'token': slack_token,
        'channel': slack_channel,
        'text': text,
    }).json()	


#Goals section

@goals_bp.route("", methods=["POST"])
def create_new_goal():
    request_form = request.get_json()

    if "title" not in request_form:
        return {"details": "Invalid data"}, 400

    new_goal = Goal(title=request_form["title"]
                    )
    db.session.add(new_goal)
    db.session.commit()
    
    return make_response({"goal": {"id":new_goal.goal_id, "title":new_goal.title}}), 201

@goals_bp.route("", methods=["GET"])
def get_all_goals():
    goals = Goal.query.all()
    return jsonify([goal.to_dict_goal() for goal in goals])

@goals_bp.route("/<goal_id>", methods=["GET"])
def get_single_goal(goal_id):  
    goal = Goal.query.get(goal_id)
    if goal:
        return {
            "goal":{
                "id": goal.goal_id, 
                "title": goal.title, 
                }}, 200
    else:
        return jsonify(None), 404

@goals_bp.route("/<goal_id>", methods=["PUT"])
def change_goal_data(goal_id):
    goal = Goal.query.get(goal_id)
    form_data = request.get_json()
    
    if goal:
        goal.title = form_data["title"]
        db.session.commit()
        return {
            "goal":{
                "id": goal.goal_id, 
                "title": goal.title, 
                }}
    else:
        return jsonify(None), 404

@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_planet(goal_id):
    """Defines an endpoint DELETE to delete planet out of existence"""
    goal = Goal.query.get(goal_id)

    if goal:
        db.session.delete(goal)
        db.session.commit()
        return {"details": "Goal 1 \"Build a habit of going outside daily\" successfully deleted"}
    else:
        return jsonify(None), 404