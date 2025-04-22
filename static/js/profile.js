document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Auto-hide alerts
    setTimeout(() => {
        document.querySelectorAll('.alert:not(.alert-important)').forEach(alert => {
            new bootstrap.Alert(alert).close();
        });
    }, 5000);

    // Task completion toggle functionality
    document.querySelectorAll('.task-completion-toggle').forEach(toggle => {
        toggle.addEventListener('change', function() {
            const taskId = this.dataset.taskId;
            const csrftoken = getCookie('csrftoken');
            const isCompleted = this.checked;

            fetch(`/tasks/${taskId}/toggle-complete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    is_completed: isCompleted
                })
            })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    const taskRow = document.querySelector(`#task-${taskId}`);
                    if (taskRow) {
                        // Update visual elements
                        taskRow.classList.toggle('table-success', isCompleted);

                        // Update status label
                        const statusLabel = taskRow.querySelector('.form-check-label');
                        if (statusLabel) {
                            statusLabel.textContent = isCompleted ? 'Completed' : 'Active';
                        }

                        // Update counters
                        updateTaskCounters();
                    }
                } else {
                    throw new Error(data.message || 'Unknown error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.checked = !isCompleted; // Revert checkbox state
                alert('Failed to update task status: ' + error.message);
            });
        });
    });

    // Task filtering
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.dataset.filter;

            // Update active button
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // Filter tasks
            const tasks = document.querySelectorAll('.task-row');
            tasks.forEach(task => {
                const isCompleted = task.querySelector('.task-completion-toggle').checked;

                if (filter === 'all' ||
                    (filter === 'active' && !isCompleted) ||
                    (filter === 'completed' && isCompleted)) {
                    task.style.display = '';
                } else {
                    task.style.display = 'none';
                }
            });
        });
    });

    // Helper function to get cookies (for CSRF token)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Function to update task counters
    function updateTaskCounters() {
        const totalTasks = document.querySelectorAll('.task-row').length;
        const completedTasks = document.querySelectorAll('.task-completion-toggle:checked').length;
        const pendingTasks = totalTasks - completedTasks;

        // Update counters in the profile card
        document.querySelectorAll('.card-footer .col-4 h5')[0].textContent = totalTasks;
        document.querySelectorAll('.card-footer .col-4 h5')[1].textContent = completedTasks;
        document.querySelectorAll('.card-footer .col-4 h5')[2].textContent = pendingTasks;
    }

    // Countdown timer for task deadlines
    function updateCountdowns() {
        document.querySelectorAll('.countdown').forEach(element => {
            const deadline = new Date(element.getAttribute('data-deadline')).getTime();
            const now = new Date().getTime();
            const distance = deadline - now;

            if (distance < 0) {
                element.innerHTML = '<span class="text-danger">Overdue</span>';
            } else {
                const days = Math.floor(distance / (1000 * 60 * 60 * 24));
                const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

                if (days > 0) {
                    element.innerHTML = days + 'd ' + hours + 'h remaining';
                } else {
                    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    element.innerHTML = hours + 'h ' + minutes + 'm remaining';
                }

                // Add warning color if deadline is near (less than 24 hours)
                if (distance < (24 * 60 * 60 * 1000)) {
                    element.classList.add('text-warning', 'fw-bold');
                }
            }
        });
    }

    // Initialize countdowns
    if (document.querySelector('.countdown')) {
        updateCountdowns();
        setInterval(updateCountdowns, 60000);
    }
});
