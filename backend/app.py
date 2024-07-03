from flask import Flask, request, jsonify, session
from flask_cors import CORS, cross_origin
from config import Config
from model import db, Task, UnschedulableTask, User
from datetime import datetime
from flask_migrate import Migrate
from schedule import create_schedule
from flask_bcrypt import Bcrypt
from flask_session import Session
import logging
# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

bcrypt = Bcrypt(app)
server_session = Session(app)
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/register', methods=["POST"])
@cross_origin()
def register():
    print("Register endpoint hit") 
    logging.debug(f"Register endpoint hit")
    data = request.get_json()
    print("Received data:", data) 
    email = data.get('email')
    password = data.get('password')

    user_exists = User.query.filter_by(email=email).first() is not None

    if user_exists:
        return jsonify({'message': 'user email already exists'})
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "id": new_user.id,
        "email": new_user.email
    }), 200

@app.route('/login', methods=["POST"])
@cross_origin()
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        session['user_id'] = user.id
        user_data = {
            'id': user.id,
            'email': user.email
        }
        return jsonify({'message': 'login successfully created', 'user': user_data}), 200
    else:
        return jsonify({'message': 'invalid credentials'}), 401
    

@app.route('/logout', methods=["POST"])
@cross_origin()
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'user logged out successfully'}), 200


def convert_to_24_hour_format(time_str):
    """Convert 12-hour time format with AM/PM to 24-hour format."""
    print("Interval in convert interval", time_str)
    in_time = datetime.strptime(time_str, "%I:%M%p")
    return in_time.strftime("%H:%M")

def convert_interval_to_24_hour_format(interval):
    start, end = interval.split('-')
    start_24 = convert_to_24_hour_format(start.strip())
    end_24 = convert_to_24_hour_format(end.strip())
    return f"{start_24}-{end_24}"

def is_valid_day(day):
    valid_days = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'}
    return day in valid_days

def is_valid_interval(interval):
    try:
        start, end = interval.split('-')
        # Ensure start and end times are valid 24-hour format
        datetime.strptime(start, '%H:%M')
        datetime.strptime(end, '%H:%M')
        return True
    except ValueError:
        return False


# This validates all of the fields for each task
# What's happening is we are only looking at the data we are passing through
# If we are just doing an update, then the if 'taskname' not in data will return true if it's just 
# a partial updagte

# TODO: There is an issue with validate_task_data that set's fixed twice
def validate_task_data(data, is_update=False):
    # Validate the presence and type of the 'fixed' field first
    if 'fixed' in data and not isinstance(data['fixed'], bool):
        return 'Invalid data: fixed must be a bool', 400
    
    if 'fixed' in data and data['fixed'] == True:
        if 'fixed_day' not in data or not is_valid_day(data['fixed_day']):
            return 'Invalid data: fixed_day must be a valid day of the week', 400
        if 'fixed_start_time' not in data or not isinstance(data['fixed_start_time'], str):
            return 'Invalid data: fixed_start_time must be provided and must be a valid time', 400
        if 'fixed_end_time' not in data or not isinstance(data['fixed_end_time'], str):
            return 'Invalid data: fixed_end_time must be provided and must be a valid time', 400
        try:
            datetime.strptime(data['fixed_start_time'], '%H:%M')
            datetime.strptime(data['fixed_end_time'], '%H:%M')
        except ValueError:
            return 'Invalid data: fixed_start_time and fixed_end_time must be valid times', 400
    else: 
        required_fields = {
        'taskname': str,
        'fixed': bool,
        'duration': int,
        'difficulty': int,
        'importance': int,
        'preferred_days': list,
        'all_days': list,
        'preferred_intervals': list,
        'max_intervals': list
      }

        for field, field_type in required_fields.items():
            if field in data:
                if not isinstance(data[field], field_type):
                    return f'Invalid data: {field} must be a {field_type.__name__}', 400
            elif not is_update:
                return f'Invalid data: {field} must be provided and must be a {field_type.__name__}', 400
            
        # Additional validation for content of specific fields
        if 'preferred_days' in data and not all(is_valid_day(day) for day in data['preferred_days']):
            return 'Invalid data: preferred_days must contain valid days of the week', 400
        if 'all_days' in data and not all(is_valid_day(day) for day in data['all_days']):
            return 'Invalid data: all_days must contain valid days of the week', 400
        if 'preferred_intervals' in data and not all(is_valid_interval(interval) for interval in data['preferred_intervals']):
            logging.debug(f"Invalid interval detected: {data['preferred_intervals']}")
            return 'Invalid data: preferred_intervals must contain valid time intervals', 400
        if 'max_intervals' in data and not all(is_valid_interval(interval) for interval in data['max_intervals']):
            return 'Invalid data: max_intervals must contain valid time intervals', 400

    # If all validations pass
    return None, 200


@app.route('/')
def home():
    return "Welcome to the AI Study Scheduler API"



