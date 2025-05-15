# Python Notebooks

In order to use the example notebooks, please DO NOT just download and run
a single notebook. There are other files that the notebooks will expect 
to find, and it will fail when these are not present.

**Please follow the instructions below**.

### 1. Clone the repo
There is a separate Lasair repo for jupyter notebooks. To begin, download the repo with:
```
git clone https://github.com/lsst-uk/lasair-examples.git
```
One branch is a set of notebooks showing how the Lasair client works 
(the API), and the other is a "Marshall" to enable viewing, 
vetoing and favouriting objects that pass through a kafka-enabled filter.

### 2. Get your token

* You need a Lasair login.  There is a video [How to get a Lasair 
account](https://www.youtube.com/watch?v=ekjl5DpLV_Q) that 
explains how to do this, or just go [here]({%lasairurl%}/register). 
Then log in to the Lasair website.
* Click on your username at the top right and select "My Profile", then copy the token.
* You can go to `notebooks/API_ztf` or `notebooks/LSST-ztf` or `notebooks/marshall`.
* Look in the repo you cloned for the `settings_template.py` and copy it to 
`settings.py` then edit it with your own token.

### 3. Lasair client
Install the lasair client with `pip3 install lasair`.

### 4. When will the alerts start?
As of this writing (May 2025), LSST has not begun operation, and there is only
fake data, and not much of that. Many of the filters will return nothing. 
Come back after the data starts flowing.

----
Now you can run the notebooks with your favourite Jupyter client. 
They are described bwlow.

#### [API_lsst/BrightSNe.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/API_lsst/BrightSNe.ipynb)
* Pulls out alerts with a Sherlock host galaxy, and plots lightcurves.

#### [API_lsst/Cone_Search.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/API_lsst/Cone_Search.ipynb)
* Uses the Lasair cone_search method to find objects near a given point in the sky.

#### [API_lsst/ObjectAPI.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/API_lsst/ObjectAPI.ipynb)
* Shows the different amounts of data from the `object` API call, the result of the two flags:
    * `lasair_added`: Content added by Lasair
    * `lite`: Just the essentials

#### [API_lsst/Query_NEEDLE_Annotations.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/API_lsst/Query_NEEDLE_Annotations.ipynb)
* Illustrates the use of the `JSON_EXTRACT` clause in SQL.

#### [API_lsst/Query_Watchlist.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/API_lsst/Query_Watchlist.ipynb)
* Illustrates how to write a query in the API that includes a watchlist

#### [features/1_whatIsAnObject.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/features/1_whatIsAnObject.ipynb)
* From the alert packet sent through the Lasair system,
the 3 cutout images are removed, and the remainder converted to JSON. 
All the original content is preserved. Here we see some examples of the three main data packets:

    * diaObject: Properties of the astrophysical object such as lightcurve features and proper motion
    * diaSource: Each represents a detection of an object that is >5 sigma from the reference
    * diaForcedSource; Each represents a detection of an object

#### [features/2_sherlock.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/features/2_sherlock.ipynb)

#### [features/3_jumpFromMean.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/features/3_jumpFromMean.ipynb)
Shows the construction of a "jump finder". Number of sigma for latest
detection above its mean/sigms between 70 and 10 days ago.

#### [features/4_milky_way.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/features/4_milky_way.ipynb)
* Galactic latitude
* E(B-V) extinction
* Absolute magnitude

#### [features/5_pair.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/features/5_pair.ipynb)

#### [features/6_bazinBlackBody.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/features/6_bazinBlackBody.ipynb)
How to use the BBB package to analyse light curves

#### [features/7_periodFinder.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/features/7_periodFinder.ipynb)
Finding a period from a lightcurve

#### [marshall/Marshall.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/marshall/Marshall.ipynb)
This Jupyter notebook allows you to view the output from a Lasair filter, to link to more information, and to either make it a favourite or veto it so it won't be shown again.
The brief instructions for using the Marshall are [at the github page](https://github.com/lsst-uk/lasair-examples/tree/main/notebooks/marshall), and 
[there is a video](https://youtu.be/sgH5cQk-TDU) about how to use it.

#### [Test_Consumers.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/Test_Consumers.ipynb)
Illustrates how to consume a stream that is the output of an active
Lasair filter.

#### [Test_Query_Methods.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/notebooks/Test_Query_Methods.ipynb)
Illustrates how to consume a stream that is the output of an active
Lasair filter.

Usage of the Lasair API is throttled by default to 10 requests per hour. If you get an error message about this, you can [email Lasair-help](mailto:lasair-help@mlist.is.ed.ac.uk?subject=throttling problem), explain what you are doing, and you will be put into the “Power Users” category. 

Please also [Contact us](mailto:lasair-help@mlist.is.ed.ac.uk?subject=Notebooks) with any notebooks that you would like to share.
