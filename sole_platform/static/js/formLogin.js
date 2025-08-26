const togglePw = document.getElementById('togglePw');


// Toggle password visibility
togglePw.addEventListener('click', () => {
    const isHidden = password.type === 'password';
    password.type = isHidden ? 'text' : 'password';
    togglePw.textContent = isHidden ? 'Ocultar' : 'Mostrar';
    togglePw.setAttribute('aria-label', isHidden ? 'Ocultar contraseña' : 'Mostrar contraseña');
});