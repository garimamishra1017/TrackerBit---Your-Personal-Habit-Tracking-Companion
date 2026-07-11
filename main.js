// Main JavaScript file for TrackerBit

document.addEventListener('DOMContentLoaded', function() {
    setupTaskHandlers();
    updateCharacterStats();
    setupModalHandlers();
    updateSummary();
});

function setupTaskHandlers() {
    // Handle task completion
    document.querySelectorAll('.task-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function(e) {
            const taskId = this.dataset.taskId;
            const taskType = this.dataset.taskType;
            
            if (this.checked) {
                completeTask(taskId, taskType);
            }
        });
    });

    // Handle habit buttons
    document.querySelectorAll('.habit-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const habitId = this.dataset.habitId;
            const direction = this.dataset.direction; // 'up' or 'down'
            
            // Add visual feedback
            this.classList.add('clicked');
            setTimeout(() => this.classList.remove('clicked'), 200);
            
            updateHabit(habitId, direction);
        });
    });
}

function completeTask(taskId, taskType) {
    fetch('/api/complete-task', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            taskId: taskId,
            taskType: taskType
        })
    })
    .then(response => response.json())
    .then(data => {
        // Mark task as completed in UI
        const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
        if (taskElement) {
            taskElement.classList.add('completed');
            const button = taskElement.querySelector('.task-complete-btn');
            if (button) {
                button.disabled = true;
            }
        }
        
        // Update character stats and summary
        updateCharacterStats();
        updateSummary();
        showNotification('Task completed! +10 XP', 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Failed to complete task', 'error');
    });
}

function updateHabit(habitId, direction) {
    fetch('/api/update-habit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            habitId: habitId,
            direction: direction
        })
    })
    .then(response => response.json())
    .then(data => {
        updateCharacterStats();
        updateSummary();
        const message = direction === 'up' ? 'Good job!' : 'Keep trying!';
        const type = direction === 'up' ? 'success' : 'warning';
        showNotification(message + ' ' + (direction === 'up' ? '+5 XP' : '-5 XP'), type);
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Failed to update habit', 'error');
    });
}

function updateCharacterStats() {
    fetch('/api/character-stats')
    .then(response => response.json())
    .then(data => {
        // Animate the changes
        animateValue('level', data.level);
        animateProgressBar('experience', data.experiencePercentage);
        animateProgressBar('health', data.healthPercentage);
    })
    .catch(error => console.error('Error:', error));
}

function animateValue(elementId, newValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const currentValue = parseInt(element.textContent);
    if (currentValue === newValue) return;
    
    const step = newValue > currentValue ? 1 : -1;
    let current = currentValue;
    
    const animate = () => {
        current += step;
        element.textContent = current;
        
        if ((step > 0 && current < newValue) || (step < 0 && current > newValue)) {
            requestAnimationFrame(animate);
        }
    };
    
    requestAnimationFrame(animate);
}

function animateProgressBar(elementId, newPercentage) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.style.width = newPercentage + '%';
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const icon = document.createElement('i');
    icon.className = getNotificationIcon(type);
    notification.appendChild(icon);
    
    const text = document.createElement('span');
    text.textContent = ' ' + message;
    notification.appendChild(text);
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 2000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success':
            return 'fas fa-check-circle';
        case 'error':
            return 'fas fa-times-circle';
        case 'warning':
            return 'fas fa-exclamation-circle';
        default:
            return 'fas fa-info-circle';
    }
}

// Modal Handling
function setupModalHandlers() {
    const modal = document.getElementById('add-task-modal');
    if (!modal) return;
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    // Handle escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
}

function showAddTaskModal(taskType) {
    const modal = document.getElementById('add-task-modal');
    const typeInput = document.getElementById('task-type');
    
    typeInput.value = taskType;
    modal.classList.add('show');
    
    // Focus on the title input
    document.getElementById('task-title').focus();
}

function closeModal() {
    const modal = document.getElementById('add-task-modal');
    modal.classList.remove('show');
    
    // Reset form
    document.getElementById('new-task-form').reset();
}

// Add new task
document.getElementById('new-task-form')?.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    fetch('/api/add-task', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Task added successfully!', 'success');
            closeModal();
            location.reload();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Failed to add task', 'error');
    });
});

// Summary section functionality
function updateSummary() {
    const today = new Date().toISOString().split('T')[0];
    fetch(`/api/daily-summary/${today}`)
        .then(response => response.json())
        .then(data => {
            updateHabitsSummary(data.habits);
            updateDailiesSummary(data.dailies);
            updateTodosSummary(data.todos);
            updateStatistics(data.stats);
        })
        .catch(error => console.error('Error fetching summary:', error));
}

function updateHabitsSummary(habits) {
    const container = document.getElementById('habits-summary');
    if (!container) return;
    
    container.innerHTML = habits.map(habit => `
        <div class="summary-item">
            <span>${habit.title}</span>
            <span class="${habit.count > 0 ? 'habit-positive' : habit.count < 0 ? 'habit-negative' : ''}">
                ${habit.count > 0 ? '+' : ''}${habit.count}
                <small>(+${habit.positive_count}/-${habit.negative_count})</small>
            </span>
        </div>
    `).join('');
}

function updateDailiesSummary(dailies) {
    const container = document.getElementById('dailies-summary');
    if (!container) return;
    
    container.innerHTML = dailies.map(daily => `
        <div class="summary-item ${daily.completed ? 'completed' : ''}">
            <span>${daily.title}</span>
            <i class="fas ${daily.completed ? 'fa-check' : 'fa-times'}"></i>
        </div>
    `).join('');
}

function updateTodosSummary(todos) {
    const container = document.getElementById('todos-summary');
    if (!container) return;
    
    container.innerHTML = todos.map(todo => `
        <div class="summary-item ${todo.completed ? 'completed' : ''}">
            <span>${todo.title}</span>
            <i class="fas ${todo.completed ? 'fa-check' : 'fa-times'}"></i>
        </div>
    `).join('');
}

function updateStatistics(stats) {
    // Update completion rate
    const completionRate = document.getElementById('completionRate');
    const completionRateText = document.getElementById('completionRateText');
    if (completionRate && completionRateText) {
        completionRate.style.width = `${stats.completionRate}%`;
        completionRateText.textContent = `${stats.completionRate}%`;
    }

    // Update experience gained
    const experienceGained = document.getElementById('experienceGained');
    if (experienceGained) {
        experienceGained.textContent = `${stats.experienceGained} XP`;
    }

    // Update health change
    const healthChange = document.getElementById('healthChange');
    if (healthChange) {
        const change = stats.healthChange;
        healthChange.textContent = change > 0 ? `+${change}` : change;
        healthChange.className = change >= 0 ? 'positive' : 'negative';
    }
}
