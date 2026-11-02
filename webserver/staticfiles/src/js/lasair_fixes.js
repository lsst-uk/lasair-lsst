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

    // Default tooltip timing: instant show, 0.5s hide. Tooltips that contain
    // a link (see includes/info_tooltip.html) override this per-element via
    // data-bs-delay so there's time to reach the link before it disappears.
    bootstrap.Tooltip.Default.delay = { show: 0, hide: 500 };
    var ttDefaultAllowList = bootstrap.Tooltip.Default.allowList;
    ttDefaultAllowList.table = [];
    ttDefaultAllowList.tr = [];
    ttDefaultAllowList.td = ['data-bs-option'];
    ttDefaultAllowList.th = [];
    ttDefaultAllowList.div = [];
    ttDefaultAllowList.tbody = [];
    ttDefaultAllowList.thead = [];

    // Guard against double-initializing an element that already has a
    // Tooltip instance (e.g. from volt.js's own init) -- attaching a second
    // instance to the same element is what caused tooltips to bubble.
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
        if (!bootstrap.Tooltip.getInstance(el)) {
            new bootstrap.Tooltip(el);
        }
    });

    // Only ever show one tooltip at a time: as soon as one is about to
    // appear, hide every other currently-attached tooltip instance.
    document.addEventListener('show.bs.tooltip', function (e) {
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
            if (el !== e.target) {
                var instance = bootstrap.Tooltip.getInstance(el);
                if (instance) {
                    instance.hide();
                }
            }
        });
    });

});
