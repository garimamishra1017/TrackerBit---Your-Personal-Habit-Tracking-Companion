from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
from sqlalchemy import func

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trackerbit.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'error'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    health = db.Column(db.Integer, default=50)
    max_health = db.Column(db.Integer, default=50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    tasks = db.relationship('Task', backref='user', lazy=True)
    task_history = db.relationship('TaskHistory', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'level': self.level,
            'experience': self.experience,
            'health': self.health,
            'max_health': self.max_health
        }

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    task_type = db.Column(db.String(20), nullable=False)  # 'habit', 'daily', 'todo'
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    history = db.relationship('TaskHistory', backref='task', lazy=True)

class TaskHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    action_type = db.Column(db.String(20), nullable=False)  # 'complete', 'habit_up', 'habit_down'
    experience_gained = db.Column(db.Integer, default=0)
    health_change = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        habits = Task.query.filter_by(user_id=current_user.id, task_type='habit').all()
        dailies = Task.query.filter_by(user_id=current_user.id, task_type='daily').all()
        todos = Task.query.filter_by(user_id=current_user.id, task_type='todo').all()
        
        experience_percentage = (current_user.experience % 100)
        health_percentage = (current_user.health / current_user.max_health) * 100
        
        return render_template('index.html',
                             habits=habits,
                             dailies=dailies,
                             todos=todos,
                             experience_percentage=experience_percentage,
                             health_percentage=health_percentage)
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('index'))
        
        flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    remember = data.get('remember', False)
    
    if not username or not password:
        return jsonify({
            'success': False,
            'message': 'Please provide both username and password'
        }), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        login_user(user, remember=remember)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
    
    return jsonify({
        'success': False,
        'message': 'Invalid username or password'
    }), 401

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
            
        user = User(username=username)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/api/add-task', methods=['POST'])
@login_required
def add_task():
    title = request.form.get('title')
    task_type = request.form.get('type')
    
    task = Task(title=title,
                task_type=task_type,
                user_id=current_user.id)
    db.session.add(task)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/complete-task', methods=['POST'])
@login_required
def complete_task():
    data = request.get_json()
    task_id = data.get('taskId')
    
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if task was already completed today
    today = datetime.utcnow().date()
    already_completed = TaskHistory.query.filter(
        TaskHistory.task_id == task.id,
        TaskHistory.action_type == 'complete',
        db.func.date(TaskHistory.timestamp) == today
    ).first()
    
    if already_completed and task.task_type == 'daily':
        return jsonify({'error': 'Task already completed today'}), 400
    
    task.completed = True
    task.completed_at = datetime.utcnow()
    
    # Record task completion in history
    history = TaskHistory(
        user_id=current_user.id,
        task_id=task.id,
        action_type='complete',
        experience_gained=10,
        health_change=5
    )
    db.session.add(history)
    
    # Update user stats
    current_user.experience += 10
    current_user.health = min(current_user.health + 5, current_user.max_health)
    
    # Level up if experience reaches 100
    if current_user.experience >= 100:
        current_user.level += 1
        current_user.experience = current_user.experience % 100
        current_user.max_health += 10
        current_user.health = current_user.max_health
    
    db.session.commit()
    return jsonify(current_user.to_dict())

@app.route('/api/update-habit', methods=['POST'])
@login_required
def update_habit():
    data = request.get_json()
    habit_id = data.get('habitId')
    direction = data.get('direction')
    
    habit = Task.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if habit.task_type != 'habit':
        return jsonify({'error': 'Task is not a habit'}), 400
    
    experience_change = 5 if direction == 'up' else -5
    health_change = 3 if direction == 'up' else -3
    
    # Record habit update in history
    history = TaskHistory(
        user_id=current_user.id,
        task_id=habit.id,
        action_type=f'habit_{direction}',
        experience_gained=experience_change,
        health_change=health_change
    )
    db.session.add(history)
    
    # Update user stats
    current_user.experience = max(0, current_user.experience + experience_change)
    current_user.health = max(0, min(current_user.health + health_change, current_user.max_health))
    
    # Level up if experience reaches 100
    if current_user.experience >= 100:
        current_user.level += 1
        current_user.experience = current_user.experience % 100
        current_user.max_health += 10
        current_user.health = current_user.max_health
    
    db.session.commit()
    return jsonify(current_user.to_dict())

@app.route('/api/character-stats')
@login_required
def character_stats():
    return jsonify({
        'level': current_user.level,
        'experiencePercentage': current_user.experience,
        'healthPercentage': (current_user.health / current_user.max_health) * 100
    })

