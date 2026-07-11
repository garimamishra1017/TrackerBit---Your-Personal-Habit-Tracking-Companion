# TrackerBit - Your Personal Habit Tracking Companion

Welcome to TrackerBit.com - A gamified habit tracking and personal development. Level up your life by turning your goals into a fun, rewarding game!

## 🌟 Features

- **Task Management**
  - Habits: Track positive and negative habits
  - Dailies: Set recurring tasks
  - To-Dos: Manage one-time tasks
  
- **Progress Tracking**
  - Experience points and leveling system
  - Health points for accountability
  - Daily summaries and statistics
  - Task completion streaks

- **User Experience**
  - Clean, modern interface
  - Mobile-responsive design
  - Real-time updates
  - Intuitive navigation

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/trackerbit.git
   cd trackerbit
   ```

2. **Create a Virtual Environment** (Recommended)
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Required Packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   Create a `.env` file in the root directory:
   ```
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=development
   ```

5. **Initialize the Database**
   ```bash
   python
   >>> from app import db, app
   >>> with app.app_context():
   >>>     db.create_all()
   >>> exit()
   ```

6. **Run the Application**
   ```bash
   python app.py
   ```

7. **Access the Website**
   - Open your browser and go to: `http://localhost:5000`
   - Register a new account
   - Start tracking your habits!

## 🌐 Accessing TrackerBit.com

### Development Environment
- Local URL: `http://localhost:5000`
- Default admin credentials:
  - Username: admin
  - Password: admin123

### Production Environment
- Visit [TrackerBit.com](https://www.trackerbit.com)
- Create your account
- Start your journey to a better you!

## 🛠️ Technologies Used

- **Backend**
  - Python 3.8+
  - Flask Framework
  - SQLAlchemy ORM
  - SQLite Database

- **Frontend**
  - HTML5/CSS3
  - JavaScript (ES6+)
  - Font Awesome Icons
  - Inter Font Family





