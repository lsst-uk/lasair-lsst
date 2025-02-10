# Lasair Client

The Lasair-Sherlock client allows developers to run queries and cone-searches, to see outputs from streaming queries, and to query the Sherlock sky-context system.

#### Sample Notebooks
Installation:
```
pip3 install lasair
```

#### Sample Notebooks
There is an [accompanying set of jupyter notebooks](python-notebooks.md)

#### Throttling of API Usage
The client has a throttling system in the backend: users with an account get up to 100 calls per hour, but "power" users get up to 10,000 calls per hour. If you wish your account to be upgraded to power user, 
[email Lasair-help](mailto:lasair-help@mlist.is.ed.ac.uk?subject=power user)

**Note: WE ASK YOU TO PLEASE NOT SHARE THESE TOKENS.** If you share code that uses the Lasair API, please put the token in a separate, imported file or environment variable, that you do not share, and is not put in github.

##### Authorisation Token

Request authentication is via the API key. Once you are logged in on the website, click on your name at the top right, and choose "My Profile". The API key can be copied and pasted into your own code. We recommend using a `settings.py` file for this,  that remains private.

#### Methods

Click on the method name to jump to documentation in the reference below.

*   [cone](#cone): runs a cone search on all the objects in the Lasair database.
*   [query](#query): runs a SQL SELECT query on the Lasair database.
*   [object](#object): returns a machine-readable version of the object web page.
*   [sherlock_object](#sherlockobject): returns Sherlock information about a named object.
*   [sherlock_position](#sherlockposition): returns Sherlock information about a sky position.

### <a name="cone"></a>cone

This method runs a cone search on all the objects in the Lasair database. The arguments are:

*   `ra`: (float) the right ascension in decimal degrees,
*   `dec`: (float) the declination in decimal degrees,
*   `radius`: (float) the angular radius of the cone in arcseconds, the maximum being 1000 arcseconds.
*   `requestType`: (string) the type of request, which can be:
    *   `nearest`: returns only the nearest objects within the cone
    *   `all`: returns all the objects within the cone
    *   `count`: returns the number of objects within the cone

Example:
```
import lasair
token = 'xxxxxxxxxxxxxxxxxxxxxxxx'
L = lasair.lasair_client(token)
c = L.cone(ra, dec, radius=240.0, requestType='all')
print(c)
```
and the return has object identifiers, and their separations in arcseconds, something like:
```
[
    {
        "object": "ZTF17aaajmtw",
        "separation": 2.393511865261539
    }
]
```
### <a name="query"></a>query

This method runs a query on the Lasair database. There is an [interactive query builder](/query), and a [schema description](/schema). The arguments are:

*   `selected`: (string) the list of attributes to be returned,
*   `tables`: (string) the list of tables to be joined,
*   `conditions`: (string) the "WHERE" criteria to restrict what is returned
*   `limit`: (int) (not required) the maximum number of records to return (default is 1000)
*   `offset`: (int) (not required) offset of record number (default is 0)

Example:
```
import lasair
token = 'xxxxxxxxxxxxxxxxxxxxxxxx'
L = lasair.lasair_client(token)
selected    = 'objectId, gmag'
tables      = 'objects'
conditions  = 'gmag < 12.0'
c = L.query(selected, tables, conditions, limit=10)
print(c)
```
and the return is something like:
```
[
  {
    "objectId": "ZTF17aaagaie",
    "gmag": 11.4319
  },
  {
    "objectId": "ZTF18aaadvxy",
    "gmag": 11.8582
  },
.... ]
```

In order to make an API query that involves a watchlist (or watchmap), first find its ID, the number at the end of the URL when you click through to your watchlist.
For example [watchlist 139](https://lasair-ztf.lsst.ac.uk/watchlists/139/) is named 'E+A galaxies'. Now add to the `selected` and `tables` variables like this:
```
selected = 'objects.objectId, watchlist_hits.name, watchlist_hits.arcsec'
tables   = 'objects,watchlists:139'
```
which returns the name of the associated watchlist entry and its distance in arcseconds.

It is also possible to query the JSON dictionary associated with an annotator. See the section [filtering on an annotator](core_functions/make_filter.html#filtering-on-an-annotator).




### <a name="object"></a>object

This method returns a machine-readable version of the information on a named object, which replicates the information on the object page of the web server. The arguments are:

*   `objectId`: an objectId for which data is wanted
*   `lasair_added`: Set to 'true' to get the lasair added information such as sherlock, cutout URLs, etc
*   `lite`: set to 'True' to get all attributes, including extended (default False).

Example:
```
import lasair
token = 'xxxxxxxxxxxxxxxxxxxxxxxx'
L = lasair.lasair_client(token)
c = L.object(objectId)
print(c)
```
and the return something like this:
```
{"objectId":"ZTF18abdphvf",
"objectData":{
    "ncand":8,
    "ramean":293.54591006249996,
    "decmean":49.429229975,
    "glonmean":81.77021010499132,
    "glatmean":13.829346704017533,
.... }
```

The data includes everything on the object page, including the object and candidates, as well as the Sherlock and TNS information. The candidate section has bot detections, that have a `candid` attribute, and the much smaller non-detections (upper limits). Each candidate has links to the cutout images that are shown on the object web page. A complete example is [shown here](ZTF23aabplmy.html).

Note that `lite=True` and `lasair_added=False` returns the lightcurve of the object.

### <a name="sherlockobject"></a>sherlock_object

This method returns Sherlock information for a named object, either the "lite" record that is also in the Lasair database, or the full record including many possible crossmatches. The arguments are:

*   `objectIds`: an objectId
*   `lite`: Set to 'true' to get the lite information only

Example
```
import lasair
token = 'xxxxxxxxxxxxxxxxxxxxxxxx'
L = lasair.lasair_client(token)
c = L.sherlock_object('ZTF20acgrvqo)
print(c)
```
and the return is something like:
```
{
    "classifications": {
        "ZTF20acpwljl": [
            "SN",
            "The transient is possibly associated with <em><a href='http://skyserver.sdss.org/dr12/en/tools/explore/Summary.aspx?id=1237673709862061782'>SDSS J081931-060114.9</a></em>; a J=17.01 mag galaxy found in the SDSS/2MASS/PS1 catalogues. It's located 1.09 arcsec N, 1.11 arcsec W from the galaxy centre."
        ]
    },
    "crossmatches": [
        {
            "catalogue_object_id": "1237673709862061782",
            "J": 17.007,
            "JErr": 0.215,
            "H": 15.974,
            "HErr": 0.179,
            "K": 15.389,
```
### <a name="sherlockposition"></a>/api/sherlock/position/

This method returns Sherlock information for an arbitrary position in the sky, either the "lite" record that is also in the Lasair database, or the full record including many possible crossmatches. It is meant as an illustration of what Sherlock can do. If you would like to use Sherlock for high volume work, please [Email Lasair-help](mailto:lasair-help@mlist.is.ed.ac.uk?subject=sherlock). The arguments are:

*   `ra`: Right ascension of a point in the sky in degrees
*   `dec`: Declination of a point in the sky in degrees
*   `lite`: Set to 'true' to get the lite information only

Example:
```
import lasair
token = 'xxxxxxxxxxxxxxxxxxxxxxxx'
L = lasair.lasair_client(token)
c = L.sherlock_position('ZTF20acgrvqo')
print(c)
```
and the return is something like:
```
status= 200
{
  "classifications": {
    "query": [
      "VS",
      "The transient is synonymous with
```