@app.route('/tasks')
@login_required
def tasks():
    habits = Task.query.filter_by(user_id=current_user.id, task_type='habit').all()
    dailies = Task.query.filter_by(user_id=current_user.id, task_type='daily').all()
    todos = Task.query.filter_by(user_id=current_user.id, task_type='todo').all()
    
    return render_template('tasks.html',
                         habits=habits,
                         dailies=dailies,
                         todos=todos)

@app.route('/profile')
@login_required
def profile():
    experience_percentage = (current_user.experience % 100)
    health_percentage = (current_user.health / current_user.max_health) * 100
    
    # Count all task completions from history
    tasks_completed = (
        TaskHistory.query
        .filter(
            TaskHistory.user_id == current_user.id,
            TaskHistory.action_type.in_(['complete', 'habit_up'])
        )
        .count()
    )
    
    # Get daily streaks
    daily_streak = (
        Task.query
        .filter_by(user_id=current_user.id, task_type='daily', completed=True)
        .count()
    )
    
    return render_template('profile.html',
                         experience_percentage=experience_percentage,
                         health_percentage=health_percentage,
                         tasks_completed=tasks_completed,
                         daily_streak=daily_streak)

@app.route('/daily-summary')
@login_required
def daily_summary():
    return render_template('daily_summary.html')

@app.route('/api/daily-summary/<date>')
@login_required
def get_daily_summary(date):
    try:
        summary_date = datetime.strptime(date, '%Y-%m-%d')
        start_of_day = summary_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        # Get habits and their counts for the day
        habits = Task.query.filter_by(
            user_id=current_user.id,
            task_type='habit'
        ).all()
        
        habit_counts = []
        for habit in habits:
            # Count positive and negative habit uses
            positive_count = TaskHistory.query.filter(
                TaskHistory.task_id == habit.id,
                TaskHistory.action_type == 'habit_up',
                TaskHistory.timestamp >= start_of_day,
                TaskHistory.timestamp < end_of_day
            ).count()
            
            negative_count = TaskHistory.query.filter(
                TaskHistory.task_id == habit.id,
                TaskHistory.action_type == 'habit_down',
                TaskHistory.timestamp >= start_of_day,
                TaskHistory.timestamp < end_of_day
            ).count()
            
            habit_counts.append({
                'title': habit.title,
                'count': positive_count - negative_count,
                'positive_count': positive_count,
                'negative_count': negative_count
            })

        # Get dailies completion status
        dailies = Task.query.filter_by(
            user_id=current_user.id,
            task_type='daily'
        ).all()
        
        daily_summary = []
        for daily in dailies:
            completed = TaskHistory.query.filter(
                TaskHistory.task_id == daily.id,
                TaskHistory.action_type == 'complete',
                TaskHistory.timestamp >= start_of_day,
                TaskHistory.timestamp < end_of_day
            ).first() is not None
            
            daily_summary.append({
                'title': daily.title,
                'completed': completed
            })

        # Get todos for the day
        todos = Task.query.filter(
            Task.user_id == current_user.id,
            Task.task_type == 'todo',
            Task.created_at >= start_of_day,
            Task.created_at < end_of_day
        ).all()
        
        todo_summary = []
        for todo in todos:
            completed = TaskHistory.query.filter(
                TaskHistory.task_id == todo.id,
                TaskHistory.action_type == 'complete',
                TaskHistory.timestamp >= start_of_day,
                TaskHistory.timestamp < end_of_day
            ).first() is not None
            
            todo_summary.append({
                'title': todo.title,
                'completed': completed
            })

        # Calculate statistics
        total_tasks = len(daily_summary) + len(todo_summary)
        completed_tasks = sum(1 for d in daily_summary if d['completed']) + sum(1 for t in todo_summary if t['completed'])
        completion_rate = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)

        # Get experience and health changes for the day
        day_stats = db.session.query(
            db.func.sum(TaskHistory.experience_gained).label('exp'),
            db.func.sum(TaskHistory.health_change).label('health')
        ).filter(
            TaskHistory.user_id == current_user.id,
            TaskHistory.timestamp >= start_of_day,
            TaskHistory.timestamp < end_of_day
        ).first()

        return jsonify({
            'habits': habit_counts,
            'dailies': daily_summary,
            'todos': todo_summary,
            'stats': {
                'completionRate': completion_rate,
                'experienceGained': day_stats.exp or 0,
                'healthChange': day_stats.health or 0
            }
        })

    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
