// Main JavaScript for Prime Lands Ltd

document.addEventListener('DOMContentLoaded', function() {
    // Toast notifications - auto-dismiss
    var toasts = document.querySelectorAll('.toast-notification');
    toasts.forEach(function(toast) {
        setTimeout(function() {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.5s ease';
            setTimeout(function() { toast.remove(); }, 500);
        }, 5000);
        toast.addEventListener('click', function() {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(function() { toast.remove(); }, 300);
        });
    });

    // Add smooth scroll to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// Installment calculator
function calculateInstallment(price) {
    var deposit = parseFloat(document.getElementById('calc-deposit').value) || 0;
    var months = parseInt(document.getElementById('calc-months').value) || 1;
    var balance = price - deposit;
    var monthly = months > 0 ? balance / months : 0;

    document.getElementById('calc-balance').textContent = 'KSh ' + balance.toLocaleString();
    document.getElementById('calc-monthly').textContent = 'KSh ' + Math.round(monthly).toLocaleString();
    document.getElementById('calc-result').classList.remove('hidden');
}

// Confirmation dialogs
function confirmAction(message) {
    return confirm(message || 'Are you sure?');
}

// Live search filter
function filterTable(inputId, tableId) {
    var input = document.getElementById(inputId);
    var filter = input.value.toLowerCase();
    var table = document.getElementById(tableId);
    var rows = table.getElementsByTagName('tr');

    for (var i = 1; i < rows.length; i++) {
        var text = rows[i].textContent.toLowerCase();
        rows[i].style.display = text.indexOf(filter) > -1 ? '' : 'none';
    }
}

// Sidebar toggle for mobile
function toggleSidebar(sidebarId, overlayId) {
    var sidebar = document.getElementById(sidebarId);
    var overlay = document.getElementById(overlayId);
    if (sidebar) {
        sidebar.classList.toggle('-translate-x-full');
        sidebar.classList.toggle('translate-x-0');
    }
    if (overlay) {
        overlay.classList.toggle('hidden');
    }
}

// Mobile menu - close on link click
document.addEventListener('DOMContentLoaded', function() {
    var mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenu) {
        mobileMenu.querySelectorAll('a').forEach(function(link) {
            link.addEventListener('click', function() {
                mobileMenu.classList.add('hidden');
            });
        });
    }
});
