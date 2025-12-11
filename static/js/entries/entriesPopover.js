$(document).ready(function() {
  $('[data-bs-toggle="popover"]').popover({
    trigger: 'hover',
    container: 'body' // This helps with positioning if your table is complex
  });
});