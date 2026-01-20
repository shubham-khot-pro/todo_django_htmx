  
        // HTMX configuration
        htmx.config.useTemplateFragments = true;
        
        // Simple function to update todo count
        function updateTodoCount() {
            const todoItems = document.querySelectorAll('#todo-items .todo-card:not(.deleted)');
            const countElement = document.getElementById('todo-count');
            if (countElement) {
                countElement.textContent = todoItems.length;
            }
        }
        
        // Update todo count when page loads
        document.addEventListener('DOMContentLoaded', function() {
            updateTodoCount();
            
            // Listen for HTMX swaps to update count
            document.body.addEventListener('htmx:afterSwap', function(evt) {
                setTimeout(updateTodoCount, 50);
            });
            
            // Listen for HTMX requests to show toasts
            document.body.addEventListener('htmx:beforeSwap', function(evt) {
                if (evt.detail.xhr.status === 400) {
                    // Show error toast
                    showToast('Error: ' + (evt.detail.xhr.responseText || 'Something went wrong'), 'danger');
                    evt.detail.shouldSwap = false;
                }
            });
        });
        
        function showToast(message, type) {
            const toast = document.createElement('div');
            toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
            toast.style.top = '20px';
            toast.style.right = '20px';
            toast.style.zIndex = '9999';
            toast.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }
    