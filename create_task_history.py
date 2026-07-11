from app import db, app

def upgrade():
    with app.app_context():
        # Create TaskHistory table
        db.engine.execute('''
            CREATE TABLE task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                experience_gained INTEGER NOT NULL DEFAULT 0,
                health_change INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (task_id) REFERENCES task (id)
            )
        ''')

def downgrade():
    with app.app_context():
        db.engine.execute('DROP TABLE IF EXISTS task_history')

if __name__ == '__main__':
    upgrade()
