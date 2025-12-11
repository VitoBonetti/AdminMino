document.addEventListener('DOMContentLoaded', (event) => {
    // Select the category select and description input
    var categorySelect = document.querySelector('#id_categoryID');
    var descriptionInput = document.querySelector('#id_description');

   // Function to update the descriptions table
    function updateDescriptionsTable(descriptions) {
        var tableBody = document.querySelector('#description-table tbody');
        tableBody.innerHTML = '';
        descriptions.forEach(function(description) {
            console.log(`Updating row for description ID ${description.id}`);  // Debug log
            var row = document.createElement('tr');
            row.dataset.descriptionId = description.id;  // Add data-description-id to the tr tag
            row.innerHTML = `
                <td class="table_cell align-middle p-1">${description.category}</td>
                <td class="table_cell align-middle p-1">${description.description}</td>
                <td class="table_cell align-middle text-end">
                    <span class="ps-1">
                        <a type="button" class="edit-button" data-description-id="{{ description.id }}" title="Edit" style="text-decoration: none;">
                            <i class="bi bi-pencil-square fw-bold link-success fs-4" title="Edit"></i>
                        </a>
                    </span>
                    <span class="pe-1">
                        <a href="{% url 'delete-description' description.id %}" class="delete-button" data-description-id="{{ description.id }}" title="Delete">
                            <i class="bi bi-trash fw-bold link-danger fs-4" title="Delete"></i>
                        </a>
                    </span>
                </td>
            `;
            tableBody.appendChild(row);
        });
    }


    // Event listeners to make requests to the server when the category or description changes
    categorySelect.addEventListener('change', function() {
        var categoryId = this.value;
        var descriptionQuery = descriptionInput.value;
        if (categoryId) {
            fetch(`/costs/descriptions/get-by-category/${categoryId}/?q=${descriptionQuery}`)
                .then(response => response.json())
                .then(updateDescriptionsTable);
        }
    });
    descriptionInput.addEventListener('input', function() {
        var categoryId = categorySelect.value;
        var descriptionQuery = this.value;
        if (categoryId) {
            fetch(`/costs/descriptions/get-by-category/${categoryId}/?q=${descriptionQuery}`)
                .then(response => response.json())
                .then(updateDescriptionsTable);
        }
    });
});