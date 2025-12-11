$(document).ready(function(){
    $('#year-select').change(function(){
        var year = $(this).val();
        if(year) {
            $.getJSON("{% url 'fetch_quarters' %}", {'year': year}, function(data){
                var quarterSelect = $('#quarter-select');
                quarterSelect.empty().append('<option value="">--Select Quarter--</option>');
                $.each(data, function(index, quarter){
                    quarterSelect.append('<option value="'+quarter.quarter+'">'+quarter.name+'</option>');
                });
                quarterSelect.prop('disabled', false);
            });
        } else {
            $('#quarter-select').prop('disabled', true).empty().append('<option value="">--Select Quarter--</option>');
            $('#tax-data').empty();
        }
    });

    $('#quarter-select').change(function(){
        var year = $('#year-select').val();
        var quarter = $(this).val();
        if(year && quarter) {
            $.getJSON("{% url 'fetch_tax_data' %}", {'year': year, 'quarter': quarter}, function(data){
                $('#tax-data').html(`
                    <div class="row mt-3">
                    <div class="col-xl-1 col-md-6 mb-4">&nbsp;</div>
                    <div class="col-xl-2 col-md-6 mb-4">
                    <div class="card border border-bottom-0 border-top-0 border-end-0 border-5 border-warning bg-warning-subtle shadow h-80 py-2">
                    <div class="card-body">
                    <div class="row no-gutters align-items-center">
                    <div class="col">
                    <div class="h5 text-secondary fw-bold text-uppercase mb-1">Real Cost</div>
                    <div class="h4 mb-0 font-weight-bold text-gray-800">${data.basic_cost}<i class="bi bi-currency-euro h4 text-gray-800"></i></div>
                    </div></div></div></div></div>
                    <div class="col-xl-2 col-md-6 mb-4">
                    <div class="card border border-bottom-0 border-top-0 border-end-0 border-5 border-warning bg-warning-subtle shadow h-80 py-2">
                    <div class="card-body">
                    <div class="row no-gutters align-items-center">
                    <div class="col">
                    <div class="h5 text-secondary fw-bold text-uppercase mb-1">Bank Interest</div>
                    <div class="h4 mb-0 font-weight-bold text-gray-800">${data.bank_interest}<i class="bi bi-currency-euro h4 text-gray-800"></i></div>
                    </div></div></div></div></div>
                    <div class="col-xl-2 col-md-6 mb-4">
                    <div class="card border border-bottom-0 border-top-0 border-end-0 border-5 border-warning bg-warning-subtle shadow h-80 py-2">
                    <div class="card-body">
                    <div class="row no-gutters align-items-center">
                    <div class="col">
                    <div class="h5 text-secondary fw-bold text-uppercase mb-1">Taxes</div>
                    <div class="h4 mb-0 font-weight-bold text-gray-800">${data.total_tax}<i class="bi bi-currency-euro h4 text-gray-800"></i></div>
                    </div></div></div></div></div>
                    <div class="col-xl-2 col-md-6 mb-4">
                    <div class="card border border-bottom-0 border-top-0 border-end-0 border-5 border-warning bg-warning-subtle shadow h-80 py-2">
                    <div class="card-body">
                    <div class="row no-gutters align-items-center">
                    <div class="col">
                    <div class="h5 text-secondary fw-bold text-uppercase mb-1">Salaries</div>
                    <div class="h4 mb-0 font-weight-bold text-gray-800">${data.total_salary}<i class="bi bi-currency-euro h4 text-gray-800"></i></div>
                    </div></div></div></div></div>
                    <div class="col-xl-2 col-md-6 mb-4">
                    <div class="card border border-bottom-0 border-top-0 border-end-0 border-5 border-warning bg-warning-subtle shadow h-80 py-2">
                    <div class="card-body">
                    <div class="row no-gutters align-items-center">
                    <div class="col">
                    <div class="h5 text-secondary fw-bold text-uppercase mb-1">Total Entries</div>
                    <div class="h4 mb-0 font-weight-bold text-gray-800">${data.entry_data}<i class="bi bi-currency-euro h4 text-gray-800"></i></div>
                    </div></div></div></div></div>
                    <div class="col-xl-1 col-md-6 mb-4">&nbsp;</div>
                    </div>
                    <div class="row mt-3">
                    <div class="col-xl-1 col-md-6 mb-4">&nbsp;</div>
                    <div class="col-xl-2 col-md-6 mb-4">
                    <div class="card border border-bottom-0 border-top-0 border-end-0 border-5 border-info bg-info-subtle shadow h-100 py-2">
                    <div class="card-body">
                    <div class="row no-gutters align-items-center">
                    <div class="col">
                    <div class="h5 text-secondary fw-bold text-uppercase mb-1">Step 1</div>
                    <div class="h6 mb-0 font-weight-bold text-gray-800">${data.basic_cost} - ${data.bank_interest}</div>
                    <hr>
                    <div class="h4 mb-0 font-weight-bold text-gray-800">${data.first_step}<i class="bi bi-currency-euro h4 text-gray-800"></i></div>
                    </div></div></div></div></div>
                    <div class="col-xl-2 col-md-6 mb-4">
                    <div class="card border border-bottom-0 border-top-0 border-end-0 border-5 border-info bg-info-subtle shadow h-100 py-2">
                    <div class="card-body">
                    <div class="row no-gutters align-items-center">
                    <div class="col">
                    <div class="h5 text-secondary fw-bold text-uppercase mb-1">Step 2</div>
                    <div class="h6 mb-0 font-weight-bold text-gray-800">${data.first_step} + ${data.total_tax}</div>
                    <hr>
                    <div class="h4 mb-0 font-weight-bold text-gray-800">${data.second_step}<i class="bi bi-currency-euro h4 text-gray-800"></i></div>
                    </div></div></div></div></div>
                    <div class="col-xl-2 col-md-6 mb-4">
                    <div class="card border border-bottom-0 border-top-0 border-end-0 border-5 border-info bg-info-subtle shadow h-100 py-2">
                    <div class="card-body">
                    <div class="row no-gutters align-items-center">
                    <div class="col">
                    <div class="h5 text-secondary fw-bold text-uppercase mb-1">Step 3</div>
                    <div class="h6 mb-0 font-weight-bold text-gray-800">${data.entry_data} - ${data.second_step}</div>
                    <hr>
                    <div class="h4 mb-0 font-weight-bold text-gray-800">${data.third_step}<i class="bi bi-currency-euro h4 text-gray-800"></i></div>
                    </div></div></div></div></div>
                    <div class="col-xl-2 col-md-6 mb-4">&nbsp;</div>
                    <div class="col-xl-2 col-md-6 mb-4">
                    <div class="card border border-bottom-0 border-top-0 border-end-0 border-5 border-danger bg-danger-subtle shadow h-100 py-2">
                    <div class="card-body">
                    <div class="row no-gutters align-items-center">
                    <div class="col">
                    <div class="h5 text-secondary fw-bold text-uppercase mb-1">Belasting</div>
                    <div class="h6 mb-0 font-weight-bold text-gray-800">${data.third_step} * 0.45</div>
                    <hr>
                    <div class="h4 mb-0 font-weight-bold text-gray-800">${data.tax}<i class="bi bi-currency-euro h4 text-gray-800"></i></div>
                    </div></div></div></div></div>
                    <div class="col-xl-1 col-md-6 mb-4">&nbsp;</div>
                    </div>
                    <div class="row mt-3">
                    <div class="col-xl-1 col-md-6 mb-4">&nbsp;</div>
                    <div class="col-xl-2 col-md-6 mb-4">
                    <div class="card border border-bottom-0 border-top-0 border-end-0 border-5 border-info bg-info-subtle shadow h-100 py-2">
                    <div class="card-body">
                    <div class="row no-gutters align-items-center">
                    <div class="col">
                    <div class="h5 text-secondary fw-bold text-uppercase mb-1">Step 4</div>
                    <div class="h6 mb-0 font-weight-bold text-gray-800">${data.third_step} - ${data.tax}</div>
                    <hr>
                    <div class="h4 mb-0 font-weight-bold text-gray-800">${data.after_tax}<i class="bi bi-currency-euro h4 text-gray-800"></i></div>
                    </div></div></div></div></div>
                    <div class="col-xl-2 col-md-6 mb-4">&nbsp;</div>
                    <div class="col-xl-2 col-md-6 mb-4">&nbsp;</div>
                    <div class="col-xl-2 col-md-6 mb-4">&nbsp;</div>
                    <div class="col-xl-2 col-md-6 mb-4">
                    <div class="card border border-bottom-0 border-top-0 border-end-0 border-5 border-success bg-success-subtle shadow h-100 py-2">
                    <div class="card-body">
                    <div class="row no-gutters align-items-center">
                    <div class="col">
                    <div class="h5 text-secondary fw-bold text-uppercase mb-1">Profit</div>
                    <div class="h6 mb-0 font-weight-bold text-gray-800">${data.after_tax} - ${data.total_salary}</div>
                    <hr>
                    <div class="h4 mb-0 font-weight-bold text-gray-800">${data.quarter_safe}<i class="bi bi-currency-euro h4 text-gray-800"></i></div>
                    </div></div></div></div></div>
                    <div class="col-xl-1 col-md-6 mb-4">&nbsp;</div>
                    </div>

                `);
            });
        }
    });
});