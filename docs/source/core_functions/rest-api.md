# Lasair API and Client

The Lasair-Sherlock API allows developers to run queries and cone-searches, to see outputs from streaming queries, and to query the Sherlock sky-context system.

#### Ways to use the API

The Lasair API uses either HTTP GET or POST. Arguments can be passed in the query string, as JSON or form encoded. Responses are JSON. There is a throttling system in the backend: users with an account get up to 100 calls per hour, but "power" users get up to 10,000 calls per hour. If you wish your account to be upgraded to power user, 
[email Lasair-help](mailto:lasair-help@lists.roe.ac.uk?subject=power user)

The examples below show how to drive the API with either GET URL, POST curl or python with the 'lasair' package. The URL should be pasted into a web browser. The curl script pasted into a terminal window, and the python code copied into a file and executed as a python program.

#### Throttling of API Usage

The Lasair API counts numbers of calls on a per-user basis, and restricts the number that can be executed in any hour time period. There are also restrictions on the number of rows that can be returned by the 'query' method. To use the API with less throttling, please get your own token from your Lasair account, as explained below "Get Your Token". If you would like to use the system for serious work, please [email Lasair-help](mailto:lasair-help@lists.roe.ac.uk?subject=throttling problem), explain what you are doing, and you will be put into the "Power Users" category. The limits for these three categories of user are:

*   User token (see 'Get Your Token') below: 100 API calls per hour, maximum 10,000 rows from query.
*   Power user token (on request): 10,000 API calls per hour, maximum 1,000,000 rows from query.

**Note: WE ASK YOU TO PLEASE NOT SHARE THESE TOKENS.** If you share code that uses the Lasair API, please put the token in a separate, imported file or environment variable, that you do not share, and is not put in github.

##### Authorisation Token

Request authentication is via the API key. For GET queries, the key can go in the parameter string, and for POST queries, the key goes in the headers. In the following, the string of xxxxxxxxxxxxxx characters should be replaced by your own key.

##### Get Your Token

Once you are logged in on the website, click on your name at the top right, and choose "My Profile". The API key is shown there.

#### Methods

Click on the method name to jump to documentation in the reference below.

