from functools import wraps
from flask import Blueprint, request, jsonify, session
from models import db, Task
from logging_config import get_logger
from datetime import datetime
import time
import uuid

api = Blueprint('api', __name__, url_prefix='/api')


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


@api.before_request
def log_request_start():
    request.start_time = time.time()
    request.request_id = str(uuid.uuid4())[:8]
    logger = get_logger()
    logger.info(
        f"[{request.request_id}] {request.method} {request.path}",
        extra={'request_id': request.request_id, 'method': request.method, 'path': request.path}
    )


@api.after_request
def log_request_end(response):
    logger = get_logger()
    duration_ms = (time.time() - request.start_time) * 1000
    logger.info(
        f"[{request.request_id}] {request.method} {request.path} -> {response.status_code} ({duration_ms:.2f}ms)",
        extra={
            'request_id': request.request_id,
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': round(duration_ms, 2)
        }
    )
    return response


@api.route('/tasks', defaults={'task_id': None}, methods=['GET'])
@api.route('/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_tasks(task_id=None):
    try:
        logger = get_logger()
        user_id = session['user_id']
        task_status = request.args.get('status')

        if task_status and task_status not in Task.VALID_STATUSES:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(Task.VALID_STATUSES)}'}), 400

        if task_id:
            task = Task.query.filter_by(id=task_id, user_id=user_id).first()
            if not task:
                return jsonify({'error': f'Task with ID {task_id} not found'}), 404
            logger.debug(f"Retrieved task with ID={task_id}")
            return jsonify(task.to_dict())

        query = Task.query.filter_by(user_id=user_id)
        if task_status:
            query = query.filter_by(status=task_status)
            logger.debug(f"Retrieved tasks with status={task_status}")
        else:
            logger.debug("Retrieved all tasks")

        tasks = query.all()
        return jsonify({
            'tasks': [t.to_dict() for t in tasks],
            'count': len(tasks)
        })
    except Exception as err:
        logger = get_logger()
        logger.error(f"Error retrieving tasks: {err}")
        return jsonify({'error': 'An error occurred while retrieving tasks'}), 500


@api.route('/tasks', methods=['POST'])
@login_required
def create_task():
    logger = get_logger()
    data = request.get_json()

    if not data or 'name' not in data:
        logger.warning("Create task failed: name is required")
        return jsonify({'error': 'Task name is required'}), 400

    name = data['name'].strip()
    if not name:
        logger.warning("Create task failed: empty name")
        return jsonify({'error': 'Task name cannot be empty'}), 400

    status = data.get('status', 'to-do')
    if status not in Task.VALID_STATUSES:
        logger.warning(f"Create task failed: invalid status '{status}'")
        return jsonify({
            'error': f'Invalid status. Must be one of: {", ".join(Task.VALID_STATUSES)}'
        }), 400

    task = Task(name=name, status=status, user_id=session['user_id'])
    db.session.add(task)
    db.session.commit()

    logger.info(f"Created task: ID {task.id}, name='{task.name}'")
    return jsonify({
        'message': 'Task added successfully',
        'task': task.to_dict()
    }), 201


@api.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    logger = get_logger()
    user_id = session['user_id']
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        logger.warning(f"Update failed: task ID {task_id} not found")
        return jsonify({'error': f'Task with ID {task_id} not found'}), 404

    data = request.get_json()
    if not data:
        logger.warning(f"Update failed: no data provided for task ID {task_id}")
        return jsonify({'error': 'No data provided'}), 400

    changes = []
    if 'name' in data:
        name = data['name'].strip()
        if not name:
            logger.warning("Update failed: empty name")
            return jsonify({'error': 'Task name cannot be empty'}), 400
        task.name = name
        changes.append(f"name='{name}'")

    if 'status' in data:
        if data['status'] not in Task.VALID_STATUSES:
            logger.warning(f"Update failed: invalid status '{data['status']}'")
            return jsonify({
                'error': f'Invalid status. Must be one of: {", ".join(Task.VALID_STATUSES)}'
            }), 400
        task.status = data['status']
        changes.append(f"status='{data['status']}'")

    task.updated_at = datetime.utcnow()
    db.session.commit()

    logger.info(f"Updated task ID {task_id}: {', '.join(changes)}")
    return jsonify({
        'message': f'Task {task_id} updated',
        'task': task.to_dict()
    })


@api.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    logger = get_logger()
    user_id = session['user_id']
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        logger.warning(f"Delete failed: task ID {task_id} not found")
        return jsonify({'error': f'Task with ID {task_id} not found'}), 404

    task_name = task.name
    db.session.delete(task)
    db.session.commit()

    logger.info(f"Deleted task: ID {task_id}, name='{task_name}'")
    return jsonify({
        'message': f'Task with ID {task_id} was deleted successfully'
    })
