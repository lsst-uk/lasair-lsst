const DEFAULT_EMPTY_TEXT = "No objects found";

/*
 * THE SEARCH BOX AND ROWS-PER-PAGE CONTROL ARE NO USE ON A TABLE WITH NO ROWS.
 * A SEARCH THAT MATCHES NOTHING IS NOT THIS CASE: THE BOX MUST STAY SO THE USER CAN CLEAR IT.
 */
function toggleEmptyTableControls(dataTable) {
    dataTable.wrapper.classList.toggle('lasair-table-is-empty', dataTable.data.length === 0);
}

/*
 * SCROLL THE TABLE ITSELF (NOT THE SEARCH BOX AND PAGER AROUND IT) AND KEEP TWO CLASSES ON ITS
 * FRAME IN STEP WITH THE SCROLL POSITION, FOR THE SHADOWS DRAWN IN _custom.scss.
 */
function frameScrollingTable(dataTable) {
    const container = dataTable.container;
    const frame = document.createElement('div');
    frame.className = 'results-scroll-frame';
    container.parentNode.insertBefore(frame, container);
    frame.appendChild(container);

    const updateShadows = function() {
        const hiddenOnRight = container.scrollWidth - container.clientWidth - container.scrollLeft;
        frame.classList.toggle('can-scroll-right', hiddenOnRight > 1);
        frame.classList.toggle('is-scrolled', container.scrollLeft > 0);
    };
    container.addEventListener('scroll', updateShadows, { passive: true });
    window.addEventListener('resize', updateShadows);
    dataTable.on('datatable.update', updateShadows);
    updateShadows();
}

/*
 * THE HEADINGS SHOWN ON THE PAGE ARE READABLE LABELS ("RA (deg)"). EXPORTS KEEP THE HEADING EACH <th>
 * DECLARES IN data-column-name (THE RAW COLUMN NAME), SO EXPORTED FILES ARE UNCHANGED.
 * THE LABELS ARE SWAPPED BACK AS SOON AS THE EXPORT HAS BUILT ITS FILE.
 */
function exportWithRawColumnNames(dataTable, exportOptions) {
    const swapped = [];
    dataTable.headings.forEach(function(th) {
        const rawName = th.getAttribute('data-column-name');
        if (rawName === null) {
            return;
        }
        const labelEl = th.querySelector('.dataTable-sorter') || th;
        swapped.push({ labelEl: labelEl, label: labelEl.textContent });
        labelEl.textContent = rawName;
    });
    try {
        dataTable.export(exportOptions);
    } finally {
        swapped.forEach(function(item) {
            item.labelEl.textContent = item.label;
        });
    }
}

/*
 * EACH COLUMN'S RAW NAME: THE <th>'S data-column-name WHEN IT HAS ONE (THE SHARED RESULTS TABLE),
 * OTHERWISE ITS HEADING TEXT. LOOKUPS BY NAME USE THIS, SO A READABLE LABEL CANNOT BREAK THEM.
 */
function columnNames(dataTable) {
    const labels = dataTable.columns().dt.labels;
    return dataTable.headings.map(function(th, idx) {
        const rawName = th.getAttribute('data-column-name');
        return rawName === null ? labels[idx] : rawName;
    });
}

document.addEventListener('DOMContentLoaded', function() {

    let dataTableEls = d.querySelectorAll('.datatable');
    dataTableEls.forEach(function(dataTableEl) {
        if (dataTableEl) {

            let tableId = null;
            if (dataTableEl.hasAttribute('id')) {
                tableId = dataTableEl.id;
            }

            let perPage = 100;
            if (dataTableEl.hasAttribute('data-perPage')) {
                perPage = parseInt(dataTableEl.getAttribute('data-perPage'));
            }

            /*
             * THE MARK COLUMN'S INDEX IS DECLARED BY THE WIDGET, NOT MATCHED BY LABEL:
             * ITS HEADING IS DELIBERATELY EMPTY AND A USER CAN ALIAS A COLUMN TO ANYTHING.
             */
            let markCol = null;
            if (dataTableEl.hasAttribute('data-mark-col')) {
                markCol = parseInt(dataTableEl.getAttribute('data-mark-col'));
            }

            const emptyText = dataTableEl.getAttribute('data-empty-text') || DEFAULT_EMPTY_TEXT;

            let searchable = true;
            let paging = true;
            if (dataTableEl.hasAttribute('datatable-vanilla')) {
                searchable = false;
                paging = false;
            }

            const dataTable = new simpleDatatables.DataTable(dataTableEl, {
                labels: {
                    placeholder: "Search table...",
                    perPage: "{select} rows per page",
                    noRows: emptyText,
                    info: "Showing {start} to {end} of {rows} rows",
                },
                searchable: searchable,
                paging: paging,
                layout: {
                    top: "{search}",
                    bottom: "{select}{info}{pager}"
                },
                perPage: perPage,
                perPageSelect: [5, 10, 50, 100, 500, 10000],
                /* WITHOUT THIS, THE BLANK HEADING SORTS BY BUTTON MARKUP AND SEARCH MATCHES EVERY ROW */
                columns: markCol === null ? [] : [{ select: markCol, sortable: false, searchable: false }]
            });

            /* SO lasair_mark.js CAN REMOVE A ROW THROUGH THE DATATABLE, KEEPING THE PAGER AND COUNT IN STEP. */
            dataTableEl.lasairDataTable = dataTable;

            toggleEmptyTableControls(dataTable);
            dataTable.on('datatable.update', function() {
                toggleEmptyTableControls(dataTable);
            });

            if (dataTableEl.classList.contains('results-table')) {
                frameScrollingTable(dataTable);
            }

            const headings = columnNames(dataTable);

            if (headings.includes("objectId")) {
                const idx = headings.indexOf("objectId");
                dataTable.columns().sort(idx, "desc")
            } else if (headings.includes("Created")) {
                const idx = headings.indexOf("Created");
                dataTable.columns().sort(idx, "desc")
            }

            if (tableId !== null) {
                document.querySelectorAll(`a[data-table=${CSS.escape(tableId)}]`).forEach(function(el) {
                    el.addEventListener("click", function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        e.stopImmediatePropagation();

                        const anchor = e.currentTarget;

                        var type = anchor.dataset.type;
                        var filename = anchor.dataset.filename;

                        if (filename == null) {
                            filename = "lasair-export";
                        }

                        var data = {
                            type: type,
                            filename: filename,
                        };

                        // REMOVE IMAGES AND ALERT PACKET COLUMNS IF THEY EXIST, AS THESE ARE NOT NEEDED IN THE EXPORT
                        const removeCols = ["images", "alert packet"];
                        const colIdxsToRemove = [];
                        columnNames(dataTable).forEach(function(name, idx) {
                            if (removeCols.includes(name)) {
                                colIdxsToRemove.push(idx);
                            }
                        });
                        if (markCol !== null) {
                            colIdxsToRemove.push(markCol);
                        }

                        if (type === "csv") {
                            data.columnDelimiter = ",";
                            data.skipColumn = colIdxsToRemove;
                        }

                        if (type === "json") {
                            data.replacer = null;
                            data.space = 4;
                            data.skipColumn = colIdxsToRemove;
                        }

                        exportWithRawColumnNames(dataTable, data);
                    });
                });
            }
        }

    });

});
