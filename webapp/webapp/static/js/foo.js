$(document).ready(function () {
    $("#selectImage").imagepicker({
        hide_select: true
    });

    var $container = $('.image_picker_selector');
    // initialize
    $grid.imagesLoaded(function () {
        $grid.masonry({
            columnWidth: 30,
            itemSelector: '.thumbnail'
        });
    });
});