*   [/api/cone/](#cone): runs a cone search on all the objects in the Lasair database.
*   [/api/query/](#query): runs a SQL SELECT query on the Lasair database.
*   [/api/streams/](#streams): returns a record of the output from a Lasair streaming query.
*   [/api/objects/](#objects): returns a machine-readable version of the object web page.
*   [/api/lightcurves/](#lightcurves): returns simple lightcurves for a number of objects.
*   [/api/sherlock/objects/](#sherlockobjects): returns Sherlock information about a list of named objects.
*   [/api/sherlock/position/](#sherlockposition): returns Sherlock information about a sky position.

### <a name="cone"></a>/api/cone/

This method runs a cone search on all the objects in the Lasair database. The arguments are:

*   `ra`: (float) the right ascension in decimal degrees,
*   `dec`: (float) the declination in decimal degrees,
*   `radius`: (float) the angular radius of the cone in arcseconds, the maximum being 1000 arcseconds.
*   `requestType`: (string) the type of request, which can be:
    *   `nearest`: returns only the nearest objects within the cone
    *   `all`: returns all the objects within the cone
    *   `count`: returns the number of objects within the cone

GET URL Example
```
https://lasair-ztf.lsst.ac.uk/api/cone/?&ra=194.494&dec=48.851&radius=240.0&requestType=all&token=xxxxxxxxxxxxxxxxxxxxxxxx&format=json
```
Curl Example: The API key (token) goes in the header of the request, and the data in the data section.
```
curl --header "Authorization: Token xxxxxxxxxxxxxxxxxxxxxxxx" --data "ra=194.494&dec=48.851&radius=240.0&requestType=all" https://lasair-ztf.lsst.ac.uk/api/cone/
```
Python Example: This code requires the `lasair` library.
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
### <a name="query"></a>/api/query/

This method runs a query on the Lasair database. There is an [interactive query builder](/query), and a [schema description](/schema). The arguments are:

*   `selected`: (string) the list of attributes to be returned,
*   `tables`: (string) the list of tables to be joined,
*   `conditions`: (string) the "WHERE" criteria to restrict what is returned
*   `limit`: (int) (not required) the maximum number of records to return (default is 1000)
*   `offset`: (int) (not required) offset of record number (default is 0)

GET URL Example
```
https://lasair-ztf.lsst.ac.uk/api/query/?selected=objectId%2Cgmag&tables=objects&conditions=gmag%3C12.0&token=xxxxxxxxxxxxxxxxxxxxxxxx&format=json
```
Curl Example: The authorization token goes in the header of the request, and the data in the data section.
```
curl --header "Authorization: Token xxxxxxxxxxxxxxxxxxxxxxxx" --data "selected=objectId,gmag&tables=objects&conditions=gmag<12.0&limit=3" https://lasair-ztf.lsst.ac.uk/api/query/
```
Python Example: This code requires the `lasair` library.
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
status= 200
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
### <a name="streams"></a>/api/streams/<topic>/ and /api/streams/

This method returns a record of the output from a Lasair streaming query. It represents an alternative to using a Kafka client to fetch from the Kafka server.

If the `topic` URL is provided (with optional `limit`), the contents of the stream are returned. Alternatively, if the topic is not provided, a `regex` argument may be provided, and a list of matching topic names will be returned. A list of all topics can be obtained with the regex `.*` or by omitting the `regex`.

The arguments are:

*   `limit`: (int) (not required) the maximum number of records to return (default 1000)
*   `regex`: (str) (not required) an expression used to select from the set of topics (regular expression)

GET URL Example with Regex
```
https://lasair-ztf.lsst.ac.uk/api/streams/?regex=.%2ASN.%2A&token=xxxxxxxxxxxxxxxxxxxxxxxx&format=json
```
Curl Example with Regex

The authorization token goes in the header of the request, and the data in the data section.
```
curl --header "Authorization: Token xxxxxxxxxxxxxxxxxxxxxxxx" --data "regex=.\*SN.\*" https://lasair-ztf.lsst.ac.uk/api/streams/
```
and the return is a list of topic names, and a URL to get more information:
```
status= 200
[
  {
    "topic": "2SN-likecandidates",
    "more_info": "https://lasair-ztf.lsst.ac.uk/query/2/"
  },
... ]
```
GET URL Example with Topic:
```
https://lasair-ztf.lsst.ac.uk/api/streams/2SN-likecandidates/?limit=1&token=xxxxxxxxxxxxxxxxxxxxxxxx&format=json
```
Curl Example with Topic: The authorization token goes in the header of the request, and the data in the data section. For more information about this stream, see [here](https://lasair-ztf.lsst.ac.uk/query/2/).
```
curl --header "Authorization: Token xxxxxxxxxxxxxxxxxxxxxxxx" --data "2SN-likecandidates&limit=1" https://lasair-ztf.lsst.ac.uk/api/streams/
```
and the return is something like:
```
status= 200
[
  {
    "objectId": "ZTF19abrokxg",
    "ramean": 35.82811567,
    "decmean": -27.79242059,
    "mjdmin": 59134.39827550016,
    "mjdmax": 59164.37175930012,
    "magrmin": 18.33,
    "rmag": 19.4124,
    "classification": "NT",
    "score": "Not Near PS1 star",
    "UTC": "2020-11-11 09:08:49"
  }
]
```
Python Example with Topic: This code requires the `lasair` library.
```
import lasair
token = 'xxxxxxxxxxxxxxxxxxxxxxxx'
L = lasair.lasair_client(token)
print(L.streams_topics())
c = L.streams('2SN-likecandidates', limit=10)
```
and the return is as above with the curl example

### <a name="objects"></a>/api/objects/

This method returns a machine-readable version of the information on a list of objects, which replicates the information on the object page of the web server. The arguments are:

*   `objectIds`: a list of objectIds for which data is wanted

GET URL Example
```
https://lasair-ztf.lsst.ac.uk/api/objects/?objectIds=ZTF18abdphvf,ZTF21aapzzgf&token=xxxxxxxxxxxxxxxxxxxxxxxx&format=json
```
Curl Example: The API key goes in the header of the request, and the data in the data section.
```
curl --header "Authorization: Token xxxxxxxxxxxxxxxxxxxxxxxx" --data "objectIds=ZTF18abdphvf,ZTF21aapzzgf" https://lasair-ztf.lsst.ac.uk/api/objects/
```
Python Example: This code requires the `lasair` library.
```
import lasair
token = 'xxxxxxxxxxxxxxxxxxxxxxxx'
L = lasair.lasair_client(token)
c = L.objects(objectIds)
print(c)
```
and the return something like this:
```
status= 200
[
{"objectId":"ZTF18abdphvf",
"objectData":{
    "ncand":8,
    "ramean":293.54591006249996,
    "decmean":49.429229975,
    "glonmean":81.77021010499132,
    "glatmean":13.829346704017533,
.... }
]
```

The data includes everything on the object page, including the object and candidates, as well as the Sherlock and TNS information. The candidate section has bot detections, that have a `candid` attribute, and the much smaller non-detections (upper limits). Each candidate 
has links to the cutout images that are shown on the object web page. A complete example
is [shown here](ZTF23aabplmy.html).

### <a name="lightcurves"></a>/api/lightcurves/

This method returns simple lightcurves for a number of objects. **NOTE:** these are difference magnitudes from a reference source, not apparent magnitudes. See [this python code](/lasair/static/mag.py) to convert the quantities below to apparent magnitude. Each lightcurve is a sequence of detections, or _candidates_, each of which has the quantities:

*   `candid`: the candidate ID for the detection
*   `fid`: The filter ID for the detection (1 = g and 2 = r)
*   `jd`: Julian Day for the detection
*   `magpsf`: The difference magnitude
*   `sigmapsf`: the error in the difference magnitude.
*   `magnr`: Magnitude of the reference source
*   `sigmagnr`: the error in the reference magnitude
*   `magzpsci`: Zero-point magnitude of the science image
*   `isdiffpos`:set to 't' if positive difference magnitude, 'f' for negative

The arguments are:

*   `objectIds`: (string) comma-separated string of objectIds to be fetched
*   There is a upper limit on the number of lightcurves that can be fetched, currently 50. If you need to do serious data mining on Lasair light curves, please write to [contact the Lasair team](mailto:lasair-help@lists.roe.ac.uk?subject=Notebooks).

GET URL Example
```
https://lasair-ztf.lsst.ac.uk/api/lightcurves/?objectIds=ZTF20acgrvqo%2CZTF19acylwtd%2CZTF18acmziob&token=xxxxxxxxxxxxxxxxxxxxxxxx&format=json
```
Curl Example: The authorization token goes in the header of the request, and the data in the data section.
```
curl --header "Authorization: Token xxxxxxxxxxxxxxxxxxxxxxxx" 
--data "objectIds=ZTF20acgrvqo,ZTF19acylwtd,ZTF18acmziob" 
https://lasair-ztf.lsst.ac.uk/api/lightcurves/
```
Python Example: This code requires the `lasair` library.
```
import lasair
token = 'xxxxxxxxxxxxxxxxxxxxxxxx'
L = lasair.lasair_client(token)
c = L.lightcurves(['ZTF20acgrvqo','ZTF19acylwtd','ZTF18acmziob'])
print(c)
```
and the return is something like:
```
{
  "objectId": "ZTF20acpwljl",
  "candidates":[
    {
      "candid":1961223331015015002,
      "fid":1,
      "magpsf":19.46470069885254,
      "sigmapsf":0.12973499298095703,
      "magnr":21.349000930786133,
      "sigmagnr":0.0989999994635582,
      "magzpsci":26.41069984436035,
      "isdiffpos":"t",
      "jd":2459715.7233333,
    },
    ]
```
### <a name="sherlockobjects"></a>/api/sherlock/objects/

This method returns Sherlock information for a collection of named objects, either the "lite" record that is also in the Lasair database, or the full record including many possible crossmatches. The arguments are:

*   `objectIds`: a comma-separated list of objectIds, maximum number is 10
*   `lite`: Set to 'true' to get the lite information only

GET URL Example with objects
```
https://lasair-ztf.lsst.ac.uk/api/sherlock/objects/?objectIds=ZTF20acpwljl%2CZTF20acqqbkl%2CZTF20acplggt&token=xxxxxxxxxxxxxxxxxxxxxxxx&lite=true&format=json
```
Curl Example with list of objects: The authorization token goes in the header of the request, and the data in the data section.
```
curl --header "Authorization: Token xxxxxxxxxxxxxxxxxxxxxxxx" --data "objectIds=ZTF20acpwljl,ZTF20acqqbkl,ZTF20acplggt&lite=True" https://lasair-ztf.lsst.ac.uk/api/sherlock/objects/
```
Python Example with list of objects: This code requires the `lasair` library.
```
import lasair
token = 'xxxxxxxxxxxxxxxxxxxxxxxx'
L = lasair.lasair_client(token)
c = L.sherlock_objects(['ZTF20acgrvqo','ZTF19acylwtd','ZTF18acmziob'])
print(c)
```
and the return is something like:
```
{
    "ZTF20acpwljl": {
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

This method returns Sherlock information for an arbitrary position in the sky, either the "lite" record that is also in the Lasair database, or the full record including many possible crossmatches. It is meant as an illustration of what Sherlock can do. If you would like to use Sherlock for high volume work, please [Email Lasair-help](mailto:lasair-help@lists.roe.ac.uk?subject=sherlock). The arguments are:

*   `ra`: Right ascension of a point in the sky in degrees
*   `dec`: Declination of a point in the sky in degrees
*   `lite`: Set to 'true' to get the lite information only

GET URL Example
```
https://lasair-ztf.lsst.ac.uk/api/sherlock/position/?ra=16.851866&dec=34.53307&token=xxxxxxxxxxxxxxxxxxxxxxxx&format=json
```

Curl Example: The authorization token goes in the header of the request, and the data in the data section.

```
curl --header "Authorization: Token xxxxxxxxxxxxxxxxxxxxxxxx" --data "ra=16.851866&dec=34.53307" https://lasair-ztf.lsst.ac.uk/api/sherlock/position/
```

Python Example: This code requires the `lasair` library.
```
import lasair
token = 'xxxxxxxxxxxxxxxxxxxxxxxx'
L = lasair.lasair_client(token)
c = L.sherlock_position(['ZTF20acgrvqo','ZTF19acylwtd','ZTF18acmziob'])
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

