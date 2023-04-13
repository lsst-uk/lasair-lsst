document.addEventListener('DOMContentLoaded', function() {

    const myDefaultAllowList = bootstrap.Popover.Default.allowList;

    myDefaultAllowList.table = [];
    myDefaultAllowList.tr = [];
    myDefaultAllowList.td = ['data-bs-option'];
    myDefaultAllowList.th = [];
    myDefaultAllowList.div = [];
    myDefaultAllowList.tbody = [];
    myDefaultAllowList.thead = [];

    $('[data-bs-toggle="popover"]').popover();

    var ttDefaultAllowList = bootstrap.Tooltip.Default.allowList;
    ttDefaultAllowList.table = [];
    ttDefaultAllowList.tr = [];
    ttDefaultAllowList.td = ['data-bs-option'];
    ttDefaultAllowList.th = [];
    ttDefaultAllowList.div = [];
    ttDefaultAllowList.tbody = [];
    ttDefaultAllowList.thead = [];

    $('[data-bs-toggle="tooltip"]').tooltip();

});

$(document).ready(function() {
    $('body').on('inserted.bs.tooltip', function(e) {
        var $target = $(e.target);

        // Keep track so we can check if mouse is hovering over the tooltip
        $('[role="tooltip"]').hover(function() {
            $(this).toggleClass('hover');
        });

        $target.on('hide.bs.tooltip', function(e) {
            // If tooltip is under the mouse, prevent hide but
            // add handler to hide when mouse leaves tooltip
            if ($('[role="tooltip"]').hasClass('hover')) {
                $('[role="tooltip"]').on('mouseleave', function() {
                    setTimeout(function() {
                        $target.tooltip('hide');
                    }, 200);
                });
                // Tell bootstrap tooltip to bail and not actually hide
                e.preventDefault();
                return;
            }
        });
    });
});
