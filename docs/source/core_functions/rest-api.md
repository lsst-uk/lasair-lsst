# Lasair API

The Lasair-Sherlock API allows developers to run queries and cone-searches, to see outputs from streaming queries, and to query the Sherlock sky-context system.

#### Ways to use the API

In addition to the Lasair client, you can
uses either HTTP GET or POST. Arguments can be passed in the query string, as JSON or form encoded. Responses are JSON. There is a throttling system in the backend: users with an account get up to 100 calls per hour, but "power" users get up to 10,000 calls per hour. If you wish your account to be upgraded to power user, 
[email Lasair-help](mailto:lasair-help@mlist.is.ed.ac.uk?subject=power user)

The examples below show how to drive the API with either GET URL, POST curl or python with the 'lasair' package. The URL should be pasted into a web browser. The curl script pasted into a terminal window, and the python code copied into a file and executed as a python program.

#### Throttling of API Usage

The Lasair API counts numbers of calls on a per-user basis, and restricts the number that can be executed in any hour time period. There are also restrictions on the number of rows that can be returned by the 'query' method. To use the API with less throttling, please get your own token from your Lasair account, as explained below "Get Your Token". If you would like to use the system for serious work, please [email Lasair-help](mailto:lasair-help@mlist.is.ed.ac.uk?subject=throttling problem), explain what you are doing, and you will be put into the "Power Users" category. The limits for these three categories of user are:

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
*   [/api/object/](#object): returns a machine-readable version of the object web page.
*   [/api/sherlock/object/](#sherlockobject): returns Sherlock information about a named objects.
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
The return has object identifiers, and their separations in arcseconds, something like:
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
### <a name="object"></a>/api/object/

This method returns a machine-readable version of the information on a named object. If `lasair_added` is `True`, it replicates the information on the object page of the web server, otherwise just returns the lightcurve as a list if `candidate`s. The arguments are:

*   `objectId`: an objectId for which data is wanted
*   `lasair_added`: a boolean, if the lasair added data is wanted

GET URL Example
```
https://lasair-ztf.lsst.ac.uk/api/object/?objectId=ZTF18abdphvf&token=xxxxxxxxxxxxxxxxxxxxxxxx&format=json
```
Curl Example: The API key goes in the header of the request, and the data in the data section.
```
curl --header "Authorization: Token xxxxxxxxxxxxxxxxxxxxxxxx" --data "objectId=ZTF18abdphvf" https://lasair-ztf.lsst.ac.uk/api/object/
```
and the return something like this:
```
status= 200
{"objectId":"ZTF18abdphvf",
"objectData":{
    "ncand":8,
    "ramean":293.54591006249996,
    "decmean":49.429229975,
    "glonmean":81.77021010499132,
    "glatmean":13.829346704017533,
.... }
}
```

The data includes everything on the object page, including the object and candidates, as well as the Sherlock and TNS information. The candidate section has bot detections, that have a `candid` attribute, and the much smaller non-detections (upper limits). Each candidate 
has links to the cutout images that are shown on the object web page. A complete example
is [shown here](ZTF23aabplmy.html).

### <a name="sherlockobject"></a>/api/sherlock/object/

This method returns Sherlock information for a named objects, either the "lite" record that is also in the Lasair database, or the full record including many possible crossmatches. The arguments are:

*   `objectIds`: a comma-separated list of objectIds, maximum number is 10
*   `lite`: Set to 'true' to get the lite information only

GET URL Example with object
```
https://lasair-ztf.lsst.ac.uk/api/sherlock/object/?objectId=ZTF20acpwljl&token=xxxxxxxxxxxxxxxxxxxxxxxx&lite=true&format=json
```
Curl Example with list of objects: The authorization token goes in the header of the request, and the data in the data section.
```
curl --header "Authorization: Token xxxxxxxxxxxxxxxxxxxxxxxx" --data "objectId=ZTF20acpwljl&lite=True" https://lasair-ztf.lsst.ac.uk/api/sherlock/object/
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

This method returns Sherlock information for an arbitrary position in the sky, either the "lite" record that is also in the Lasair database, or the full record including many possible crossmatches. It is meant as an illustration of what Sherlock can do. If you would like to use Sherlock for high volume work, please [Email Lasair-help](mailto:lasair-help@mlist.is.ed.ac.uk?subject=sherlock). The arguments are:

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
