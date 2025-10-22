document.addEventListener('DOMContentLoaded', function() {
    // --- UTILITY FUNCTIONS ---
    const getCsrfToken = () => document.querySelector('input[name=csrfmiddlewaretoken]')?.value || '';

    function showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 5000);
    }

    // --- MODAL CONTROLS ---
    const modals = {
        createThread: document.getElementById('createThreadModal'),
        editThread: document.getElementById('editThreadModal'),
        editReply: document.getElementById('editReplyModal'),
        deleteConfirm: document.getElementById('deleteConfirmModal'),
        addReply: document.getElementById('replyModal'),
    };
    function showModal(modal) { if (modal) modal.style.display = 'flex'; }
    function hideModal(modal) { if (modal) modal.style.display = 'none'; }
    document.querySelectorAll('.modal-close, .cancel-delete-btn').forEach(btn => btn.onclick = () => hideModal(btn.closest('.modal-overlay')));
    window.onclick = (event) => { if (event.target.classList.contains('modal-overlay')) hideModal(event.target); };

    // --- EVENT DELEGATION FOR ALL CLICKS ---
    document.body.addEventListener('click', async function(e) {
        const target = e.target;
        const csrfToken = getCsrfToken();

        if (target.id === 'openCreateThreadModalBtn') {
            showModal(modals.createThread);
        }

        const replyToBtn = target.closest('.reply-to-btn');
        if (replyToBtn) {
            e.preventDefault();
            const parentId = replyToBtn.dataset.parentId || '';
            modals.addReply.querySelector('#parent-reply-id').value = parentId;
            modals.addReply.querySelector('#reply-modal-title').textContent = parentId ? 'Balas Komentar Ini' : 'Tulis Balasan untuk Thread';
            showModal(modals.addReply);
        }

        const editThreadBtn = target.closest('.edit-thread-btn');
        if (editThreadBtn) {
            e.preventDefault();
            const threadId = editThreadBtn.dataset.threadId;
            modals.editThread.querySelector('#edit-thread-id').value = threadId;
            modals.editThread.querySelector('#edit-thread-title').value = editThreadBtn.dataset.title;
            modals.editThread.querySelector('#edit-thread-content').value = editThreadBtn.dataset.content;
            showModal(modals.editThread);
        }

        const editReplyBtn = target.closest('.edit-reply-btn');
        if (editReplyBtn) {
            e.preventDefault();
            const replyId = editReplyBtn.dataset.replyId;
            modals.editReply.querySelector('#edit-reply-id').value = replyId;
            modals.editReply.querySelector('#edit-reply-content').value = editReplyBtn.dataset.content;
            showModal(modals.editReply);
        }

        // Open "Delete Confirmation" Modal
        const deleteBtn = target.closest('.delete-thread-btn, .delete-reply-btn');
        if (deleteBtn) {
            e.preventDefault();
            const id = deleteBtn.dataset.threadId || deleteBtn.dataset.replyId;
            const type = deleteBtn.classList.contains('delete-thread-btn') ? 'thread' : 'reply';
            const confirmBtn = modals.deleteConfirm.querySelector('#confirm-delete-btn');
            confirmBtn.dataset.id = id;
            confirmBtn.dataset.type = type;
            showModal(modals.deleteConfirm);
        }

        if (target.id === 'confirm-delete-btn') {
            const id = target.dataset.id;
            const type = target.dataset.type;
            const url = type === 'thread' ? `/community/thread/${id}/delete/` : `/community/reply/${id}/delete/`;
            const response = await fetch(url, { method: 'POST', headers: {'X-CSRFToken': csrfToken} });
            if (response.ok) {
                const elementToRemove = document.getElementById(`${type}-${id}`);
                if (elementToRemove) elementToRemove.remove();
                showToast(`${type.charAt(0).toUpperCase() + type.slice(1)} berhasil dihapus.`, 'success');
            } else { showToast(`Gagal menghapus ${type}.`, 'error'); }
            hideModal(modals.deleteConfirm);
        }

    });

    // --- FORM SUBMISSIONS (AJAX) ---
    const createThreadForm = document.getElementById('create-thread-form');
    if (createThreadForm) {
        createThreadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const response = await fetch(this.action, { method: 'POST', body: formData, headers: {'X-CSRFToken': getCsrfToken()} });
            if (response.ok) {
                const data = await response.json();
                document.getElementById('thread-list-container').insertAdjacentHTML('afterbegin', data.html_card);
                if (document.getElementById('no-threads-yet')) document.getElementById('no-threads-yet').remove();
                this.reset();
                hideModal(modals.createThread);
                showToast('Thread berhasil dibuat!', 'success');
            } else { showToast('Gagal membuat thread.', 'error'); }
        });
    }

    const addReplyForm = document.getElementById('reply-form-modal');
    if (addReplyForm) {
        addReplyForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const content = this.querySelector('textarea').value;
            const parentId = this.querySelector('#parent-reply-id').value;
            const response = await fetch(this.dataset.url, {
                method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken()},
                body: JSON.stringify({ content, parent_id: parentId }),
            });
            if (response.ok) {
                const data = await response.json();
                if (document.getElementById('no-replies-yet')) document.getElementById('no-replies-yet').remove();
                let container = data.parent_id ? document.getElementById(`children-of-${data.parent_id}`) : document.getElementById('reply-section');
                container.insertAdjacentHTML('beforeend', data.html_reply);
                this.reset();
                hideModal(modals.addReply);
                showToast('Balasan berhasil dikirim!', 'success');
            } else { showToast('Gagal mengirim balasan.', 'error'); }
        });
    }

    const editThreadForm = document.getElementById('edit-thread-form');
    if (editThreadForm) {
        editThreadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const id = this.querySelector('#edit-thread-id').value;
            const title = this.querySelector('#edit-thread-title').value;
            const content = this.querySelector('#edit-thread-content').value;
            const response = await fetch(`/community/thread/${id}/edit/`, {
                method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken()},
                body: JSON.stringify({ title, content }),
            });
            if (response.ok) {
                const data = await response.json();
                const card = document.getElementById(`thread-${id}`);
                card.querySelector('.post-header h3 a').textContent = data.title;
                card.querySelector('.post-body p').textContent = data.content;
                const editBtn = card.querySelector('.edit-thread-btn');
                editBtn.dataset.title = data.title;
                editBtn.dataset.content = data.content;
                hideModal(modals.editThread);
                showToast('Thread berhasil diperbarui.', 'success');
            } else { showToast('Gagal memperbarui thread.', 'error'); }
        });
    }

    const editReplyForm = document.getElementById('edit-reply-form');
    if (editReplyForm) {
        editReplyForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const id = this.querySelector('#edit-reply-id').value;
            const content = this.querySelector('#edit-reply-content').value;
            const response = await fetch(`/community/reply/${id}/edit/`, {
                method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken()},
                body: JSON.stringify({ content }),
            });
            if (response.ok) {
                const data = await response.json();
                const contentP = document.querySelector(`#reply-${id} .reply-content p`);
                if (contentP) contentP.textContent = data.content;
                const editBtn = document.querySelector(`#reply-${id} .edit-reply-btn`);
                if(editBtn) editBtn.dataset.content = data.content;
                hideModal(modals.editReply);
                showToast('Balasan berhasil diperbarui.', 'success');
            } else { showToast('Gagal memperbarui balasan.', 'error'); }
        });
    }

    const replySortSelect = document.getElementById('reply-sort-select');
    if (replySortSelect) {
        replySortSelect.addEventListener('change', function() {
            const sortBy = this.value;
            const replySection = document.getElementById('reply-section');
            const replies = Array.from(replySection.children).filter(el => el.classList.contains('reply-card'));
            replies.sort((a, b) => {
                if (sortBy === 'oldest') {
                    return parseInt(a.dataset.timestamp, 10) - parseInt(b.dataset.timestamp, 10);
                } else {
                    return parseInt(b.dataset.timestamp, 10) - parseInt(a.dataset.timestamp, 10);
                }
            });
            replies.forEach(reply => replySection.appendChild(reply));
        });
    }
});