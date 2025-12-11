$(document).ready(function() {
  $('.detail-link').click(function(e) {
    e.preventDefault();
    var url = $(this).attr('href');
    // Use screen dimensions to open the window in "full screen"
    var windowFeatures = 'width=' + screen.width + ', height=' + screen.height + ', scrollbars=yes';
    window.open(url, 'popupWindow', windowFeatures);
  });
});