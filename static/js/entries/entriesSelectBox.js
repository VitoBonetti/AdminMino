$(document).ready(function() {
    $('#pageSelect').change(function() {
        var url = $(this).val(); // Get the selected option value
        if(url) { // Check if a URL was selected
            window.location = url; // Redirect to the selected URL
        }
    });
});