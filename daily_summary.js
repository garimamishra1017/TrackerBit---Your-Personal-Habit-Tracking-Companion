let currentDate = new Date();

function formatDate(date) {
    return date.toLocaleDateString('en-US', { 
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatDateForPicker(date) {
    return date.toISOString().split('T')[0];
}

function updateDateDisplay() {
    document.getElementById('currentDate').textContent = formatDate(currentDate);
    document.getElementById('datePicker').value = formatDateForPicker(currentDate);
}

function previousDate() {
    currentDate.setDate(currentDate.getDate() - 1);
    updateDateDisplay();
    fetchDailySummary();
}

function nextDate() {
    currentDate.setDate(currentDate.getDate() + 1);
    updateDateDisplay();
    fetchDailySummary();
}

function selectDate(dateString) {
    currentDate = new Date(dateString);
    updateDateDisplay();
    fetchDailySummary();
}

function updateHabitsSummary(habits) {
    const container = document.getElementById('habits-summary');
    container.innerHTML = habits.map(habit => `
        <div class="summary-item">
            <span>${habit.title}</span>
            <span class="${habit.count > 0 ? 'habit-positive' : 'habit-negative'}">
                ${habit.count > 0 ? '+' : ''}${habit.count}
            </span>
        </div>
    `).join('');
}

function updateDailiesSummary(dailies) {
    const container = document.getElementById('dailies-summary');
    container.innerHTML = dailies.map(daily => `
        <div class="summary-item ${daily.completed ? 'completed' : ''}">
            <span>${daily.title}</span>
            <i class="fas ${daily.completed ? 'fa-check' : 'fa-times'}"></i>
        </div>
    `).join('');
}

function updateTodosSummary(todos) {
    const container = document.getElementById('todos-summary');
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
    completionRate.style.width = `${stats.completionRate}%`;
    completionRateText.textContent = `${stats.completionRate}%`;

    // Update experience gained
    const experienceGained = document.getElementById('experienceGained');
    experienceGained.textContent = `${stats.experienceGained} XP`;

    // Update health change
    const healthChange = document.getElementById('healthChange');
    healthChange.textContent = stats.healthChange > 0 ? `+${stats.healthChange}` : stats.healthChange;
    healthChange.className = stats.healthChange >= 0 ? 'positive' : 'negative';
}

function fetchDailySummary() {
    const dateStr = currentDate.toISOString().split('T')[0];
    
    fetch(`/api/daily-summary/${dateStr}`)
        .then(response => response.json())
        .then(data => {
            updateHabitsSummary(data.habits);
            updateDailiesSummary(data.dailies);
            updateTodosSummary(data.todos);
            updateStatistics(data.stats);
        })
        .catch(error => console.error('Error fetching daily summary:', error));
}

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    // Set the date picker's max value to today
    const today = new Date();
    const datePicker = document.getElementById('datePicker');
    datePicker.max = formatDateForPicker(today);
    
    // Initialize with today's date
    currentDate = today;
    updateDateDisplay();
    fetchDailySummary();
    document.getElementById('datePicker').addEventListener('change', (e) => {
        selectDate(e.target.value);
    });
});
