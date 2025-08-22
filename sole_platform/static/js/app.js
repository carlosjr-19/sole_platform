/* ...existing code... */
// Simple UI interactions: menu navigation, responsive toggle, sample form handling
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('toggleBtn');
    const sidebarClose = document.getElementById('sidebarClose');
    const menuItems = document.querySelectorAll('.menu-item[data-page]');
    const pageTitle = document.getElementById('pageTitle');
    const content = document.getElementById('content');
    const logoutBtn = document.getElementById('logoutBtn');
    const topLogout = document.getElementById('topLogout');
    const sidebarToggleInBar = document.getElementById('sidebarToggleInBar');

    // Initialize collapsed state on wide screens (icons-only)
    function applyInitialSidebarState() {
        if (window.innerWidth > 900) {
            sidebar.classList.add('collapsed');
            sidebar.classList.remove('mini');
        } else {
            // on small screens show a narrow mini bar (icons-only) instead of fully hiding
            sidebar.classList.remove('collapsed');
            sidebar.classList.add('mini');
        }
    }
    applyInitialSidebarState();
    refreshToggleVisibility();

    // reuse same toggle behaviour when pressing the in-bar toggle
    if (sidebarToggleInBar) {
        sidebarToggleInBar.addEventListener('click', () => {
            // delegate to the main toggle button logic to keep behaviour consistent
            toggleBtn.click();
        });
    }

    // update visibility of topbar toggle vs in-bar toggle after state changes
    function refreshToggleVisibility() {
        const topToggle = toggleBtn;
        const inbar = sidebarToggleInBar;
        if (!topToggle || !inbar) return;
        // when sidebar is collapsed, mini, or open, show in-bar toggle and hide topbar toggle
        if (sidebar.classList.contains('collapsed') || sidebar.classList.contains('mini') || sidebar.classList.contains('open')) {
            inbar.style.display = 'flex';
            topToggle.style.display = 'none';
        } else {
            inbar.style.display = 'none';
            topToggle.style.display = 'flex';
        }
    }

    // call refresh after initial state and on changes
    applyInitialSidebarState();
    refreshToggleVisibility();

    // Toggle sidebar on small screens
    toggleBtn.addEventListener('click', () => {
        const willOpen = !sidebar.classList.contains('open');
        if (willOpen) {
            sidebar.classList.add('open');
            // when opening, remove mini/collapsed to show full panel
            sidebar.classList.remove('collapsed', 'mini');
        } else {
            sidebar.classList.remove('open');
            // when closing, restore collapsed or mini depending on width
            if (window.innerWidth > 900) {
                sidebar.classList.add('collapsed');
                sidebar.classList.remove('mini');
            } else {
                sidebar.classList.add('mini');
                sidebar.classList.remove('collapsed');
            }
        }
        refreshToggleVisibility();
        if (window.feather) feather.replace();
    });

    // Close button inside sidebar (X)
    if (typeof sidebarClose !== 'undefined' && sidebarClose) {
        sidebarClose.addEventListener('click', () => {
            sidebar.classList.remove('open');
            if (window.innerWidth > 900) {
                sidebar.classList.add('collapsed');
                sidebar.classList.remove('mini');
            } else {
                sidebar.classList.add('mini');
                sidebar.classList.remove('collapsed');
            }
            refreshToggleVisibility();
        });
    }

    // Close sidebar if click outside (mobile)
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 900 && !sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
            console.log('probando cerrar sidebar por click fuera');
            sidebar.classList.remove('open');
            sidebar.classList.add('mini');   // <- aquí fuerza a volver al estado mini
            sidebar.classList.remove('collapsed'); // por si acaso
            refreshToggleVisibility();       // refresca botones hamburguesa / inbar
        }
    });



    // Menu navigation (loads simple placeholder content)
    menuItems.forEach(item => {
        item.addEventListener('click', (e) => {
            //e.preventDefault();
            document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');

        });
    });

    // wire top logout to same action as sidebar logout
    if (topLogout) {
        topLogout.addEventListener('click', () => {
            if (confirm('¿Cerrar sesión?')) {
                alert('Sesión cerrada (simulado).');
            }
        });
    }

    // ensure feather icons refresh (re-run after inserting header icons)
    if (window.feather) feather.replace();



    // Logout action (placeholder)
    logoutBtn.addEventListener('click', () => {
        if (confirm('¿Cerrar sesión?')) {
            // placeholder: in real app, call API / redirect
            alert('Sesión cerrada (simulado).');
        }
    });

    // ensure window resize updates visibility after recalculating state
    window.addEventListener('resize', () => {
        applyInitialSidebarState();
        refreshToggleVisibility();
    });
});