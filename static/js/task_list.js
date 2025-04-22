document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Clear filters button
    document.getElementById('clear-filters').addEventListener('click', function() {
        const form = document.getElementById('task-filter-form');
        form.reset();
        form.submit();
    });

    // Task completion toggle functionality
    document.querySelectorAll('.task-completion-toggle').forEach(toggle => {
        toggle.addEventListener('change', function() {
            const taskId = this.dataset.taskId;
            const csrftoken = getCookie('csrftoken');
            const isCompleted = this.checked;
            const taskRow = document.querySelector(`#task-${taskId}`);
            const statusLabel = taskRow.querySelector('.form-check-label');

            // Show loading state
            const originalHTML = taskRow.innerHTML;
            taskRow.innerHTML = '<td colspan="6" class="text-center py-2"><div class="spinner-border spinner-border-sm" role="status"></div></td>';

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

                    // Update row styling
                    taskRow.classList.remove('table-success', 'table-danger');
                    if (isCompleted) {
                        taskRow.classList.add('table-success');
                    } else {
                        const deadline = new Date(taskRow.querySelector('.countdown').dataset.deadline);
                        if (deadline < new Date()) {
                            taskRow.classList.add('table-danger');
                        }
                    }

                    // Update status label
                    if (statusLabel) {
                        statusLabel.textContent = isCompleted ? 'Completed' : 'Active';
                    }

                    // If filtered by status, reload the page to reflect changes
                    const statusFilter = document.querySelector('select[name="status"]').value;
                    if (statusFilter && ((statusFilter === 'active' && isCompleted) ||
                                        (statusFilter === 'completed' && !isCompleted))) {
                        window.location.reload();
                    }
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

    // Countdown timer for task deadlines
    function updateCountdowns() {
        document.querySelectorAll('.countdown').forEach(element => {
            const deadline = new Date(element.getAttribute('data-deadline')).getTime();
            const now = new Date().getTime();
            const distance = deadline - now;
            const taskRow = element.closest('.task-row');

            if (distance < 0) {
                element.innerHTML = '<span class="text-danger">Overdue</span>';
                if (!taskRow.classList.contains('table-success')) {
                    taskRow.classList.add('table-danger');
                }
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
