/*
 * Favourite and hidden marks.
 *
 * One end-state endpoint, POST /objects/<id>/mark/, carrying the mark the user
 * wants to hold: "favourite", "hidden" or null to clear. The server owns the
 * rule that the two are mutually exclusive, so the client never chains two
 * requests.
 *
 * This is the site's first CSRF-aware AJAX call, so the token helper lives here
 * and every mark surface reuses it.
 */

function lasairCsrfToken() {
    var match = document.cookie.match(/(^|;)\s*csrftoken\s*=\s*([^;]+)/);
    return match ? decodeURIComponent(match[2]) : '';
}

/*
 * Send the desired end state for one object. Resolves with the server's JSON,
 * rejects with an Error carrying `detail` and, on 403, `loginUrl`.
 */
function postMark(diaObjectId, mark) {
    return fetch('/objects/' + encodeURIComponent(diaObjectId) + '/mark/', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': lasairCsrfToken()
        },
        body: JSON.stringify({ mark: mark })
    }).then(function(response) {
        return response.json().catch(function() {
            return {};
        }).then(function(body) {
            if (response.ok) {
                return body;
            }
            var error = new Error(body.detail || 'Could not save the mark');
            error.status = response.status;
            error.loginUrl = body.loginUrl;
            throw error;
        });
    });
}

/* The mark a pair of buttons holds now, read from the DOM. */
function currentMark(container) {
    var on = container.querySelector('.mark-btn.is-on');
    return on ? on.getAttribute('data-mark') : null;
}

function labelFor(mark, isOn) {
    if (mark === 'favourite') {
        return isOn ? 'Favourited — click to undo' : 'Favourite';
    }
    return isOn ? 'Hidden — click to undo' : 'Hide';
}

/* Paint one pair of buttons to show the given mark. */
function renderMark(container, mark) {
    var buttons = container.querySelectorAll('.mark-btn');
    Array.prototype.forEach.call(buttons, function(button) {
        var isOn = button.getAttribute('data-mark') === mark;
        button.classList.toggle('is-on', isOn);
        button.setAttribute('aria-pressed', isOn ? 'true' : 'false');
        var label = labelFor(button.getAttribute('data-mark'), isOn);
        button.setAttribute('aria-label', label);
        button.setAttribute('title', label);
    });
}

function setInFlight(container, inFlight) {
    var buttons = container.querySelectorAll('.mark-btn');
    Array.prototype.forEach.call(buttons, function(button) {
        button.classList.toggle('is-in-flight', inFlight);
        button.disabled = inFlight;
    });
}

function shake(container) {
    container.classList.remove('mark-shake');
    /* FORCE A REFLOW SO THE ANIMATION RESTARTS ON A SECOND FAILURE */
    void container.offsetWidth;
    container.classList.add('mark-shake');
    setTimeout(function() {
        container.classList.remove('mark-shake');
    }, 350);
}

/*
 * Toasts. Notyf is loaded site-wide by the vendor bundle; fall back to nothing
 * rather than to an alert(), which would block the page.
 */
function lasairToast(message, type) {
    if (typeof Notyf === 'undefined') {
        return;
    }
    if (!window.lasairNotyf) {
        window.lasairNotyf = new Notyf({
            duration: 5000,
            ripple: false,
            position: { x: 'right', y: 'bottom' },
            types: [
                {
                    /* SOFT PINK RATHER THAN NOTYF'S DEFAULT RED: THIS IS A RULE
                     * THE USER HAS RUN INTO, NOT A FAILURE ON THEIR PART. THE PALE
                     * BACKGROUND NEEDS DARK TEXT, WHICH .notyf__toast--mark-error
                     * IN _custom.scss SUPPLIES; NOTYF'S WHITE-ON-COLOUR ICON WOULD
                     * VANISH AGAINST IT, SO THERE IS NO ICON. */
                    type: 'error',
                    background: '#f9dbe3',
                    className: 'notyf__toast--mark-error',
                    icon: false,
                    dismissible: false
                }
            ]
        });
    }
    if (type === 'error') {
        window.lasairNotyf.error(message);
    } else {
        window.lasairNotyf.success(message);
    }
}

/* SHOWN WHEN THE MARK COULD NOT BE SAVED. DELIBERATELY GENERIC: THE SERVER
 * RETURNS ONE 500 FOR EVERY CAUSE -- DATABASE DOWN, TIMEOUT, DROPPED
 * CONNECTION -- SO THIS CANNOT NAME A REASON WITHOUT SOMETIMES BEING WRONG. */
var MARK_ERROR_MESSAGE = 'Something went wrong. Nothing was changed.';

var MARK_DISPLACED_MESSAGE = {
    favourite: 'Favourited. This object is no longer hidden from your results.',
    hidden: 'Hidden. This object is no longer one of your favourites.'
};

/* HOW LONG A ROW STAYS VISIBLE, FADING, BEFORE IT STARTS TO ROLL UP. */
var ROW_FADE_MS = 3000;

