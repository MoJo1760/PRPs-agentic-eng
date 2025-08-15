/**
 * JavaScript for dynamic questionnaire functionality
 */

// Questionnaire state management
let questionnaireState = {
    currentSession: null,
    currentQuestion: null,
    responses: [],
    totalQuestions: 0,
    completedQuestions: 0
};

/**
 * Initialize questionnaire functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize form validation
    initializeFormValidation();
    
    // Set up auto-save for long forms
    setupAutoSave();
});

/**
 * Enhanced form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('input', function(e) {
            validateField(e.target);
        });
        
        form.addEventListener('blur', function(e) {
            validateField(e.target);
        }, true);
    });
}

/**
 * Validate individual form fields
 */
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let message = '';
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        message = 'This field is required';
    }
    
    // Minimum length validation
    const minLength = field.getAttribute('minlength');
    if (minLength && value.length < parseInt(minLength)) {
        isValid = false;
        message = `Minimum ${minLength} characters required`;
    }
    
    // Maximum length validation
    const maxLength = field.getAttribute('maxlength');
    if (maxLength && value.length > parseInt(maxLength)) {
        isValid = false;
        message = `Maximum ${maxLength} characters allowed`;
    }
    
    // Email validation
    if (field.type === 'email' && value && !isValidEmail(value)) {
        isValid = false;
        message = 'Please enter a valid email address';
    }
    
    // Update field appearance
    updateFieldValidation(field, isValid, message);
    
    return isValid;
}

/**
 * Update field validation appearance
 */
function updateFieldValidation(field, isValid, message) {
    // Remove existing validation classes
    field.classList.remove('is-valid', 'is-invalid');
    
    // Remove existing feedback
    const existingFeedback = field.parentNode.querySelector('.invalid-feedback, .valid-feedback');
    if (existingFeedback) {
        existingFeedback.remove();
    }
    
    if (field.value.trim()) {
        if (isValid) {
            field.classList.add('is-valid');
        } else {
            field.classList.add('is-invalid');
            
            // Add error message
            const feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            feedback.textContent = message;
            field.parentNode.appendChild(feedback);
        }
    }
}

/**
 * Email validation helper
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Auto-save functionality for forms
 */
function setupAutoSave() {
    const autoSaveKey = 'prp_generator_form_data';
    const form = document.getElementById('conceptForm');
    
    if (!form) return;
    
    // Load saved data
    const savedData = localStorage.getItem(autoSaveKey);
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            populateForm(form, data);
            showAutoSaveNotification('Form data restored from previous session');
        } catch (e) {
            console.error('Error loading saved form data:', e);
        }
    }
    
    // Save data on input
    form.addEventListener('input', debounce(function() {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        localStorage.setItem(autoSaveKey, JSON.stringify(data));
        showAutoSaveNotification('Form saved automatically');
    }, 2000));
    
    // Clear saved data on successful submission
    form.addEventListener('submit', function() {
        localStorage.removeItem(autoSaveKey);
    });
}

/**
 * Populate form with saved data
 */
function populateForm(form, data) {
    for (let [key, value] of Object.entries(data)) {
        const field = form.querySelector(`[name="${key}"]`);
        if (field) {
            field.value = value;
        }
    }
}

/**
 * Show auto-save notification
 */
function showAutoSaveNotification(message) {
    // Create or update notification
    let notification = document.getElementById('autoSaveNotification');
    
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'autoSaveNotification';
        notification.className = 'alert alert-info alert-dismissible fade show position-fixed';
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 300px;';
        document.body.appendChild(notification);
    }
    
    notification.innerHTML = `
        <small>${message}</small>
        <button type="button" class="btn-close btn-close-sm" data-bs-dismiss="alert"></button>
    `;
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        if (notification && notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification && notification.parentNode) {
                    notification.remove();
                }
            }, 150);
        }
    }, 3000);
}

/**
 * Debounce function to limit API calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Enhanced question display with animations
 */
function displayQuestionWithAnimation(question, progress) {
    const questionnaireContent = document.getElementById('questionnaireContent');
    
    // Fade out current content
    questionnaireContent.style.opacity = '0';
    
    setTimeout(() => {
        displayQuestion(question, progress);
        
        // Fade in new content
        questionnaireContent.style.opacity = '1';
        questionnaireContent.classList.add('fade-in');
        
        // Scroll to question
        questionnaireContent.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Focus on input
        const firstInput = questionnaireContent.querySelector('input, textarea, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 300);
        }
    }, 300);
}

/**
 * Keyboard navigation for questionnaire
 */
