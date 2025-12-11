document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-button');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            let buttonElement = event.target.closest('.delete-button');
            const ticketId = buttonElement.dataset.supportId;
            const deleteUrl = `/support/delete/${ticketId}/`;

            if (confirm('Are you sure you want to delete this record?')) {
                window.location.href = deleteUrl;
            }
//            return false;
        });
    });
});