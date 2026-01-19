// // app.js - JavaScript utilities for todo app

// document.addEventListener('DOMContentLoaded', function() {
//     // Auto-focus on first input in forms
//     const forms = document.querySelectorAll('form');
//     forms.forEach(form => {
//         const firstInput = form.querySelector('input[type="text"], textarea');
//         if (firstInput) {
//             firstInput.focus();
//         }
//     });
    
//     // Handle escape key to close modals
//     document.addEventListener('keydown', function(e) {
//         if (e.key === 'Escape') {
//             const modals = document.querySelectorAll('.modal');
//             modals.forEach(modal => {
//                 if (modal.style.display === 'block') {
//                     modal.style.display = 'none';
//                 }
//             });
//         }
//     });
// });

// // HTMX configuration
// htmx.config.requestClass = 'htmx-request';
// htmx.config.historyEnabled = true;
// htmx.config.historyCacheSize = 10;

// // HTMX event handlers
// document.body.addEventListener('htmx:beforeRequest', function(e) {
//     // Show loading state
//     const target = e.target;
//     if (target && target.classList.contains('btn')) {
//         target.classList.add('loading');
//     }
// });

// document.body.addEventListener('htmx:afterRequest', function(e) {
//     // Remove loading state
//     const target = e.target;
//     if (target && target.classList.contains('btn')) {
//         target.classList.remove('loading');
//     }
// });

// // Infinite scroll handler
// function setupInfiniteScroll(containerSelector, triggerSelector, urlTemplate) {
//     const container = document.querySelector(containerSelector);
//     if (!container) return;
    
//     const observer = new IntersectionObserver((entries) => {
//         entries.forEach(entry => {
//             if (entry.isIntersecting) {
//                 const trigger = entry.target;
//                 const nextPage = trigger.dataset.nextPage;
//                 if (nextPage) {
//                     htmx.ajax('GET', urlTemplate.replace('{page}', nextPage), {
//                         target: containerSelector,
//                         swap: 'beforeend'
//                     });
//                     trigger.dataset.nextPage = parseInt(nextPage) + 1;
//                 }
//             }
//         });
//     });
    
//     const trigger = document.querySelector(triggerSelector);
//     if (trigger) {
//         observer.observe(trigger);
//     }
// }

// // Initialize infinite scroll on page load
// document.addEventListener('DOMContentLoaded', function() {
//     setupInfiniteScroll(
//         '#history-container',
//         '#load-more-trigger',
//         '/todos/{todo_id}/history/scroll/?page={page}'
//     );
// });