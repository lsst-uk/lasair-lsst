# Sky Context

There are already a large number of astronomical catalogues, each containing carefully curated data about 
astronomical objects: stars, galaxies, variable stars, cataclysmic variables, active galactic nuclei, etc.
When an existing object brightens, or a new object appears, astronomers want to know if it is 
already known, and if so, what kind of object it is. If the astronomer is searching for extra-galactic
explosive events such as supernovae, they are usually associated with a galaxy. That astronomer is also 
interested if the explosive event has already been seen and registered by somebody else.

Lasair provides several kinds of sky context:

 - Sherlock: A software package and integrated massive database system that provides a 
rapid and reliable spatial cross-match service for any astrophysical variable or transient.
[Details here](../core_functions/sherlock.html).

 - Transient Name Server (TNS) is the official IAU mechanism for reporting new astronomical 
transients such as supernova candidates. Once spectroscopically confirmed, new supernova 
discoveries are officially designated a SN name. Lasair keeps a cache of the database, updated every few hours.
[Details here](https://www.wis-tns.org/).

 - Personal Watchlists: Lasair allows users to upload personal catalogues of interesting sources, which are 
crossmatched in real time with incoming alerts.
