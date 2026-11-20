# Changes

## Unreleased

**FEATURE**: the profile page has a "Regenerate token" button below the blurred API token; it opens a confirmation box that warns the old token stops working at once, and the token is replaced only when you confirm.

**ENHANCEMENT**: the profile page shows the API token blurred, with buttons to reveal it and to copy it without revealing it.
**FEATURE**: the object page shows a Detection Scatter card, beside the Object Info card, with a scatter plot of each detection's offset from the object position, drawn with the light curve's band colors and symbols.

**ENHANCEMENT**: the object page's top card is renamed Object Info, is headed with the object's `LSST-AP-DO-<diaObjectId>` name and shows its discovery, latest and peak details in tables at all times, without a Go Deeper button, the object's RA and Dec move to the Detection Scatter card, the TNS and Sherlock cards now sit side by side at half width each, and the object-page cards now share one header layout, so every icon has the same size and top-left position, every title has the same size, and every card has the same padding.

**ENHANCEMENT**: the object page layout now adapts to narrow windows: the top cards rearrange by width, the Object Info tables stack when the card is narrow, the scatter plot keeps a sensible size, and the light curves show fewer date labels on narrow plots and keep the UTC Time title clear of the legend.

**FIXED**: every page was slow or stalled when the CDS servers were slow, because each page loaded Aladin Lite with a blocking script tag from the CDS website; Lasair now serves its own copy of Aladin Lite 3.8.1, loads it only on the home, object and MMA watchmap pages, loads it in the background, and shows a message in the sky map if it has not loaded after 10 seconds.

**FIXED**: unfavouriting or unhiding several objects in quick succession on the Favourites or Hidden page removed only the first row, because each removal rebuilt the table from clones and the pending timers still pointed at the old rows; leaving rows are now tracked by object id, and a mark set on one row now survives another row's removal.

**FIXED**: the `fits` cutout view opened a new Cassandra cluster connection on every request and never shut it down; each web worker now reuses one connection, and rebuilds it after a failed connect, a lost connection, a shutdown, or a fork.

**FIXED**: `test_hidden_object_results.py` and `test_email_digest.py` failed in CI, because they relied on settings (`lasair.settings`, `LASAIR_URL`) that only the gitignored `settings.py` on developer machines provides.

**FIXED**: `gulp build` corrupted every binary asset it copied, because gulp 5 decodes file contents as UTF-8 by default and replaces each invalid byte sequence with U+FFFD, which left images, fonts, the PDF and the JS9 WebAssembly module both broken and larger than their sources.

**FIXED**: hiding an object the user had favourited returned a 500, because the new mark was inserted before the mark it displaces was deleted, which is a duplicate entry against the unique key that schemas before 11_1 carry over `(diaObjectId, topic)`.

**FIXED**: `3_make_alter_table.py` diffed only the fields of a schema, so an index change between two versions was never emitted as an `ALTER TABLE` and never reached an existing database.

**FIXED**: the test image build and the filter deploy role failed to install the SFD dust maps, because Harvard Dataverse now returns 403 to the python-requests user agent that `dustmaps.sfd.fetch()` uses; both now download the two maps directly, check their MD5 sums, and confirm `SFDQuery` loads them.

**ENHANCEMENT**: the New and Edit Filter forms no longer offer the per-user `tags_<username>` annotators in the Object Annotators list; a filter that already uses one keeps it.

**ENHANCEMENT**: the deploy playbooks pinned schema 11_0 while `SCHEMA_VERSION` was 11_1, so fresh nodes were built with the superseded `annotations` unique key.

**ENHANCEMENT**: the toast shown when a mark cannot be saved is now soft pink with a generic message, rather than Notyf's default red carrying the server's error detail.

**ENHANCEMENT**: SQL shown to users now replaces the favourites/hidden-objects correlated subquery with a short comment placeholder, instead of exposing the raw `EXISTS` clause.