# This function adds a task to the database
@app.route('/addTask', methods=['POST'])
@cross_origin()
def add_task():
    
    
    # if request.method == 'OPTIONS':
    #     response = jsonify({'message': 'Preflight request'})
    #     response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
    #     response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    #     response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    #     return response, 200

    print("Received a POST request")
    data = request.get_json()
    print(data)
     # Convert intervals to 24-hour format if they exist
    if 'preferred_intervals' in data and data['preferred_intervals']:
        data['preferred_intervals'] = [convert_interval_to_24_hour_format(interval) for interval in data['preferred_intervals']]
    if 'max_intervals' in data and data['max_intervals']:
        data['max_intervals'] = [convert_interval_to_24_hour_format(interval) for interval in data['max_intervals']]

    print("Converted data", data)
    error_message, status_code = validate_task_data(data, is_update=False)
    print(error_message)
    if status_code != 200:
        response = jsonify({'message': error_message})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        return response, status_code
    
    task = Task(
        user_id=data['user_id'],
        taskname=data['taskname'],
        fixed=data['fixed'],
        duration=data['duration'],
        preferred_intervals=data.get('preferred_intervals') if not data['fixed'] else None,
        preferred_days=data.get('preferred_days') if not data['fixed'] else None,
        max_intervals=data.get('max_intervals') if not data['fixed'] else None,
        all_days=data.get('all_days') if not data['fixed'] else None,
        difficulty=data['difficulty'] if not data['fixed'] else None,
        importance=data.get('importance') if not data['fixed'] else None,
        fixed_day=data['fixed_day'] if data['fixed'] else None,
        fixed_start_time=datetime.strptime(data['fixed_start_time'], '%H:%M').time() if data['fixed'] else None,
        fixed_end_time=datetime.strptime(data['fixed_end_time'], '%H:%M').time() if data['fixed'] else None
    )
    db.session.add(task)
    db.session.commit()

    response = jsonify({'message': 'task added successfully', 
                        'task': {
                            'id': task.id,
                            'user_id': task.user_id,
                            'taskname': task.taskname,
                            'fixed': task.fixed,
                            'duration': task.duration,
                            'preferred_intervals': task.preferred_intervals,
                            'preferred_days': task.preferred_days,
                            'max_intervals': task.max_intervals,
                            'all_days': task.all_days,
                            'difficulty': task.difficulty,
                            'importance': task.importance,
                            'fixed_day': task.fixed_day,
                            'fixed_start_time': task.fixed_start_time.strftime('%H:%M') if task.fixed_start_time else None,
                            'fixed_end_time': task.fixed_end_time.strftime('%H:%M') if task.fixed_end_time else None
                        }})
    return response, 201

# Add unschedulable task to databse
@app.route('/addUnschedulableTask', methods=['POST'])
def add_unscheduled_task():
    data = request.get_json()

    # Validate task_id
    if 'task_id' not in data or not isinstance(data['task_id'], int):
        return jsonify({'message': 'Invalid data: task_id must be provided and must be an integer'}), 400
    
    task = Task.query.get(data['task_id'])
    if not task:
        return jsonify({'message': 'Task not found'}), 404
    
    unschedulable_task = UnschedulableTask(task_id=data['task_id'])
    db.session.add(unschedulable_task)
    db.session.commit()

    return jsonify({'message': 'Unschedulable task added successfully'}), 201



# This function is to get all of the tasks, specified my user
@app.route('/getTasks/<int:user_id>', methods=['GET'])
def get_tasks(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()
    tasks_list = [
        {
            'id': task.id,
            'taskname': task.taskname,
            'fixed': task.fixed,
            'duration': task.duration,
            'preferred_intervals': task.preferred_intervals,
            'preferred_days': task.preferred_days,
            'max_intervals': task.max_intervals,
            'all_days': task.all_days,
            'difficulty': task.difficulty,
            'importance': task.importance,
            'created_at': task.created_at
        } for task in tasks
    ]
    return jsonify(tasks_list), 200

# This is a function to update a task by the task_id
# In case you decide to change any of the variables of a task (i.e. change it from fixed to not fixed)
@app.route('/updateTask/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    task = Task.query.get(task_id)
    # If you try to update a task with an ID that doesn't exist
    if not task:
        return jsonify({'message': 'Task not found'}), 404
    
    # Validate incoming data
    error_message, status_code = validate_task_data(data, is_update=True)
    if status_code != 200:
        return jsonify({'message': error_message}), status_code

    # Update the fixed field first
    if 'fixed' in data:
        task.fixed = data['fixed']

    # Update fields based on the fixed status
    if task.fixed:
        task.taskname = data.get('taskname', task.taskname)
        task.fixed_day = data.get('fixed_day', task.fixed_day)
        task.fixed_start_time = datetime.strptime(data['fixed_start_time'], '%H:%M').time() if 'fixed_start_time' in data else task.fixed_start_time
        task.fixed_end_time = datetime.strptime(data['fixed_end_time'], '%H:%M').time() if 'fixed_end_time' in data else task.fixed_end_time
        task.duration = task.duration = data.get('duration', task.duration)
        task.preferred_intervals = None
        task.preferred_days = None
        task.max_intervals = None
        task.all_days = None
        task.difficulty = None
        task.importance = None
    else:
        task.taskname = data.get('taskname', task.taskname)
        task.duration = data.get('duration', task.duration)
        task.preferred_intervals = data.get('preferred_intervals', task.preferred_intervals)
        task.preferred_days = data.get('preferred_days', task.preferred_days)
        task.max_intervals = data.get('max_intervals', task.max_intervals)
        task.all_days = data.get('all_days', task.all_days)
        task.difficulty = data.get('difficulty', task.difficulty)
        task.importance = data.get('importance', task.importance)
        task.fixed_day = None
        task.fixed_start_time = None
        task.fixed_end_time = None
    
    db.session.commit()
    return jsonify({'message': 'Task updated successfully'}), 200

# This is the function to delete a task
@app.route('/deleteTask/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'message': 'Task not found'}), 404
    
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'}), 200

@app.route('/createSchedule', methods=['POST'])
def create_schedule_route():
    schedule, unschedulable = create_schedule()
    print("Scheduled tasks", schedule)
    print("Unscheduled task", unschedulable)

    return jsonify({'schedule': schedule, 'unschedulable': [task.id for task in unschedulable]}), 200


if __name__ == '__main__':
    app.run(debug=True)
