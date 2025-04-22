document.addEventListener('DOMContentLoaded', function () {
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
        toggle.addEventListener('change', function () {
            const taskId = this.dataset.taskId;
            const csrftoken = getCookie('csrftoken');
            const isCompleted = this.checked;
            const taskRow = document.querySelector(`#task-${taskId}`);

            // Show loading state
            const originalHTML = taskRow.innerHTML;
            taskRow.innerHTML = '<div class="text-center py-2"><div class="spinner-border spinner-border-sm" role="status"></div></div>';

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
                        // Restore task row
                        taskRow.innerHTML = originalHTML;

                        // Update task status indicator
                        const statusIndicator = taskRow.querySelector('.task-status-indicator');
                        if (statusIndicator) {
                            statusIndicator.className = `task-status-indicator status-${
                                isCompleted ? 'completed' :
                                    (new Date(taskRow.querySelector('.countdown').dataset.deadline) < new Date() ? 'overdue' : 'active')
                            }`;
                        }

                        // Update task badge
                        const statusBadge = taskRow.querySelector('.task-status-badge');
                        if (statusBadge) {
                            statusBadge.textContent = isCompleted ? 'Completed' : statusBadge.textContent;
                        }

                        // Move task to appropriate container
                        const inProgressContainer = document.querySelector('#in-progress-tasks');
                        const completedContainer = document.querySelector('#completed-tasks');
                        const emptyStateInProgress = inProgressContainer.querySelector('.empty-state');
                        const emptyStateCompleted = completedContainer.querySelector('.empty-state');

                        taskRow.remove();

                        if (isCompleted) {
                            completedContainer.insertBefore(taskRow, emptyStateCompleted);
                        } else {
                            inProgressContainer.insertBefore(taskRow, emptyStateInProgress);
                        }

                        // Update counters
                        updateTaskCounters();
                    } else {
                        throw new Error(data.message || 'Unknown error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    taskRow.innerHTML = originalHTML;
                    this.checked = !isCompleted; // Revert checkbox state
                    alert('Failed to update task status: ' + error.message);
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

    // Function to update all task counters
    function updateTaskCounters() {
        const totalTasks = document.querySelectorAll('.task-row').length;
        const completedTasks = document.querySelectorAll('.task-completion-toggle:checked').length;
        const activeTasks = totalTasks - completedTasks;

        // Update tab counters
        document.querySelector('#in-progress-counter').textContent = activeTasks;
        document.querySelector('#completed-counter').textContent = completedTasks;

        // Update stat cards
        document.querySelector('#total-tasks-counter').textContent = totalTasks;
        document.querySelector('#completed-tasks-counter').textContent = completedTasks;

        // Update progress bars
        const completedPercent = Math.round((completedTasks / totalTasks) * 100);
        const activePercent = 100 - completedPercent;

        document.querySelector('#completed-progress').style.width = `${completedPercent}%`;
        document.querySelector('#completed-progress').setAttribute('aria-valuenow', completedTasks);
        document.querySelector('#completed-progress').textContent = `${completedTasks} Completed`;

        document.querySelector('#active-progress').style.width = `${activePercent}%`;
        document.querySelector('#active-progress').setAttribute('aria-valuenow', activeTasks);
        document.querySelector('#active-progress').textContent = `${activeTasks} Active`;

        // Update badges in the list
        document.querySelector('#completed-badge').textContent = completedTasks;
        document.querySelector('#active-badge').textContent = activeTasks;
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

    // Animation for cards on scroll
    function animateOnScroll() {
        const cards = document.querySelectorAll('.card.animate-on-scroll');
        cards.forEach(card => {
            const position = card.getBoundingClientRect();
            if (position.top >= 0 && position.bottom <= window.innerHeight) {
                card.classList.add('animate__animated', 'animate__fadeInUp');
                card.classList.remove('animate-on-scroll');
            }
        });
    }

    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll();
});
