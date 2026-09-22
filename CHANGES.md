# Changes

## Unreleased

**FIXED**: `gulp build` corrupted every binary asset it copied, because gulp 5 decodes file contents as UTF-8 by default and replaces each invalid byte sequence with U+FFFD, which left images, fonts, the PDF and the JS9 WebAssembly module both broken and larger than their sources.

**FIXED**: hiding an object the user had favourited returned a 500, because the new mark was inserted before the mark it displaces was deleted, which is a duplicate entry against the unique key that schemas before 11_1 carry over `(diaObjectId, topic)`.

**FIXED**: `3_make_alter_table.py` diffed only the fields of a schema, so an index change between two versions was never emitted as an `ALTER TABLE` and never reached an existing database.

**ENHANCEMENT**: the deploy playbooks pinned schema 11_0 while `SCHEMA_VERSION` was 11_1, so fresh nodes were built with the superseded `annotations` unique key.

**ENHANCEMENT**: the toast shown when a mark cannot be saved is now soft pink with a generic message, rather than Notyf's default red carrying the server's error detail.

**ENHANCEMENT**: SQL shown to users now replaces the favourites/hidden-objects correlated subquery with a short comment placeholder, instead of exposing the raw `EXISTS` clause.

**ENHANCEMENT**: the hide button now shows the same closed-eye icon as the "My hidden objects" link on the profile page, instead of an archive box, everywhere the mark applies (object page, result tables, the hidden-objects list header).

**FEATURE**: hiding an object from a result table fades the row, rolls it up and removes it, and a panel shown once per browser session says where hidden objects went.
