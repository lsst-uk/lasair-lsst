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
                    noRows: "No objects found",
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

            const headings = dataTable.columns().dt.labels;

            if (headings.includes("objectId")) {
                const idx = headings.indexOf("objectId");
                dataTable.columns().sort(idx, "desc")
            } else if (headings.includes("Created")) {
                const idx = headings.indexOf("Created");
                dataTable.columns().sort(idx, "desc")
            }
            // console.log(dataTable.columns().dt.labels);

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
                        dataTable.columns().dt.labels.forEach(function(label, idx) {
                            if (removeCols.includes(label)) {
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

                        dataTable.export(data);
                    });
                });
            }
        }

    });

});
