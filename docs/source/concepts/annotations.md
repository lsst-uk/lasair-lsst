# Annotations

Lasair allows users to add information to the database, that can then be used
as part of a query by another user. Each *annotation* is associated with a 
specific Lasair object, and with a specific *annotator*, and may 
contain:

* `objectId`: the Lasair object being annotated
* `topic`: the name of the annotator that produced this annotation
* `classification`: a short string drawn from a fixed vocabulary, eg "kilonova".
* `explanation`: a natural language explanation of the classification, eg “probable kilonova but could also be supernova”
* `classjson`: the annotation information expressed as a JSON dictionary
* `url`: a URL where more information can be obtained, for example
a spectrum of the object obtained by follow-up.

The `classification` is easy to query: it is just a word; but the `classjson` 
can hold complex information and querying is more sophisticated.

Annotations can be pushed to the Lasair database using the Lasair client,
however the user must be authenticated to do so. Lasair staff are happy to 
receive a request to create an annotator, and the successful user
will be given a `topic` name that allows them to upload annotations.

## Cookbook

For instructions on how to run your own annotator, see [Making an Annotator](../core_functions/make_annotator.html).

