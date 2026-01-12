/* Main JavaScript for Problem Solver Platform */

// Initialize Bootstrap tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    tooltipList.forEach(function (tooltip) {
        tooltip.show();
    });
});

// Form validation helpers
function validateProblemForm() {
    const title = document.getElementById('title');
    const description = document.getElementById('description');
    
    if (!title.value.trim()) {
        title.classList.add('is-invalid');
        return false;
    } else {
        title.classList.remove('is-invalid');
    }
    
    if (!description.value.trim()) {
        description.classList.add('is-invalid');
        return false;
    } else {
        description.classList.remove('is-invalid');
    }
    
    return title.value.trim() && description.value.trim();
}

// AJAX helpers
function submitForm(formId, url, successCallback) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Submitting...';
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrf_token')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (successCallback) successCallback(data);
            showFlashMessage('success', data.message);
        } else {
            showFlashMessage('error', data.message);
        }
    })
    .catch(error => {
        showFlashMessage('error', 'An error occurred. Please try again.');
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-send"></i> Submit';
    });
}

// Flash message system
function showFlashMessage(type, message) {
    const alertContainer = document.getElementById('flash-container') || createFlashContainer();
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function createFlashContainer() {
    let container = document.getElementById('flash-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'flash-container';
        container.className = 'container mt-3';
        document.querySelector('main').prepend(container);
    }
    return container;
}

// Cookie helper
function getCookie(name) {
    const value = `; ${document.cookie}`.match(`(^|; )${name}=([^;]*)`);
    return value ? value[2].split(',').shift().trim() : null;
}

// Vote handling
function handleVote(solutionId, voteType) {
    const voteUrl = `/api/solutions/${solutionId}/vote`;
    
    submitForm(`vote-form-${solutionId}`, voteUrl, (data) => {
        if (data.success) {
            updateVoteDisplay(solutionId, data.vote_score);
            showFlashMessage('success', data.message);
        }
    });
}

function updateVoteDisplay(solutionId, voteScore) {
    const voteElements = document.querySelectorAll(`[data-solution-id="${solutionId}"] .vote-display`);
    voteElements.forEach(element => {
        element.textContent = voteScore;
        element.className = voteScore > 0 ? 'badge bg-success' : 'badge bg-danger';
    });
}

// Search functionality
function searchProblems() {
    const query = document.getElementById('search-input').value;
    const filters = getActiveFilters();
    
    const params = new URLSearchParams({
        q: query,
        ...filters
    });
    
    window.location.href = `/problems/search?${params.toString()}`;
}

function getActiveFilters() {
    const filters = {};
    const activeFilterElements = document.querySelectorAll('.filter-option:checked');
    
    activeFilterElements.forEach(element => {
        filters[element.name] = element.value;
    });
    
    return filters;
}

// Page navigation with history
function navigateToPage(page) {
    const url = new URL(window.location);
    url.searchParams.set('page', page);
    window.location.href = url.toString();
}

// Infinite scroll for problem lists
function loadMoreProblems() {
    const currentPage = getCurrentPage();
    navigateToPage(currentPage + 1);
}

function getCurrentPage() {
    const urlParams = new URLSearchParams(window.location.search);
    return parseInt(urlParams.get('page')) || 1;
}