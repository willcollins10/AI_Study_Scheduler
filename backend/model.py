from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each table
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    taskname = db.Column(db.String(255), nullable=False)
    fixed = db.Column(db.Boolean, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    preferred_intervals = db.Column(db.ARRAY(db.String), nullable=True)  # Array of time intervals in string format
    preferred_days = db.Column(db.ARRAY(db.String), nullable=True)  # Array of days in string format
    max_intervals = db.Column(db.ARRAY(db.String), nullable=True)  # Array of time intervals in string format
    all_days = db.Column(db.ARRAY(db.String), nullable=True)  # Array of days in string format
    difficulty = db.Column(db.Integer, nullable=True)
    importance = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    fixed_day = db.Column(db.String(10), nullable=True)  # For fixed tasks
    fixed_start_time = db.Column(db.Time, nullable=True)  # For fixed tasks
    fixed_end_time = db.Column(db.Time, nullable=True)  # For fixed tasks

    # This is a user attribute 
    # Lazy is here so tasks are only loaded when I access the tasks attribute
        # user = User.query.first() (no tasks are loaded from the database)
        # tasks = user.tasks (now tasks are loaded from the database)
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'taskname': self.taskname,
            'fixed': self.fixed,
            'duration': self.duration,
            'preferred_intervals': self.preferred_intervals,
            'preferred_days': self.preferred_days,
            'max_intervals': self.max_intervals,
            'all_days': self.all_days,
            'difficulty': self.difficulty,
            'importance': self.importance,
            'created_at': self.created_at,
            'fixed_day': self.fixed_day,
            'fixed_start_time': self.fixed_start_time,
            'fixed_end_time': self.fixed_end_time
        }



class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    day = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    # This allows be to access specific task objects from the Schedule db
    task = db.relationship('Task')

class UnschedulableTask(db.Model):
    __tablename__ = 'unschedulable_tasks'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    task = db.relationship('Task')