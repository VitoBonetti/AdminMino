document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.edit-button').forEach(button => {
        button.addEventListener('click', function() {
            const companyId = this.dataset.companyId;
            fetch(`/mycompany/details/?id=${companyId}`)
                .then(response => response.json())
                .then(data => {
                    // document.querySelector('input[name="id"]').value = companyId;
                    document.querySelector('#company_id').value = companyId;
                    document.querySelector('#id_name').value = data.name;
                    document.querySelector('#id_address').value = data.address;
                    document.querySelector('#id_postcode').value = data.postcode;
                    document.querySelector('#id_city').value = data.city;
                    document.querySelector('#id_nation').value = data.nation;
                    document.querySelector('#id_telephone').value = data.telephone;
                    document.querySelector('#id_email').value = data.email;
                    document.querySelector('#id_btw').value = data.btw;
                    document.querySelector('#id_kvk').value = data.kvk;
                    document.querySelector('#id_iban').value = data.iban;
                    document.querySelector('#id_is_active').checked = data.is_active;
                })
                .catch(error => console.error('Error loading company data:', error));
        });
    });
});