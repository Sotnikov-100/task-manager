document.addEventListener('DOMContentLoaded', function() {
  // Enable all tooltips
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
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

  // Task completion toggle
  var completionToggles = document.querySelectorAll('.task-completion-toggle');
  completionToggles.forEach(function(toggle) {
    toggle.addEventListener('change', function() {
      var taskId = this.getAttribute('data-task-id');
      var isCompleted = this.checked;

      // Submit via fetch API
      fetch('/tasks/toggle-completion/' + taskId + '/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
          is_completed: isCompleted
        })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Update UI
          var taskElement = document.querySelector('#task-' + taskId);
          if (isCompleted) {
            taskElement.classList.add('completed-task');
          } else {
            taskElement.classList.remove('completed-task');
          }
        }
      });
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
