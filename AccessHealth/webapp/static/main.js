document.querySelectorAll('.tab-nav-btn, .next-tab-trigger').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
        // Get the active tab section—use closest .tab-pane or parent if necessary
        var activePane = btn.closest('.tab-pane');
        if (!activePane) activePane = btn.parentNode; // fallback for your structure

        var valid = true;
        var requiredFields = activePane.querySelectorAll('[required]');
        requiredFields.forEach(function(field) {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                valid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });

        // Password and confirm password match check
        var password = activePane.querySelector('#password');
        var confirmPassword = activePane.querySelector('#confirm_password');
        var pwMessage = activePane.querySelector('#pw-message') || document.getElementById('pw-message');
        if (password && confirmPassword) {
            if (password.value !== confirmPassword.value) {
                valid = false;
                password.classList.add('is-invalid');
                confirmPassword.classList.add('is-invalid');
                if (pwMessage) pwMessage.textContent = "Passwords do not match!";
                alert('Passwords do not match. Please fix before continuing.');
            } else {
                password.classList.remove('is-invalid');
                confirmPassword.classList.remove('is-invalid');
                if (pwMessage) pwMessage.textContent = "";
            }
        }

        if (!valid) {
            e.preventDefault();
            return false;
        }
        // Tab Switch: find corresponding nav tab and click for Bootstrap
        var nextTabSelector = btn.getAttribute('data-next');
        if (nextTabSelector) {
            var nextTabNav = document.querySelector('[data-bs-target="' + nextTabSelector + '"]');
            if (nextTabNav) {
                nextTabNav.click();
            }
        }
    });
});

// Live feedback for password matching in the pane
var passwordField = document.getElementById('password');
var confirmField = document.getElementById('confirm_password');
var pwMessageBox = document.getElementById('pw-message');
function updatePasswordMessage() {
    if (!passwordField.value && !confirmField.value) {
        pwMessageBox.textContent = "";
        confirmField.classList.remove('is-invalid');
    } else if (passwordField.value !== confirmField.value) {
        pwMessageBox.textContent = "Passwords do not match!";
        confirmField.classList.add('is-invalid');
    } else {
        pwMessageBox.textContent = "";
        confirmField.classList.remove('is-invalid');
    }
}
if (passwordField && confirmField && pwMessageBox) {
    passwordField.addEventListener('input', updatePasswordMessage);
    confirmField.addEventListener('input', updatePasswordMessage);
}
const passwordInput = document.getElementById('passwordInput');
        const confirmPasswordInput = document.getElementById('confirmPasswordInput');
        const submitButton = document.getElementById('submitButton');
        const confirmationMessage = document.getElementById('confirmationMessage');
        const errorMessage = document.getElementById('errorMessage');
        const closeButton = document.getElementById('closeButton');
        const closeErrorButton = document.getElementById('closeErrorButton');
        const eyeIcon1 = document.getElementById('eyeIcon1');
        const eyeIcon2 = document.getElementById('eyeIcon2');
        const errorText = document.getElementById('errorText');

        // Toggle password visibility for first field
        eyeIcon1.addEventListener('click', function() {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                eyeIcon1.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
            } else {
                passwordInput.type = 'password';
                eyeIcon1.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
            }
        });

        // Toggle password visibility for second field
        eyeIcon2.addEventListener('click', function() {
            if (confirmPasswordInput.type === 'password') {
                confirmPasswordInput.type = 'text';
                eyeIcon2.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
            } else {
                confirmPasswordInput.type = 'password';
                eyeIcon2.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
            }
        });

        // Handle form submission
        submitButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            const password = passwordInput.value;
            const confirmPassword = confirmPasswordInput.value;
            
            // Validate passwords
            const validation = validatePassword(password, confirmPassword);
            
            if (validation.isValid) {
                // Show confirmation message
                confirmationMessage.classList.add('show');
                
                // Clear inputs
                passwordInput.value = '';
                confirmPasswordInput.value = '';
            } else {
                // Show error message
                errorText.textContent = validation.message;
                errorMessage.classList.add('show');
            }
        });

        // Handle Enter key press
        confirmPasswordInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                submitButton.click();
            }
        });

        // Close confirmation message
        closeButton.addEventListener('click', function() {
            confirmationMessage.classList.remove('show');
        });

        // Close error message
        closeErrorButton.addEventListener('click', function() {
            errorMessage.classList.remove('show');
        });

        // Password validation function
        function validatePassword(password, confirmPassword) {
            // Check if passwords match
            if (password !== confirmPassword) {
                return {
                    isValid: false,
                    message: 'Passwords do not match. Please try again.'
                };
            }

            // Check minimum length (8 characters)
            if (password.length < 8) {
                return {
                    isValid: false,
                    message: 'Password must be at least 8 characters long.'
                };
            }

            // Check for at least one uppercase letter
            if (!/[A-Z]/.test(password)) {
                return {
                    isValid: false,
                    message: 'Password must include at least one capital letter.'
                };
            }

            // Check for at least one lowercase letter
            if (!/[a-z]/.test(password)) {
                return {
                    isValid: false,
                    message: 'Password must include at least one small letter.'
                };
            }

            // Check for at least one special character
            if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
                return {
                    isValid: false,
                    message: 'Password must include at least one special character.'
                };
            }

            return {
                isValid: true,
                message: 'Password is valid'
            };
        }