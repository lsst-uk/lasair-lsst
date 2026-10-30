# Changes

## Unreleased

**FIXED**: every page was slow or stalled when the CDS servers were slow, because each page loaded Aladin Lite with a blocking script tag from the CDS website; Lasair now serves its own copy of Aladin Lite 3.8.1, loads it only on the home, object and MMA watchmap pages, loads it in the background, and shows a message in the sky map if it has not loaded after 10 seconds.
