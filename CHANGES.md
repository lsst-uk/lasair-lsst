# Changes

## Unreleased

**FIXED**: every page was slow or stalled when the CDS servers were slow, because each page loaded Aladin Lite with a blocking script tag from the CDS website; Lasair now serves its own copy of Aladin Lite 3.8.1, loads it only on the home, object and MMA watchmap pages, loads it in the background, and shows a message in the sky map if it has not loaded after 10 seconds.

**FIXED**: unfavouriting or unhiding several objects in quick succession on the Favourites or Hidden page removed only the first row, because each removal rebuilt the table from clones and the pending timers still pointed at the old rows; leaving rows are now tracked by object id, and a mark set on one row now survives another row's removal.
**FIXED**: the `fits` cutout view opened a new Cassandra cluster connection on every request and never shut it down; each web worker now reuses one connection, and rebuilds it after a failed connect, a lost connection, a shutdown, or a fork.

**FIXED**: `test_hidden_object_results.py` and `test_email_digest.py` failed in CI, because they relied on settings (`lasair.settings`, `LASAIR_URL`) that only the gitignored `settings.py` on developer machines provides.

**FIXED**: `gulp build` corrupted every binary asset it copied, because gulp 5 decodes file contents as UTF-8 by default and replaces each invalid byte sequence with U+FFFD, which left images, fonts, the PDF and the JS9 WebAssembly module both broken and larger than their sources.

**FIXED**: hiding an object the user had favourited returned a 500, because the new mark was inserted before the mark it displaces was deleted, which is a duplicate entry against the unique key that schemas before 11_1 carry over `(diaObjectId, topic)`.

**FIXED**: `3_make_alter_table.py` diffed only the fields of a schema, so an index change between two versions was never emitted as an `ALTER TABLE` and never reached an existing database.

**ENHANCEMENT**: the New and Edit Filter forms no longer offer the per-user `tags_<username>` annotators in the Object Annotators list; a filter that already uses one keeps it.

**ENHANCEMENT**: the deploy playbooks pinned schema 11_0 while `SCHEMA_VERSION` was 11_1, so fresh nodes were built with the superseded `annotations` unique key.

**ENHANCEMENT**: the toast shown when a mark cannot be saved is now soft pink with a generic message, rather than Notyf's default red carrying the server's error detail.

**ENHANCEMENT**: SQL shown to users now replaces the favourites/hidden-objects correlated subquery with a short comment placeholder, instead of exposing the raw `EXISTS` clause.

**ENHANCEMENT**: the hide button now shows a plain open eye when an object is not hidden and a plain closed eye when it is, instead of a single crossed-eye glyph, everywhere the mark applies (object page, result tables, the hidden-objects list header).

**ENHANCEMENT**: the "My hidden objects" link on the profile page now uses the same closed-eye icon as the hide button, instead of the crossed-eye glyph it kept after the hide button moved on.

**REFACTOR**: removed the unused Aladin Lite files `aladin.js`, `aladin.min.js` and `aladin.min.css` from `webserver/static/vendor/` and `webserver/staticfiles/vendor/`; no page loaded them, and Aladin Lite now comes from `vendor/aladin-lite/<VERSION>/`.

**FEATURE**: hiding an object from a result table fades the row, rolls it up and removes it, and a panel shown once per browser session says where hidden objects went.
