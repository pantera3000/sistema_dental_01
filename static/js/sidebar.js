// Sidebar Navigation JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const menuItems = document.querySelectorAll('.menu-item');
    const quickActionsBtn = document.querySelector('.quick-actions-btn');
    const quickActionsMenu = document.querySelector('.quick-actions-menu');
    
    // Load sidebar state from localStorage
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (sidebarCollapsed && window.innerWidth >= 1024) {
        sidebar.classList.add('collapsed');
    }
    
    // Toggle sidebar
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            if (window.innerWidth < 1024) {
                // Mobile: show/hide sidebar
                sidebar.classList.toggle('show');
                sidebarOverlay.classList.toggle('show');
            } else {
                // Desktop: collapse/expand sidebar
                sidebar.classList.toggle('collapsed');
                const isCollapsed = sidebar.classList.contains('collapsed');
                localStorage.setItem('sidebarCollapsed', isCollapsed);
            }
        });
    }
    
    // Close sidebar when clicking overlay (mobile)
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('show');
            sidebarOverlay.classList.remove('show');
        });
    }
    
    // Handle submenu toggles
    menuItems.forEach(item => {
        const submenu = item.nextElementSibling;
        
        // Check if next sibling is a submenu
        if (submenu && submenu.classList.contains('submenu')) {
            // Make the menu item clickable
            item.style.cursor = 'pointer';
            
            item.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Close other submenus
                menuItems.forEach(otherItem => {
                    const otherSubmenu = otherItem.nextElementSibling;
                    if (otherItem !== item && otherSubmenu && otherSubmenu.classList.contains('submenu')) {
                        otherItem.classList.remove('expanded');
                        otherSubmenu.classList.remove('show');
                    }
                });
                
                // Toggle current submenu
                item.classList.toggle('expanded');
                submenu.classList.toggle('show');
            });
        }
    });
    
    // Set active menu item based on current URL
    const currentPath = window.location.pathname;
    
    // Check all submenu items first
    document.querySelectorAll('.submenu-item').forEach(submenuItem => {
        if (submenuItem.getAttribute('href') === currentPath) {
            submenuItem.classList.add('active');
            
            // Expand parent submenu
            const parentSubmenu = submenuItem.closest('.submenu');
            if (parentSubmenu) {
                parentSubmenu.classList.add('show');
                
                // Find and mark parent menu item as expanded
                const parentMenuItem = parentSubmenu.previousElementSibling;
                if (parentMenuItem && parentMenuItem.classList.contains('menu-item')) {
                    parentMenuItem.classList.add('expanded', 'active');
                }
            }
        }
    });
    
    // Check direct menu items (those without submenus)
    menuItems.forEach(item => {
        const link = item.querySelector('a');
        if (link && link.getAttribute('href') === currentPath) {
            item.classList.add('active');
        }
    });
    
    // Quick Actions Button
    if (quickActionsBtn && quickActionsMenu) {
        quickActionsBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            quickActionsMenu.classList.toggle('show');
        });
        
        // Close quick actions when clicking outside
        document.addEventListener('click', function(e) {
            if (!quickActionsMenu.contains(e.target) && e.target !== quickActionsBtn) {
                quickActionsMenu.classList.remove('show');
            }
        });
    }
    
    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (window.innerWidth >= 1024) {
                // Desktop: remove mobile classes
                sidebar.classList.remove('show');
                sidebarOverlay.classList.remove('show');
                
                // Restore collapsed state from localStorage
                const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
                if (isCollapsed) {
                    sidebar.classList.add('collapsed');
                } else {
                    sidebar.classList.remove('collapsed');
                }
            } else {
                // Mobile: remove collapsed class
                sidebar.classList.remove('collapsed');
            }
        }, 250);
    });
    
    // Notifications dropdown
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationsDropdown = document.getElementById('notificationsDropdown');
    
    if (notificationBtn && notificationsDropdown) {
        notificationBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            notificationsDropdown.classList.toggle('show');
            
            // Close user dropdown if open
            const userDropdown = document.getElementById('userDropdown');
            if (userDropdown) {
                userDropdown.classList.remove('show');
            }
        });
    }
    
    // User dropdown
    const userBtn = document.getElementById('userBtn');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userBtn && userDropdown) {
        userBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
            
            // Close notifications dropdown if open
            if (notificationsDropdown) {
                notificationsDropdown.classList.remove('show');
            }
        });
    }
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (notificationsDropdown && !notificationsDropdown.contains(e.target) && e.target !== notificationBtn) {
            notificationsDropdown.classList.remove('show');
        }
        if (userDropdown && !userDropdown.contains(e.target) && e.target !== userBtn) {
            userDropdown.classList.remove('show');
        }
    });
    
    // Search functionality (basic)
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    
    if (searchInput && searchResults) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length < 2) {
                searchResults.classList.remove('show');
                return;
            }
            
            searchTimeout = setTimeout(function() {
                // TODO: Implement actual search via AJAX
                // For now, just show the dropdown
                searchResults.classList.add('show');
            }, 300);
        });
        
        searchInput.addEventListener('focus', function() {
            if (this.value.trim().length >= 2) {
                searchResults.classList.add('show');
            }
        });
        
        // Close search results when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchResults.contains(e.target) && e.target !== searchInput) {
                searchResults.classList.remove('show');
            }
        });
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K: Focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Ctrl/Cmd + B: Toggle sidebar
        if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
            e.preventDefault();
            if (sidebarToggle) {
                sidebarToggle.click();
            }
        }
        
        // Escape: Close all dropdowns and overlays
        if (e.key === 'Escape') {
            sidebar.classList.remove('show');
            sidebarOverlay.classList.remove('show');
            if (notificationsDropdown) notificationsDropdown.classList.remove('show');
            if (userDropdown) userDropdown.classList.remove('show');
            if (quickActionsMenu) quickActionsMenu.classList.remove('show');
            if (searchResults) searchResults.classList.remove('show');
        }
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '#!') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
});
