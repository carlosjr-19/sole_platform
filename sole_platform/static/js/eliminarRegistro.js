// Abre el modal de confirmación
function openDeleteModal(contracargoId) {
    const modal = document.getElementById('deleteModal');
    modal.style.display = 'flex';

    // Establece la acción del formulario dinámicamente
    const form = document.getElementById('deleteForm');
    form.action = `/delete_contracargo/${contracargoId}`;
}

// Cierra el modal de confirmación
function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    modal.style.display = 'none';
}