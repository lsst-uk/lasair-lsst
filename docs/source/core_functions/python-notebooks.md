# Python Notebooks

There is a separate Lasair repo for jupyter notebooks. To begin, lets the repo with:
```
git clone https://github.com/lsst-uk/lasair-examples.git
```
One branch is a set of notebooks showing how the Lasair client works (the API), and the other is a "Marshall" to enable viewing, vetoing and favouriting objects that pass through a kafka-enabled filter.

## Clone the repo and get your token
* You need a Lasair login.  There is a video [How to get a Lasair account](https://www.youtube.com/watch?v=ekjl5DpLV_Q) that explains how to do this, or just go [here]({%lasairurl%}/register). Then log in to the Lasair website.
* Click on your username at the top right and select "My Profile", then copy the token.
* You can go to `notebooks/API_examples` or `notebooks/marshall`. In each case, make a file called `settings.py` with the single line `API_TOKEN='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'`, where the `xxx` is the token for your account.
* Install the lasair client with `pip3 install lasair`.

## API_examples

The notebooks are:
### Using the query and lightcurve methods
#### Cone_Search.ipynb
Uses the Lasair cone_search method to find objcts near a given point in the sky.

#### BrightSNe.ipynb
Runs a query on the Lasair objects table and the Sherlock table to extract possible supernovae, then fetches lightcurves and plots them.

#### SN_Like_Candidates.ipynb
Runs a query on the Lasair objects table and the Sherlock table to extract possible supernovae, then fetches lightcurves and plots them.

#### TDE_candidates.ipynb
A sophisticated gathering of information from Lasair, the Transient Naming Service, and PanStarrs cutout images.

### Querying with Join
#### Query_Watchlist.ipynb
A simple notebook to jointly query objects and a watchlist.

#### Get_Watchlist_and_Area_Hits.ipynb
Shows how to use the Lasair API query method to search the objects, a watchlist, and a watchmap jointly.

#### Query_Fastfinder_Annotations.ipynb
Shows how to use the Lasair API query method to search quantities uploaded as annotations.

### Using the Sherlock methods
#### Sherlock.ipynb
How to use the Sherlock API to fetch sky context information about a Lasair object, or about an arbitrary position in the sky.

### Fetching Kafka
#### Fetch_kafka.ipynb
Fetches alerts that have passed through a kafka-enabled filter, using the kafka consumer.

Usage of the Lasair API is throttled by default to 10 requests per hour. If you get an error message about this, you can [email Lasair-help](mailto:lasair-help@lists.roe.ac.uk?subject=throttling problem), explain what you are doing, and you will be put into the “Power Users” category. 

Please also [Contact us](mailto:lasair-help@lists.roe.ac.uk?subject=Notebooks) with any notebooks that you would like to share.

## Marshall Notebook

This Jupyter notebook allows you to view the output from a Lasair filter, to link to moreinformation, and to either make it a favourite or veto it so it won't be shoen again.
The brief instructions for using the Marshall are [at the github page](https://github.com/lsst-uk/lasair-examples/tree/main/notebooks/marshall), and 
[there is a video](https://youtu.be/sgH5cQk-TDU) about how to use it.

