function initCostForm(categoryId, descriptionId) {
    const categorySelect = document.getElementById(categoryId);
    const descriptionSelect = document.getElementById(descriptionId);

    // if category is selected then fetch and display corresponding descriptions
    if (categorySelect.value) {
        fetchDescriptions(categorySelect.value);
    }

    // If description value exists (edit mode), enable the description field
    if (descriptionSelect.value) {
        descriptionSelect.disabled = false;
    }

    categorySelect.addEventListener('change', function () {
        const categoryId = this.value;

        if (categoryId) {
            // Enable the Description dropdown
            descriptionSelect.disabled = false;
            fetchDescriptions(categoryId);
        } else {
            // Disable the Description dropdown and clear its options
            descriptionSelect.disabled = true;
            descriptionSelect.innerHTML = '<option value="" class="form-control form-control-sm">---------</option>';
        }
    });

    function fetchDescriptions(categoryId) {
        fetch(`/costs/fetch-descriptions/${categoryId}/`)
            .then(response => response.json())
            .then(data => {
                let options = '<option value="" class="form-control form-control-sm">---------</option>';
                data.data.forEach(description => {
                    const isSelected = description.id == descriptionSelect.value ? 'selected' : '';
                    if (isSelected) {
                        descriptionSelect.disabled = false;
                    }
                    options += `<option value="${description.id}" ${isSelected}>${description.description}</option>`;
                });

                descriptionSelect.innerHTML = options;
            });
    }
}