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
(the API), another shows how to use the real-time Kafka output from 
active filters, and another shows how the lightcurve features are 
built that can be used to make a Lasair filter.

### 2. Get your token

* You need a Lasair login.  There is a video [How to get a Lasair 
account](https://www.youtube.com/watch?v=ekjl5DpLV_Q) that 
explains how to do this, or just go [here]({%lasairurl%}/register). 
Then log in to the Lasair website.
* Click on your username at the top right and select "My Profile", then copy the token.
* You can go to `notebook/API_lsst` or `features`.
* Look in the repo for the `settings_template.py` and copy it to 
`settings.py` then edit it with your own token.

### 3. Libraries
Install the lasair client with `pip3 install lasair`.
Install matplotlib with `pip3 install matplotlib`.

----
Now you can run the notebooks with your favourite Jupyter client. 
The root of the tree is [here](https://github.com/lsst-uk/lasair-examples/tree/main/lsst_notebooks).
They are described below.

## [api](https://github.com/lsst-uk/lasair-examples/tree/main/lsst_notebooks/api)
Shows how to use the Lasair API.
Please note that usage of the Lasair API is throttled by default to 10 requests per hour. If you get an error message about this, you can [email Lasair-help](mailto:lasair-help@mlist.is.ed.ac.uk?subject=throttling problem), explain what you are doing, and you will be put into the “Power Users” category. 
### [api/cone.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/lsst_notebooks/api/cone.ipynb)
The cone search method of the API finds objects within a cone, i.e. a point in the sky and radius in arcseconds. It can return:
- A count of the number in the cone
- - The nearest of those in the cone
All of those in the cone
### [api/object.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/lsst_notebooks/api/object.ipynb)
For a given object, identified by its diaObjectId, the object API call has two additional arguments:
`lasair_added`: True if you want the attributes that Lasair computes the attributes in the schema, as well as the Sherlock association, TNS crossmatch, and links to all the image cutouts.
`lite`: True if you want the simplified version that is usually sufficient, or False if you want the large number of attributes that Rubin has supplied.
### [api/query.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/lsst_notebooks/api/query.ipynb)
This notebook runs a Lasair filter using three strings: selected, 'tables', and 'conditions', as in the web interface. In this case we just fina a few objects that have a Sherlock host association.
### [api/sherlock_api](https://github.com/lsst-uk/lasair-examples/blob/main/lsst_notebooks/api/sherlock_api.ipynb)
Demonstrates the two Sherlock calls: one by diaObjectId and the other by sky position ra, dec.
### [api/watchlist](https://github.com/lsst-uk/lasair-examples/blob/main/lsst_notebooks/api/watchlist.ipynb)
This notebook runs a Lasair filter that includes a watchlist.
## [Kafka](https://github.com/lsst-uk/lasair-examples/tree/main/lsst_notebooks/kafka)
Shows how to consume Kafka from your active filter.
### [kafka/consume.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/lsst_notebooks/kafka/consume.ipynb)
Shows how to consume Kafka and print the results. You will need to change the topic to the one listed in the webpage for your active filter.
### [kafka/consume_plot.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/lsst_notebooks/kafka/consume_plot.ipynb)
Shows how to consume Kafka and plot the results. We assume the filter is saved with the option 'lightcurve_lite'. You will need to change the topic to the one listed in the webpage for your active filter.
## [features](https://github.com/lsst-uk/lasair-examples/tree/main/lsst_notebooks/features)
Shows how some of the Lasair added value is made.
### [features/jump.ipynb](https://github.com/lsst-uk/lasair-examples/tree/main/lsst_notebooks/features/jump.ipynb)
This simple feature is to filter out lightcurves with a significant change in brightness. The mean and standard deviation are computed from the time between 70 days ago and 10 days ago. Then the difference between the latest flux and the mean is divided by the standard deviation: this is jump1. The same is computed for the other 5 flux bands: this is jump2. If there is a true jump in brightness, we can expect both jump1 and jump2 to be larger than several sigma.
### [features/milky_way.ipynb](https://github.com/lsst-uk/lasair-examples/tree/main/lsst_notebooks/features/milky_way.ipynb)
Calculation of the extinction E(B-V) and the galactic latitude. To run this notebook, you will need to install the dustmaps package that puts a 64 Mbyte file on your system.
### [features/pair_analysis.ipynb](https://github.com/lsst-uk/lasair-examples/tree/main/lsst_notebooks/features/pair_analysis.ipynb)
The Rubin cadence includes the same object in different wavebands only ~30 minutes apart, so it is possible to separate rapid brightening from colour. While the actual colour is reported (eg magnitude difference is 0.99 between filters g and r), this is also converted to an effective temperature using the blackbody model.
### [features/sherlock_feature.ipynb](https://github.com/lsst-uk/lasair-examples/tree/main/lsst_notebooks/features/sherlock_feature.ipynb)
The Sherlock system classifies each Lasair alert based on its location in the sky, finding previously catalogued objects such as variable stars and host galaxy. In this notebook, we see all the crossmatches that sherlock finds, and plots them in position relative to the original alert.
### [features/bazinBlackBody](https://github.com/lsst-uk/lasair-examples/tree/main/lsst_notebooks/features/bazinBlackBody)
For alerts with a Sherlock host galaxy, a two-dimensional fit is made in both time and wavelength to look for fast risers and discern their colour. There are several notebooks in the directory.
#### [features/bazinBlackBody/introduction.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/lsst_notebooks/features/bazinBlackBody/introduction.ipynb)
Start here to see what precisely this code it doing. It is fitting a 2D surface to the lightcurve, with time in one dimension and wavelength in the other. The fit to the flux can be either exponential in time (linear in magnitude), or with a Bazin explosion model -- exponential rise in flux then exponential fall.
#### [features/bazinBlackBody/example.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/lsst_notebooks/features/bazinBlackBody/example.ipynb)
This notebook reads a simulated supernova lightcurve from a file, then fits it and plots the result.
#### [features/bazinBlackBody/synthetic.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/lsst_notebooks/features/bazinBlackBody/synthetic.ipynb)
This notebook creates a BazinBlackbody lightcurve surface, then fits it and plots the result.
#### [features/bazinBlackBody/api_plot_lsst.ipynb](https://github.com/lsst-uk/lasair-examples/blob/main/lsst_notebooks/features/bazinBlackBody/api_plot_lsst.ipynb)
This notebook runs the fit for an arbitrary object in the Lasair database. To see the result for another object, change the 2nd last line of the notebook where it says `diaObjectId = ...` to the `diaObjectId` of your chosen object.

Please also [Contact us](mailto:lasair-help@mlist.is.ed.ac.uk?subject=Notebooks) with any notebooks that you would like to share.
