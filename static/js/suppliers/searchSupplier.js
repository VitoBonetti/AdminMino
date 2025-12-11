// JavaScript for Search Functionality
document.addEventListener("DOMContentLoaded", function() {
    // Search input event listener
    document.getElementById("searchSupplier").addEventListener("keyup", function() {
        const query = this.value;
        fetch(`/suppliers/search-supplier/?q=${query}`)
            .then(response => response.json())
            .then(data => {
                updateTable(data.suppliers);
                document.getElementById("searchCount").innerText = `Results found: ${data.count}`;
            })
            .catch(error => console.error('Error fetching search data:', error));
    });
});

function updateTable(suppliers) {
    const tableBody = document.getElementById("suppliersTableBody");
    tableBody.innerHTML = ""; // Clear existing table rows

    suppliers.forEach(supplier => {
        const row = `<tr class="p-1">
            <td class="table_cell align-middle">
                <a href="javascript:void(0);" onclick="fetchSupplierDetails(${supplier.id})" class="supplier-detail-link table_link_supplier">${supplier.name}</a>
            </td>
            <td class="table_cell h3 align-middle text-end">
                <span class="ps-1 h3">
                    <a href="/update-supplier/${supplier.id}" style="text-decoration: none;">
                        <i class="bi bi-pencil-square fw-bold link-success fs-4" title="Edit"></i>
                    </a>
                </span>
                <span class="pe-1 h3">
                    <a class="delete-button" data-company-id="${supplier.id}" title="Delete">
                        <i class="bi bi-trash fw-bold link-danger fs-4" title="Delete"></i>
                    </a>
                </span>
            </td>
        </tr>`;
        tableBody.innerHTML += row;
    });
}