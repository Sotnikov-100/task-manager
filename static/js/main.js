document.addEventListener('DOMContentLoaded', function() {
  // Enable all tooltips
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
  });
// Auto-hide alerts after 5 seconds
  setTimeout(function() {
    var alerts = document.querySelectorAll('.alert:not(.alert-important)');
    alerts.forEach(function(alert) {
      var bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    });
  }, 5000);

  // Add animation effects to cards when they come into view
  function animateOnScroll() {
    var cards = document.querySelectorAll('.card.animate-on-scroll');

    cards.forEach(function(card) {
      var position = card.getBoundingClientRect();

      // Check if card is in viewport
      if(position.top >= 0 && position.bottom <= window.innerHeight) {
        card.classList.add('animate__animated', 'animate__fadeInUp');
        card.classList.remove('animate-on-scroll');
      }
    });
  }

  // Run on scroll
  window.addEventListener('scroll', animateOnScroll);
  // Run once on page load
  animateOnScroll();

  // Task completion toggle - UPDATED VERSION
  document.querySelectorAll('.task-completion-toggle').forEach(function(toggle) {
    toggle.addEventListener('change', function() {
      const taskId = this.dataset.taskId;
      const csrftoken = getCookie('csrftoken');
      const isCompleted = this.checked;

      fetch(`/tasks/task/${taskId}/toggle-complete/`, {
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
          // Update UI without full page reload
          const taskRow = document.querySelector(`#task-${taskId}`);
          if (taskRow) {
            taskRow.classList.toggle('table-success', isCompleted);

            // Update status badge if exists
            const statusBadge = taskRow.querySelector('.task-status-badge');
            if (statusBadge) {
              statusBadge.textContent = isCompleted ? 'Completed' : 'In Progress';
              statusBadge.className = `badge ${isCompleted ? 'bg-success' : 'bg-warning'}`;
            }
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

  // Task filter form functionality
  const filterForm = document.getElementById('task-filter-form');
  if (filterForm) {
    const clearFiltersBtn = document.getElementById('clear-filters');

    clearFiltersBtn.addEventListener('click', function(e) {
      e.preventDefault();
      const inputs = filterForm.querySelectorAll('input, select');
      inputs.forEach(input => {
        if (input.type !== 'submit') {
          input.value = '';
        }
      });
      filterForm.submit();
    });
  }

  // Countdown timer for task deadlines
  function updateCountdowns() {
    const countdownElements = document.querySelectorAll('.countdown');

    countdownElements.forEach(element => {
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

  // Update countdowns every minute
  if (document.querySelector('.countdown')) {
    updateCountdowns();
    setInterval(updateCountdowns, 60000);
  }
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

// Document upload modal handler (NEW)
function setupDocumentUpload() {
  const uploadModal = document.getElementById('documentUploadModal');
  if (uploadModal) {
    const form = uploadModal.querySelector('form');
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const formData = new FormData(form);

      fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        }
      })
      .then(response => {
        if (response.ok) {
          window.location.reload();
        } else {
          throw new Error('Upload failed');
        }
      })
      .catch(error => {
        alert('Error uploading document: ' + error.message);
      });
    });
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', setupDocumentUpload);
