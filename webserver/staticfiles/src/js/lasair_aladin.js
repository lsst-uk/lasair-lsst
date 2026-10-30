/*
 * Load Aladin Lite on demand, without blocking the rest of the page.
 *
 * Aladin Lite ships as an ES module, so it is fetched with a dynamic import().
 * If it does not load and initialise within ALADIN_TIMEOUT_MS, a message is
 * shown in the sky-map container and the returned promise rejects.
 */
(function () {
    // A SECOND INCLUDE ON THE SAME PAGE KEEPS THE FIRST LOADER AND ITS SHARED IMPORT
    if (window.loadAladin) {
        return;
    }

    var ALADIN_TIMEOUT_MS = 10000;
    var FALLBACK_MESSAGE = 'Sky map unavailable: Aladin Lite could not be loaded. Reload the page to try again.';
    var aladinPromise = null;

    function showFallback(containerSelector) {
        var container = document.querySelector(containerSelector);
        if (!container) {
            return;
        }
        var message = document.createElement('p');
        message.className = 'text-muted text-center mb-0 px-3';
        message.setAttribute('role', 'status');
        message.textContent = FALLBACK_MESSAGE;
        container.textContent = '';
        container.classList.add('d-flex', 'align-items-center', 'justify-content-center', 'bg-gray-50', 'rounded');
        container.appendChild(message);
    }

    function importAladin(src) {
        // ONE IMPORT PER PAGE, SHARED BY EVERY CALLER
        if (!aladinPromise) {
            aladinPromise = import(src).then(function (module) {
                var A = module.default;
                window.A = A;
                return A.init.then(function () {
                    return A;
                });
            });
        }
        return aladinPromise;
    }

    window.loadAladin = function (src, containerSelector, timeoutMs) {
        var limitMs = timeoutMs || ALADIN_TIMEOUT_MS;
        var timer;
        var timeout = new Promise(function (resolve, reject) {
            timer = setTimeout(function () {
                reject(new Error('Aladin Lite did not load within ' + limitMs + ' ms (timed out)'));
            }, limitMs);
        });

        // IF THE IMPORT FINISHES AFTER THE TIMEOUT, THE MAP IS DELIBERATELY NOT DRAWN:
        // THE FALLBACK STAYS, AND A RELOAD USES THE NOW-CACHED FILE
        return Promise.race([importAladin(src), timeout]).then(
            function (A) {
                clearTimeout(timer);
                return A;
            },
            function (error) {
                clearTimeout(timer);
                console.warn('Aladin Lite unavailable:', error);
                showFallback(containerSelector);
                throw error;
            }
        );
    };
})();
