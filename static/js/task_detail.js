document.addEventListener('DOMContentLoaded', function () {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Task completion toggle functionality
    const completionToggle = document.querySelector('.task-completion-toggle');
    if (completionToggle) {
        completionToggle.addEventListener('change', function () {
            const taskId = this.dataset.taskId;
            const csrftoken = getCookie('csrftoken');
            const isCompleted = this.checked;
            const statusIndicator = document.querySelector('.task-status-indicator');
            const statusBadge = document.getElementById('task-status-badge');
            const progressBar = document.getElementById('deadline-progress');
            const toggleLabel = document.querySelector('label[for="complete-task-' + taskId + '"]');

            // Show loading state
            const originalHTML = this.outerHTML;
            this.outerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div>';

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
                        // Restore toggle
                        document.querySelector('.form-check-input').outerHTML = originalHTML;

                        // Update status indicator
                        if (statusIndicator) {
                            statusIndicator.className = `task-status-indicator status-${
                                isCompleted ? 'completed' :
                                    (new Date(document.querySelector('.countdown').dataset.deadline) < new Date() ? 'overdue' : 'active')
                            }`;
                        }

                        // Update status badge
                        if (statusBadge) {
                            statusBadge.textContent = isCompleted ? 'Completed' : 'In Progress';
                            statusBadge.className = `badge ${isCompleted ? 'bg-success' : 'bg-warning'}`;
                        }

                        // Update progress bar
                        if (progressBar) {
                            progressBar.style.width = isCompleted ? '100%' : '50%';
                            progressBar.style.backgroundColor = isCompleted ? '#198754' : '#0d6efd';
                        }

                        // Update toggle label
                        if (toggleLabel) {
                            toggleLabel.textContent = `Mark as ${isCompleted ? 'incomplete' : 'complete'}`;
                        }

                        // Show success message
                        showToast('Task status updated successfully', 'success');
                    } else {
                        throw new Error(data.message || 'Unknown error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.querySelector('.form-check-input').outerHTML = originalHTML;
                    completionToggle.checked = !isCompleted; // Revert checkbox state
                    showToast('Failed to update task status: ' + error.message, 'danger');
                });
        });
    }

    // Countdown timer for task deadline
    function updateCountdown() {
        const countdownElement = document.querySelector('.countdown');
        if (!countdownElement) return;

        const deadline = new Date(countdownElement.getAttribute('data-deadline')).getTime();
        const now = new Date().getTime();
        const distance = deadline - now;
        const progressBar = document.getElementById('deadline-progress');
        const statusIndicator = document.querySelector('.task-status-indicator');

        if (distance < 0) {
            countdownElement.innerHTML = '<span class="text-danger">Overdue</span>';
            if (progressBar && !document.querySelector('.task-completion-toggle').checked) {
                progressBar.style.backgroundColor = '#dc3545';
            }
            if (statusIndicator && !document.querySelector('.task-completion-toggle').checked) {
                statusIndicator.className = 'task-status-indicator status-overdue me-2';
            }
        } else {
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

            if (days > 0) {
                countdownElement.innerHTML = days + 'd ' + hours + 'h remaining';
            } else {
                const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                countdownElement.innerHTML = hours + 'h ' + minutes + 'm remaining';
            }

            // Add warning color if deadline is near (less than 24 hours)
            if (distance < (24 * 60 * 60 * 1000)) {
                countdownElement.classList.add('text-warning', 'fw-bold');
            }

            // Update progress bar if not completed
            if (progressBar && !document.querySelector('.task-completion-toggle').checked) {
                const totalTime = new Date(countdownElement.dataset.deadline) - new Date("{{ task.created_at|date:'c' }}");
                const timePassed = now - new Date("{{ task.created_at|date:'c' }}");
                const progressPercent = Math.min(100, Math.round((timePassed / totalTime) * 100));
                progressBar.style.width = `${progressPercent}%`;
            }
        }
    }

    // Initialize countdown
    updateCountdown();
    setInterval(updateCountdown, 60000);

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

    // Function to show toast notifications
    function showToast(message, type) {
        const toastContainer = document.createElement('div');
        toastContainer.className = `toast align-items-center text-white bg-${type} border-0 show`;
        toastContainer.setAttribute('role', 'alert');
        toastContainer.setAttribute('aria-live', 'assertive');
        toastContainer.setAttribute('aria-atomic', 'true');
        toastContainer.style.position = 'fixed';
        toastContainer.style.bottom = '20px';
        toastContainer.style.right = '20px';
        toastContainer.style.zIndex = '9999';

        toastContainer.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        document.body.appendChild(toastContainer);

        setTimeout(() => {
            toastContainer.classList.remove('show');
            setTimeout(() => toastContainer.remove(), 150);
        }, 3000);
    }
});

$(document).on('submit', '#relationship-form', function(e) {
    e.preventDefault();
    $.ajax({
        type: 'POST',
        url: $(this).attr('action'),
        data: $(this).serialize(),
        success: function(response) {
            location.reload();
        }
    });
});
