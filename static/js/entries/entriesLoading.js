jq(document).ready(function() {
    jq('#id_supplier_id').change(function() {
        var url = "/entries/api/get-loading-addresses/";
        var supplierId = jq(this).val();

        jq.get(url, { supplier_id: supplierId }, function(data) {
            var select = jq('#id_loading_address_id');
            select.empty();
            select.append('<option value="">----------</option>');
            data.forEach(function(row){
                var newOption = new Option(row.address, row.id, false, false);
                select.append(newOption);
            });
        });
    });
});