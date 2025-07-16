const hamburger = document.querySelector(".hamburger");
const navMenu = document.querySelector(".nav-menu");

// Alterna el menú y la animación de la hamburguesa
function toggleMenu() {
    hamburger.classList.toggle("active");
    navMenu.classList.toggle("active");

    // Bloquea el scroll del body cuando el menú está abierto
    if (navMenu.classList.contains("active")) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = 'auto';
    }
}

hamburger.addEventListener("click", toggleMenu);

// Cierra el menú cuando se hace clic en un enlace
document.querySelectorAll(".nav-link").forEach(n => n.addEventListener("click", () => {
    if (navMenu.classList.contains("active")) {
        toggleMenu();
    }
}));