/* HOW LONG TO WAIT FOR THE ROLL-UP BEFORE THE ROW IS REMOVED FROM THE TABLE.
 * A HAIR LONGER THAN THE 300ms transition ON tr.row-collapsing IN _custom.scss,
 * SO THE ANIMATION FINISHES BEFORE THE NODE GOES. */
var ROW_COLLAPSE_MS = 350;

/* ROWS ON THEIR WAY OUT, PER TABLE: { objectId: { phase, timer } }. KEYED BY
 * OBJECT ID, NOT BY <tr>: EVERY simple-datatables rows().remove() REBUILDS THE
 * TABLE BODY FROM CLONES, SO A <tr> HELD ACROSS ONE REMOVAL IS DETACHED AND
 * OFF SCREEN BY THE TIME ITS OWN TIMER FIRES. */
var leavingRowsByTable = new WeakMap();

/* THE TWO PHASES OF A LEAVING ROW, EACH NAMED AFTER ITS CSS CLASS. */
var PHASE_FADING = 'fading';
var PHASE_COLLAPSING = 'collapsing';

/* SHOWN ONCE PER BROWSER SESSION, ON THE FIRST HIDE. PERSISTED IN
 * sessionStorage SO A RELOAD DOES NOT RE-SHOW IT; CLEARED WHEN THE TAB
 * (SESSION) ENDS. */
var HIDDEN_INFO_SHOWN_KEY = 'lasair_hidden_info_shown';

/*
 * Handle a click on one mark button. Optimistic: the icon fills immediately and
 * reverts if the write fails, because at realistic latency a pessimistic icon
 * reads as broken.
 *
 * In a result table the clicked cell can be swapped for a clone while the
 * request is in flight (see leavingRowsByTable), so every repaint goes through
 * markCellsFor, which finds the object's cells afresh each time.
 */
function handleMarkClick(button) {
    var container = button.closest('.mark-controls');
    if (!container || button.disabled) {
        return;
    }
    var diaObjectId = button.getAttribute('data-object-id');
    var clicked = button.getAttribute('data-mark');
    var previous = currentMark(container);
    var wanted = previous === clicked ? null : clicked;
    var isRowCell = container.classList.contains('mark-col-cell');
    var table = isRowCell ? container.closest('table') : null;

    function paint(mark, inFlight) {
        markCellsFor(container, table, diaObjectId).forEach(function(cell) {
            renderMark(cell, mark);
            setInFlight(cell, inFlight);
        });
    }

    paint(wanted, true);

    postMark(diaObjectId, wanted).then(function() {
        paint(wanted, false);
        if (wanted && previous && previous !== wanted) {
            lasairToast(MARK_DISPLACED_MESSAGE[wanted], 'info');
        }
        if (wanted === 'hidden') {
            showHiddenInfoPanel();
        }
        if (!isRowCell) {
            /* THE OBJECT-PAGE PAIR: DARKEN OR LIGHTEN THE WHOLE PAGE LIVE. */
            document.body.classList.toggle('object-hidden', wanted === 'hidden');
        }
        if (table) {
            reflectMarkInRow(table, diaObjectId, wanted);
        }
    }).catch(function(error) {
        paint(previous, false);
        shake(container);
        if (error.status === 403 && error.loginUrl) {
            lasairToast('Your session has expired and nothing was changed. Sign in again to continue.', 'error');
        } else {
            lasairToast(MARK_ERROR_MESSAGE, 'error');
        }
    });
}

/*
 * Reveal the "where did hidden objects go" panel, once per browser session,
 * on the first successful hide. Tracked in sessionStorage so it survives a
 * reload but not a new tab/session. The panel is only in the DOM for
 * signed-in users.
 */
function showHiddenInfoPanel() {
    try {
        if (window.sessionStorage.getItem(HIDDEN_INFO_SHOWN_KEY)) {
            return;
        }
        window.sessionStorage.setItem(HIDDEN_INFO_SHOWN_KEY, 'true');
    } catch (e) {
        /* PRIVATE BROWSING OR STORAGE DISABLED: FALL BACK TO SHOWING EVERY TIME. */
    }
    var panel = document.getElementById('hidden-info-panel');
    if (panel) {
        panel.hidden = false;
        /* d-flex ADDED HERE, NOT IN THE TEMPLATE: Bootstrap's !important
         * display:flex WOULD OTHERWISE OVERRIDE [hidden]. SEE THE TEMPLATE
         * COMMENT IN widget_hidden_info_panel.html. */
        panel.classList.add('d-flex');
    }
}

/*
 * Whether the new mark makes this row leave the list it is in. Read from the
 * table's data-mark-list: 'favourites' and 'hidden' are the dedicated pages,
 * anything else is an ordinary result table. A row shown only because "Include
 * hidden objects" is ticked (data-shows-hidden) never leaves.
 */
function rowIsLeaving(table, row, mark) {
    var list = table.getAttribute('data-mark-list');
    if (list === 'favourites') {
        return mark !== 'favourite';
    }
    if (list === 'hidden') {
        return mark !== 'hidden';
    }
    return mark === 'hidden' && row.getAttribute('data-shows-hidden') !== 'true';
}

