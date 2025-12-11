document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-button');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            let buttonElement = event.target.closest('.delete-button');
            const supplierId = buttonElement.dataset.companyId;
            const deleteUrl = `/suppliers/delete/${supplierId}/`;

            if (confirm('Are you sure you want to delete this record?')) {
                window.location.href = deleteUrl;
            }
        });
    });
});