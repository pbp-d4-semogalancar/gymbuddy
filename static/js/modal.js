document.addEventListener('DOMContentLoaded', () => {
    const genericModal = document.getElementById('generic-modal');
    const modalContentTarget = document.getElementById('modal-content-target');
    
    if (!genericModal || !modalContentTarget) {
        console.warn("Modal shell atau modal content target tidak ditemukan di halaman ini.");
        return;
    }
    
    const closeModal = () => {
        genericModal.classList.add('hidden');
        modalContentTarget.innerHTML = '';
    }

    document.body.addEventListener('click', (event) => {
        const button = event.target.closest('[data-modal-target]');
        if (button) {
            const modalId = button.getAttribute('data-modal-target');
            const modal = document.querySelector(modalId);
            if (modal) {
                modal.classList.remove('hidden');
            }
        }
    });

    genericModal.addEventListener('click', (event) => {
        if (event.target.classList.contains('modal-close') || event.target.classList.contains('modal')) {
            closeModal();
        }
    });

    
    document.body.addEventListener('click', async (event) => {
        const button = event.target.closest('[data-load-url]');
        if (button) {
            const url = button.getAttribute('data-load-url');
            
            modalContentTarget.innerHTML = '<p class="p-6 text-center text-gray-600">Loading form...</p>';
            genericModal.classList.remove('hidden');
            try {
                const response = await fetch(url);
                if (!response.ok) throw new Error('Network response was not ok');
                
                const html = await response.text();
                modalContentTarget.innerHTML = html; 
                
            } catch (error) {
                modalContentTarget.innerHTML = '<p class="p-6 text-red-500">Gagal memuat konten. Coba lagi.</p>';
                console.error('Fetch error:', error);
            }
        }
    });
    

    
    genericModal.addEventListener('submit', async (event) => {
        // Cek apakah event berasal dari <form>
        if (event.target.tagName === 'FORM') { 
            event.preventDefault(); 
            
            const form = event.target;
            const url = form.action;
            const method = form.method;
            const formData = new FormData(form);

            try {
                const response = await fetch(url, {
                    method: method,
                    body: formData,
                    headers: {

                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    }
                });
                const data = await response.json();

                if (response.ok) {
                    window.showToast(data.message || 'Operasi berhasil!', 'success');
                    const successEvent = new CustomEvent('modal:success', {
                        bubbles: true, 
                        detail: { response: data, form: form }
                    });
                    form.dispatchEvent(successEvent);
                    if (!successEvent.defaultPrevented) {
                        closeModal();
                    }

                } else {
                     const errorEvent = new CustomEvent('modal:error', {
                         bubbles: true,
                         detail: { error: data, form: form, status: response.status }
                     });
                     form.dispatchEvent(errorEvent);
                    window.showToast(data.message || 'Terjadi error.', 'error');
                }
            } catch (error) {
                console.error('Form submission error:', error);
                window.showToast('Tidak bisa terhubung ke server.', 'error');
            }
        }
    });
});