/* The object a table row shows, read from its mark buttons. */
function rowObjectId(row) {
    var button = row.querySelector ? row.querySelector('.mark-btn[data-object-id]') : null;
    return button ? button.getAttribute('data-object-id') : null;
}

/* The rows leaving one table, created on first use. */
function leavingRowsOf(table) {
    var leaving = leavingRowsByTable.get(table);
    if (!leaving) {
        leaving = new Map();
        leavingRowsByTable.set(table, leaving);
    }
    return leaving;
}

/*
 * Every copy of one object's mark cell in a table, plus the cell that was
 * clicked. Outside a table (the object-page pair) that is the clicked pair
 * alone.
 */
function markCellsFor(container, table, objectId) {
    var cells = [container];
    if (!table) {
        return cells;
    }
    rowsForObject(table, objectId).forEach(function(row) {
        var cell = row.querySelector('.mark-col-cell');
        if (cell && cells.indexOf(cell) === -1) {
            cells.push(cell);
        }
    });
    return cells;
}

/*
 * Every <tr> a table holds: the ones on screen and, once upgraded, the copies
 * simple-datatables keeps for its other pages and its next rebuild.
 */
function tableRows(table) {
    var rows = Array.prototype.slice.call(table.querySelectorAll('tbody tr'));
    var dt = table.lasairDataTable;
    if (dt) {
        rows = rows.concat(dt.data || [], dt.activeRows || []);
    }
    return rows;
}

/* Every copy of one object's row in a table. */
function rowsForObject(table, objectId) {
    return tableRows(table).filter(function(row) {
        return rowObjectId(row) === objectId;
    });
}

/*
 * Paint every row of a table to match the rows leaving it. Run after each
 * change, because a rebuild clones rows with whatever classes the copy it was
 * cloned from held, not the classes that were on screen.
 */
function repaintLeavingRows(table) {
    var leaving = leavingRowsOf(table);
    tableRows(table).forEach(function(row) {
        var entry = leaving.get(rowObjectId(row));
        var phase = entry ? entry.phase : null;
        row.classList.toggle('row-fading', phase === PHASE_FADING);
        row.classList.toggle('row-collapsing', phase === PHASE_COLLAPSING);
    });
}

/*
 * Remove one object's row from its DataTable, keeping simple-datatables' own
 * data array in step so the pager and "Showing X to Y of Z" stay correct. The
 * row is found by object id at removal time, so it does not matter how many
 * rebuilds happened since the click. Falls back to a plain DOM removal if the
 * table was never upgraded.
 */
function removeLeavingRow(table, objectId) {
    leavingRowsOf(table).delete(objectId);
    var dt = table.lasairDataTable;
    if (dt && dt.data) {
        var index = dt.data.findIndex(function(row) {
            return rowObjectId(row) === objectId;
        });
        if (index > -1) {
            dt.rows().remove(index);
        }
    } else {
        rowsForObject(table, objectId).forEach(function(row) {
            row.remove();
        });
    }
    repaintLeavingRows(table);
}

/*
 * Roll the row up — collapse its height to nothing over ROW_COLLAPSE_MS, driven
 * by the CSS transition on tr.row-collapsing — then remove it. The removal timer
 * replaces the fade timer, so an undo click clears it the same way.
 */
function collapseLeavingRow(table, objectId) {
    var entry = leavingRowsOf(table).get(objectId);
    if (!entry) {
        return;
    }
    entry.phase = PHASE_COLLAPSING;
    entry.timer = setTimeout(function() {
        removeLeavingRow(table, objectId);
    }, ROW_COLLAPSE_MS);
    repaintLeavingRows(table);
}

/*
 * In a result table, a mark that makes the row leave its list fades the row over
 * ROW_FADE_MS, then rolls it up and removes it. Clicking the same button again
 * before the row goes clears the timer and restores the row — that is the
 * undo. A mark that does not make the row leave just clears any pending fade.
 * Any number of rows can be leaving at once.
 */
function reflectMarkInRow(table, objectId, mark) {
    var row = rowsForObject(table, objectId)[0];
    if (!row) {
        return;
    }

    var leaving = leavingRowsOf(table);
    if (!rowIsLeaving(table, row, mark)) {
        var pending = leaving.get(objectId);
        if (pending) {
            clearTimeout(pending.timer);
            leaving.delete(objectId);
        }
        repaintLeavingRows(table);
        return;
    }

    if (leaving.has(objectId)) {
        return;
    }
    leaving.set(objectId, {
        phase: PHASE_FADING,
        timer: setTimeout(function() {
            collapseLeavingRow(table, objectId);
        }, ROW_FADE_MS)
    });
    repaintLeavingRows(table);
}

/* One delegated listener per container, never one per button. */
function bindMarkButtons(root) {
    root.addEventListener('click', function(event) {
        var button = event.target.closest ? event.target.closest('.mark-btn') : null;
        if (button && !button.classList.contains('mark-btn-signedout') && root.contains(button)) {
            handleMarkClick(button);
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    bindMarkButtons(document.body);
});