**ENHANCEMENT**: the hide button now shows a plain open eye when an object is not hidden and a plain closed eye when it is, instead of a single crossed-eye glyph, everywhere the mark applies (object page, result tables, the hidden-objects list header).

**ENHANCEMENT**: the "My hidden objects" link on the profile page now uses the same closed-eye icon as the hide button, instead of the crossed-eye glyph it kept after the hide button moved on.

**REFACTOR**: removed the unused Aladin Lite files `aladin.js`, `aladin.min.js` and `aladin.min.css` from `webserver/static/vendor/` and `webserver/staticfiles/vendor/`; no page loaded them, and Aladin Lite now comes from `vendor/aladin-lite/<VERSION>/`.

**FEATURE**: hiding an object from a result table fades the row, rolls it up and removes it, and a panel shown once per browser session says where hidden objects went.

**ENHANCEMENT**: search now sends a GET request, so `/search/?query=<text>` links work and a search can be bookmarked or shared; the old `/search/<query>` URL still works.

**ENHANCEMENT**: results and object-page tables fit their cards at desktop width without a scrollbar above the table, show readable column headings with units (for example "separation (arcsec)" and "r flux (nJy)"), keep the mark column and diaObjectId in view while other columns scroll, and no longer let sort arrows cover short headings; sorting and export still use the raw column names. The `table-responsive` wrapper stays as a fallback for older CSS.

**ENHANCEMENT**: the Schema Browser has one search box in its header card that filters every table by table name, column name, or description, shows the match count, and clears when you click a table jump link.

**ENHANCEMENT**: the sidebar highlights only the current page, sets `aria-current`, shows a keyboard focus ring, points the Sky Area and Status arrows down when their menus are open, and opens those menus with real buttons.

**ENHANCEMENT**: every page has a tab title in the form "Page name · Lasair", including the Home, object, Filter Builder, and sign-in pages; the sign-in row now puts "Remember me" on the left and one "Forgot password?" link on the right, and the logo links home.

**REFACTOR**: the old `/api`, `/contact`, and `/simple_search` pages are replaced by redirects to the REST API docs, the contact docs, and the Filter Builder; the unused `api.html`, `contact.html`, and `simple_search.html` templates are deleted.

**FIXED**: the search view built SQL by joining user input into the query string; it now binds every value as a parameter, accepts object names only from an allow-list, rejects cone radii that are not finite and positive or are over 1000 arcsec, rejects coordinates that are not finite or are off the sky (and accepts a declination of exactly 90), and the unused `conesearch_impl`, `readcone`, `sexra`, and `sexde` helpers are removed.

**FIXED**: the `run_filter` error message showed the internal query wrapper and put the user's SQL and the database error into HTML unescaped; it now shows the SQL the user wrote, escapes both strings, and the Filter Builder shows this error after a failed run.

**FIXED**: the status page hid the Next day button in the evening, because `nid_to_days_ago` read the clock separately from `nid_now`; both now use `nid_now`, and the Previous day and Next day buttons sit in the header card.

**FIXED**: filter name and description examples are placeholders, not prefilled text, and a form submitted with the example text is rejected; the Filter Builder no longer shows "ZERO MATCHES" before a run; the lightcurve Log toggle looks like a button and shows when it is on; the filter list shows an Active or Off badge on every row.

**FIXED**: text and empty states from the UI/UX audit: clearer intros for the home, filters, watchmaps, and annotators pages, a watchlist header with a count in words in place of the corner badge, empty tables that name the item and the next step, a favourites empty state, no "None" for an empty annotator description, a profile form with full-width upload and its help text below, and an annotator header that tested `annotation.active`, a variable that does not exist.

**TEST**: new unit tests cover search, filter descriptions, the Log toggle, docs redirects, column labels, page titles, and the `run_filter` error, and `test_date_nid.py` freezes the clock; all run in `tests/Jenkinsfile`.
