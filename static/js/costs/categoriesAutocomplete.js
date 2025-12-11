document.addEventListener("DOMContentLoaded", function() {
    const categoryInput = document.querySelector('.category-input');
    if (categoryInput) {
        let debounceTimer;

        categoryInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                fetch(`/costs/category-autocomplete/?q=${this.value}`)
                .then(response => response.json())
                .then(data => {
                    // Clear the existing options
                    const table = document.querySelector('tbody');
                    while (table.firstChild) {
                        table.removeChild(table.firstChild);
                    }

                    // Add new filtered categories
                    data.forEach(category => {
                        const tr = document.createElement('tr');
                        const td1 = document.createElement('td');
                        const td2 = document.createElement('td');
                        const td3 = document.createElement('td');

                        td1.classList.add('align-middle', 'fw-bold');
                        td1.textContent = category.category.charAt(0).toUpperCase() + category.category.slice(1);
                        td2.classList.add('align-middle', 'text-center');
                        td3.classList.add('align-middle', 'text-end');

                        const ul = document.createElement('ul');
                        category.descriptions.forEach(description => {
                            const li = document.createElement('li');
                            li.textContent = description.charAt(0).toUpperCase() + description.slice(1);
                            ul.appendChild(li);
                        });
                        td2.appendChild(ul);

                        const a1 = document.createElement('a');
                        a1.href = `/costs/categories/?id=${category.id}`;
                        a1.title = 'Edit';
                        const i1 = document.createElement('i');
                        i1.classList.add('bi', 'bi-pencil-square', 'fw-bold', 'link-success', 'fs-4');
                        a1.appendChild(i1);

                        const a2 = document.createElement('a');
                        a2.href = `/costs/categories/delete/${category.id}`;
                        a2.classList.add('delete-button');
                        a2.dataset.companyId = category.id;
                        a2.title = 'Delete';
                        const i2 = document.createElement('i');
                        i2.classList.add('bi', 'bi-trash', 'fw-bold', 'link-danger', 'fs-4');
                        a2.appendChild(i2);

                        td3.classList.add('text-end', 'align-middle');
                        td3.appendChild(a1);
                        td3.appendChild(a2);

                        tr.appendChild(td1);
                        tr.appendChild(td2);
                        tr.appendChild(td3);

                        table.appendChild(tr);
                    });
                });

            }, 300); // Delay in ms
        });
    } else {
        console.error('No input element found with the class "category-input".');
    }
});