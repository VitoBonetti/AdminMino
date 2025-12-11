document.addEventListener("DOMContentLoaded", function() {
    // Search input event listener
    document.getElementById("searchCustomer").addEventListener("keyup", function() {
        const query = this.value;
        fetch(`/customers/search-customer/?q=${query}`)
            .then(response => response.json())
            .then(data => {
                console.log("received data:", data);
                updateTable(data.customers);
                document.getElementById("searchCustomerCount").innerText = `Results found: ${data.count}`;
            })
            .catch(error => console.error('Error fetching search data:', error));
    });
});

function updateTable(customers) {
    const tableBody = document.getElementById("customerTableBody");
    tableBody.innerHTML = ""; // Clear existing table rows

    customers.forEach(customer => {
        const row = document.createElement('tr');

        row.className = customer.is_active ? 'text-success' : 'text-danger';

        row.innerHTML = `
            <td class="align-middle">
                ${customer.name}
            </td>
            <td class="align-middle text-center">
                <a href="https://maps.google.com/?q=${customer.address}, ${customer.postcode} ${customer.city} ${customer.city} - ${customer.nation}" class="table_link">${customer.address}, ${customer.postcode} ${customer.city} ${customer.city} - ${customer.nation}</a>
            </td>
            <td class="align-middle text-center"><a href="mailto:${customer.email}" class="table_link">${customer.email}</a></td>
            <td class="align-middle text-center">${customer.phone}</td>
            <td class="align-middle text-center">${customer.kvk}</td>
            <td class="align-middle text-center">${customer.btw}</td>
            <td class="align-middle text-center">${customer.bankaccountname}: ${customer.iban}</td>
            <td class="align-middle text-center ${customer.is_active ? 'text-success' : 'text-danger'}">${customer.is_active ? 'True' : 'False'}</td>
            <td class="table_cell h3 align-middle text-end">
                <span class="ps-1 h3">
                    <a href="javascript:void(0)" class="edit-button" data-company-id="${customer.id}" title="Edit" data-bs-toggle="modal" data-bs-target="#customersModal" data-name="${customer.name}" data-address="${customer.address}" data-postcode="${customer.postcode}" data-city="${customer.city}" data-nation="${customer.nation}" data-phone="${customer.phone}" data-email="${customer.email}" data-btw="${customer.btw}" data-kvk="${customer.kvk}" data-accountname="${customer.bankaccountname}" data-iban="${customer.iban}" data-is_active="${customer.is_active}" style="text-decoration: none;">
                        <i class="bi bi-pencil-square fw-bold link-success fs-4" title="Edit"></i>
                    </a>
                </span>
                <span class="pe-1 h3">
                    <a class="delete-button" data-company-id="${customer.id}" title="Delete">
                        <i class="bi bi-trash fw-bold link-danger fs-4" title="Delete"></i>
                    </a>
                </span>
            </td>
        `;
        tableBody.appendChild(row);
    });

    // Bind click events to edit buttons after table update
    bindEditButtonEvents();
}

function bindEditButtonEvents() {
    document.querySelectorAll('.edit-button').forEach(button => {
        button.addEventListener('click', function() {
            const modalForm = document.querySelector('#customersModal .modal-body form');
            const attributes = this.attributes;
            Object.keys(attributes).forEach(key => {
                const attrName = attributes[key].name;
                if (attrName && attrName.startsWith('data-')) {
                    const dataKey = attrName.replace('data-', '');
                    const formField = modalForm.querySelector(`[name=${dataKey}]`);
                    if (formField) {
                        formField.value = attributes[key].value;
                    }
                }
            });
            // Special case for setting the hidden ID field for the customer
            const customerId = this.getAttribute('data-customer-id');
            const hiddenIdField = modalForm.querySelector('#customer_id');
            if (hiddenIdField) {
                hiddenIdField.value = customerId;
            }
        });
    });
}