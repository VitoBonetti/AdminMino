document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.edit-button').forEach(button => {
        button.addEventListener('click', function() {
            const customerId = this.dataset.companyId;
            fetch(`/customers/details/${customerId}`)
                .then(response => response.json())
                .then(data => {
                    // document.querySelector('input[name="id"]').value = companyId;
                    document.querySelector('#customer_id').value = customerId;
                    document.querySelector('#id_name').value = data.name;
                    document.querySelector('#id_address').value = data.address;
                    document.querySelector('#id_postcode').value = data.postcode;
                    document.querySelector('#id_city').value = data.city;
                    document.querySelector('#id_nation').value = data.nation;
                    document.querySelector('#id_phone').value = data.phone;
                    document.querySelector('#id_email').value = data.email;
                    document.querySelector('#id_btw').value = data.btw;
                    document.querySelector('#id_kvk').value = data.kvk;
                    document.querySelector('#id_bankaccountname').value = data.bankaccountname;
                    document.querySelector('#id_iban').value = data.iban;
                    document.querySelector('#id_is_active').checked = data.is_active;
                })
                .catch(error => console.error('Error loading customer data:', error));
        });
    });
});