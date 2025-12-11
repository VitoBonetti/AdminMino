// Function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function () {
    const categorySelect = document.getElementById('id_category_id');
    const descriptionSelect = document.getElementById('id_description_id');

    categorySelect.addEventListener('change', function () {
        const categoryId = this.value;

        if (categoryId) {
            fetchCosts(categoryId, null);
        } else {
            fetchCosts(null, null);
        }
    });

    descriptionSelect.addEventListener('change', function () {
        const descriptionId = this.value;

        if (categorySelect.value) {
            fetchCosts(categorySelect.value, descriptionId);
        } else {
            fetchCosts(null, descriptionId);
        }
    });

    function fetchCosts(categoryId, descriptionId) {
        let url = '/costs/';
        if (categoryId || descriptionId) {
            url += '?';
            if (categoryId) {
                url += `category_id=${categoryId}&`;
            }
            if (descriptionId) {
                url += `description_id=${descriptionId}`;
            }
        }

        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            },
        })
        .then(response => response.text())  // Getting the response as text
        .then(text => {
            console.log('Raw response:', text);  // Printing the raw response
            return JSON.parse(text);  // Parsing the response text as JSON
        })
        .then(data => {
            const table = document.querySelector('tbody');
            while (table.firstChild) {
                table.removeChild(table.firstChild);
            }

            data.forEach(cost => {
                const tr = document.createElement('tr');

                // Process the date
                let [year, month, day] = cost.cost_date.split("-");
                // let date = new Date(year, month - 1, day);

                // Create an array of month names
                let monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
                ];

                // convert the month string to integer and adjust the index
                month = parseInt(month) - 1;

                // Format the date
                let formattedDate = `${parseInt(day).toString().padStart(2, '0')}-${monthNames[month]}-${year}`;

                // Then re-order the date format to "day-month-year"
                formattedDate = formattedDate.split("-").reverse().join("-");


                // Process the amount
                let amountHtml = '';
                if(cost.is_credit){
                    amountHtml = `<span class="credit">€ ${cost.euro_amount}</span>`;
                }else{
                    amountHtml = `<span class="debit">€ ${cost.euro_amount}</span>`;
                }

                // Set defaults if none
                let category = cost.category || '';
                let description = cost.description || '';
                let cost_note = cost.cost_note || '';

                tr.innerHTML = `
                    <td class="align-middle">${cost.reference_id}</td>
                    <td class="align-middle">${formattedDate}</td>
                    <td class="align-middle">${category}</td>
                    <td class="align-middle">${description}</td>
                    <td class="align-middle">${amountHtml}</td>
                    <td class="align-middle">${cost_note}</td>
                    <td class="text-end align-middle">
                        <a href="/costs?id=${cost.id}" title="Edit">
                            <i class="bi bi-pencil-square fw-bold link-primary"></i>
                        </a>
                        <a href="/delete-cost/${cost.id}" class="delete-button" title="Delete"  data-company-id="${cost.id}">
                            <i class="bi bi-trash link-danger fw-bold"></i>
                        </a>
                    </td>
                `;

                table.appendChild(tr);
            });
        })
        .catch(error => console.error('Error:', error));
    }
});