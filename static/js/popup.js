function showToast(message = "Product added to cart") {
    const toastEl = document.getElementById('cartToast');
    if (!toastEl) return;

    toastEl.querySelector('.toast-body').textContent = message;

    // Bootstrap 4/5 toast
    const toast = new bootstrap.Toast(toastEl, {
        delay: 4000  // auto hide after 4s
    });
    toast.show();
}