var loadtype;
var ndiv = 0;
var nwin = 1;
var lastid;

document.addEventListener('DOMContentLoaded', function() {

    JS9.globalOpts.alerts = false;
    JS9.globalOpts.updateTitlebar = false;
    JS9.globalOpts.lightWinClose = "close";
    JS9.globalOpts.helperType = "none";
    JS9.globalOpts.helperPort = 3333;

    JS9.imageOpts = {
        inherit: false, // inherit props from previous image?
        contrast: 1.0, // default color contrast
        bias: 0.5, // default color bias
        invert: false, // default colormap invert
        exp: 1000, // default exp value for scaling
        colormap: "heat", // default color map
        overlay: true, // display png/jpeg overlay?
        scale: "linear", // default scale algorithm
        scaleclipping: "dataminmax", // "dataminmax", "zscale", or "user" (when scalemin, scalemax is supplied)
        scalemin: Number.NaN, // default scale min is undefined
        scalemax: Number.NaN, // default scale max is undefined
        flip: "none", // default flip state
        rot90: 0, // default 90 deg rotation state
        rotate: 0, // default rotation state
        zscalecontrast: 0.25, // default from ds9
        zscalesamples: 600, // default from ds9
        zscaleline: 120, // default from ds9
        wcssys: "native", // default WCS sys
        lcs: "physical", // default logical coordinate system
        valpos: false, // whether to display value/position
        sigma: "none", // gauss blur sigma or none
        opacity: 1.0, // opacity between 0 and 1
        alpha: 255, // alpha for image (but use opacity!)
        nancolor: "#FF0000", // 6-digit #hex color for NaN values
        nocolor: {
            red: 0,
            green: 0,
            blue: 0,
            alpha: 0
        }, // static color map no color
        // xcen: 0,                         // default x center pos to pan to
        // ycen: 0,                         // default y center pos to pan to
        zoom: "toFit", // default zoom factor
        zooms: 6, // how many zooms in each direction?
        topZooms: 2, // how many zooms are at top level?
        wcsalign: true, // align image using wcs after reproj?
        rotationMode: "relative", // default: relative or absolute?
        crosshair: true, // enable crosshair?
        disable: [], // list of disabled core services
        ltvbug: false, // add 0.5/ltm to image LTV values?
        listonchange: false, // whether to list after a reg change
        whichonchange: "selected" // which to list ("all" or "selected")
    };

    let fns = [loadFitsImages, fixJS9ExtraStyles, collapseJS9Extras];

    // chain function will call the supplied function
    // and recursively call the chain function with the
    // the next element in the array
    function chain(fn) {
        if (fn) {
            fn(() => chain(fns.shift()));
        }
    }
    chain(fns.shift());

});

function fixJS9ExtraStyles(next) {
    // MAKE SQUARE
    let fitsImgs = document.querySelectorAll(".JS9");
    fitsImgs.forEach(function(fits) {
        var checkExist = setInterval(function() {
            if ($(`#${fits.id}`).length) {
                clearInterval(checkExist);
                var im = JS9.LookupDisplay(fits.id);
                JS9.ResizeDisplay(fits.id, im.width, im.width);
            }
        }, 100); // check every 100ms

    });
    // MAKE SQUARE
    var checkExist2 = setInterval(function() {
        if (document.querySelectorAll(".JS9Magnifier").length) {
            clearInterval(checkExist2);
            let plugins = document.querySelectorAll(".JS9Magnifier");

            plugins.forEach(function(plugin) {
                plugin.style.height = plugin.offsetWidth + 'px';
            });
        }
    }, 100); // check every 100ms
    setTimeout(() => {
        next()
    }, 2000);
    // MAKE SQUARE
    var checkExist = setInterval(function() {
        if (document.querySelectorAll(".ImExamRadialProj").length) {
            clearInterval(checkExist);
            let plugins = document.querySelectorAll(".ImExamRadialProj");

            plugins.forEach(function(plugin) {
                plugin.style.height = plugin.offsetWidth + 'px';
            });
        }
    }, 100); // check every 100ms
    setTimeout(() => {
        next()
    }, 2000);

    // MAKE SQUARE
    var checkExist3 = setInterval(function() {
        if (document.querySelectorAll(".ImExam3dPlot").length) {
            clearInterval(checkExist3);
            let plugins = document.querySelectorAll(".ImExam3dPlot");

            plugins.forEach(function(plugin) {
                plugin.style.height = plugin.offsetWidth + 'px';
            });
        }
    }, 100); // check every 100ms
    setTimeout(() => {
        next()
    }, 2000);

}

function loadFitsImages(next) {
    let allFits = document.querySelectorAll(".fitsStamp");
    allFits.forEach(function(fits) {
        let fitsScr = fits.getAttribute("src");
        const newItem = document.createElement('span');
        let uuid = uuidv4();
        newItem.innerHTML = `<div class="JS9" data-width="100%" id="${uuid}" ></div>`;
        if (fits.classList.contains("fits-lite")) {
            // DO NOTHING
        } else if (fits.classList.contains("fits-toggle")) {
            newItem.innerHTML = `<div class="JS9Menubar d-none" id="${uuid}Menubar" data-width="100%"></div>` + newItem.innerHTML
        } else {
            newItem.innerHTML = `<div class="JS9Menubar" id="${uuid}Menubar" data-width="100%"></div>` + newItem.innerHTML
        }

        fits.parentNode.replaceChild(newItem, fits);

        JS9.Preload(fitsScr, {
            scale: 'linear',
            zoom: 'toFit',
            onload: setDefaultParams
        }, {
            display: uuid
        });
    });
    next();
};

function collapseJS9Extras(next) {

    var myCollapse = document.getElementById('collapseJS9Extras');
    if (typeof myCollapse !== 'undefined' && myCollapse !== null) {
        myCollapse.classList.add("collapse");
        next();
    }
}

function setDefaultParams(display) {

    JS9.SetZoom('ToFit', {
        display: display
    });
    JS9.SetColormap('grey', {
        display: display
    });
    JS9.SetScale('dataminmax', {
        display: display
    });
    JS9.AddRegions("circle", {
        radius: 10
    }, {
        display: display
    });
    // JS9.SetOpacity(opacity, floorvalue, flooropacity);
    // JS9.SetFlip(flip);
    // JS9.SetRotate(rot);
    // JS9.SetParam(param, value);

}

function uuidv4() {
    return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
}

function toggleJS9Menus() {
    event.preventDefault();
    let menus = document.getElementsByClassName('JS9Menubar');
    for (var i = 0; i < menus.length; i++) {
        menus[i].classList.toggle('d-none');
    }
}

function JS9Popout(file, opts) {
    var dobj = JS9.LookupDisplay("Stamp", false);
    loadtype = "light";
    var id, did, head, body, html, doc;
    var myopts = opts || {};
    myopts.onload = setDefaultParams;
    myopts.id = "Stamp";
    if (dobj == null) {

        lastid = JS9.LoadWindow(file, myopts, "light");
    } else {
        JS9.RefreshImage(file, myopts, {
            display: dobj
        })
    }

}
