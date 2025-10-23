document.addEventListener('DOMContentLoaded', () => {
    
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    const toastIcon = document.getElementById('toast-icon');
    const toastClose = document.getElementById('toast-close');
    
    let toastTimeout; 

    const hideToast = () => {
        if (toast) {
            toast.classList.add('opacity-0', 'translate-x-10');
            setTimeout(() => {
                toast.classList.add('hidden');
                toast.classList.remove('bg-green-500', 'bg-red-500', 'text-white');
            }, 300); 
        }
    };

    if (toastClose) {
        toastClose.addEventListener('click', () => {
            clearTimeout(toastTimeout); 
            hideToast();
        });
    }

    window.showToast = (message, type = 'success') => {
        if (!toast || !toastMessage || !toastIcon) return;

        clearTimeout(toastTimeout);

        toastMessage.textContent = message;
        
        toast.classList.remove('bg-green-500', 'bg-red-500', 'text-white', 'hidden', 'opacity-0', 'translate-x-10');

        if (type === 'success') {
            toast.classList.add('bg-green-500', 'text-white');
            toastIcon.textContent = '✓';
        } else if (type === 'error') {
            toast.classList.add('bg-red-500', 'text-white');
            toastIcon.textContent = '✗';
        }
        
        // Tampilkan toast dengan animasi
        toast.classList.remove('hidden');
        setTimeout(() => {
            toast.classList.remove('opacity-0', 'translate-x-10');
        }, 10); 
        toastTimeout = setTimeout(hideToast, 3000);
    }
});