document.addEventListener('keydown', function(e) {
    // Only handle keyboard navigation when questionnaire is active
    if (!document.getElementById('questionnaireSection').classList.contains('d-none')) {
        
        // Enter key to submit answer (when not in textarea)
        if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
            e.preventDefault();
            const submitButton = document.querySelector('#questionnaireContent button[onclick*="submitAnswer"]');
            if (submitButton) {
                submitButton.click();
            }
        }
        
        // Arrow keys for radio buttons
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            const radioButtons = document.querySelectorAll('input[type="radio"][name="answer"]');
            if (radioButtons.length > 0) {
                const currentIndex = Array.from(radioButtons).findIndex(radio => radio.checked);
                let nextIndex;
                
                if (e.key === 'ArrowDown') {
                    nextIndex = currentIndex < radioButtons.length - 1 ? currentIndex + 1 : 0;
                } else {
                    nextIndex = currentIndex > 0 ? currentIndex - 1 : radioButtons.length - 1;
                }
                
                radioButtons[nextIndex].checked = true;
                radioButtons[nextIndex].focus();
                e.preventDefault();
            }
        }
    }
});

/**
 * Progress tracking with visual feedback
 */
function updateProgressWithAnimation(percentage) {
    const progressBar = document.getElementById('progressBar');
    const currentWidth = parseFloat(progressBar.style.width) || 0;
    
    // Animate progress bar
    const duration = 500;
    const startTime = performance.now();
    
    function animateProgress(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const width = currentWidth + (percentage - currentWidth) * progress;
        progressBar.style.width = `${width}%`;
        
        if (progress < 1) {
            requestAnimationFrame(animateProgress);
        }
    }
    
    requestAnimationFrame(animateProgress);
    
    // Add celebration effect when completed
    if (percentage >= 100) {
        setTimeout(() => {
            progressBar.classList.add('bg-success');
            showCompletionCelebration();
        }, 600);
    }
}

/**
 * Show completion celebration
 */
function showCompletionCelebration() {
    // Create celebration overlay
    const celebration = document.createElement('div');
    celebration.className = 'position-fixed w-100 h-100';
    celebration.style.cssText = 'top: 0; left: 0; pointer-events: none; z-index: 9999;';
    
    // Add confetti or celebration animation
    celebration.innerHTML = `
        <div class="text-center" style="margin-top: 20vh;">
            <div class="display-1">🎉</div>
            <h3 class="text-success">Questionnaire Complete!</h3>
            <p class="lead">Now generating your comprehensive PRP...</p>
        </div>
    `;
    
    document.body.appendChild(celebration);
    
    // Remove after 3 seconds
    setTimeout(() => {
        celebration.remove();
    }, 3000);
}

/**
 * Enhanced error handling with user-friendly messages
 */
function handleAPIError(error, context = '') {
    console.error(`API Error ${context}:`, error);
    
    let userMessage = 'An unexpected error occurred. Please try again.';
    
    // Customize message based on error type
    if (error.message) {
        if (error.message.includes('network')) {
            userMessage = 'Network error. Please check your internet connection and try again.';
        } else if (error.message.includes('timeout')) {
            userMessage = 'Request timed out. This might take a few moments - please wait and try again.';
        } else if (error.message.includes('validation')) {
            userMessage = 'Please check your input and make sure all required fields are filled correctly.';
        } else {
            userMessage = error.message;
        }
    }
    
    showErrorNotification(userMessage, context);
}

/**
 * Show error notification
 */
function showErrorNotification(message, context = '') {
    const notification = document.createElement('div');
    notification.className = 'alert alert-danger alert-dismissible fade show position-fixed';
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 400px;';
    
    notification.innerHTML = `
        <h6 class="alert-heading">Error ${context}</h6>
        <p class="mb-2">${message}</p>
        <hr>
        <div class="d-flex justify-content-between">
            <small class="text-muted">Please try again or contact support if the problem persists.</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-hide after 10 seconds
    setTimeout(() => {
        if (notification && notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification && notification.parentNode) {
                    notification.remove();
                }
            }, 150);
        }
    }, 10000);
}

/**
 * Loading state management
 */
function setLoadingState(element, isLoading, originalText = '') {
    if (isLoading) {
        element.disabled = true;
        element.dataset.originalText = originalText || element.innerHTML;
        element.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status"></span>
            Loading...
        `;
    } else {
        element.disabled = false;
        element.innerHTML = element.dataset.originalText || originalText;
    }
}

/**
 * Smooth scrolling utility
 */
function smoothScrollTo(element, offset = 0) {
    const targetPosition = element.offsetTop - offset;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    const duration = 800;
    
    let start = null;
    
    function animation(currentTime) {
        if (start === null) start = currentTime;
        const timeElapsed = currentTime - start;
        const run = ease(timeElapsed, startPosition, distance, duration);
        
        window.scrollTo(0, run);
        
        if (timeElapsed < duration) {
            requestAnimationFrame(animation);
        }
    }
    
    function ease(t, b, c, d) {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
    }
    
    requestAnimationFrame(animation);
}

/**
 * Export questionnaire data for debugging
 */
function exportQuestionnaireData() {
    const data = {
        state: questionnaireState,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `questionnaire-data-${Date.now()}.json`;
    a.click();
    
    URL.revokeObjectURL(url);
}

// Make functions available globally for inline event handlers
window.displayQuestionWithAnimation = displayQuestionWithAnimation;
window.updateProgressWithAnimation = updateProgressWithAnimation;
window.handleAPIError = handleAPIError;
window.setLoadingState = setLoadingState;
window.smoothScrollTo = smoothScrollTo;