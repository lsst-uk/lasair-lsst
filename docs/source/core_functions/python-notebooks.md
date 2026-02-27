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
### 2. Get your token

* You need a Lasair login.  There is a video [How to get a Lasair 
account](https://www.youtube.com/watch?v=ekjl5DpLV_Q) that 
explains how to do this, or just go [here]({%lasairurl%}/register). 
Then log in to the Lasair website.
* Click on your username at the top right and select "My Profile", then copy the token.
* Put your token into your Unix environment as `LASAIR_LSST_TOKEN`. Run the `env` command to make sure its there.

- Libraries
    - Install the lasair client with `pip3 install lasair`.
    - Install matplotlib with `pip3 install matplotlib`.
    - Now you can run the notebooks with your favourite Jupyter client. 
The root of the tree is [here](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/).
They are described below.
----
### Learn Lasair
- [Using the Lasair API](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/tutorials/API_recipes.ipynb): **Learn how to use the Lasair API.**
- [Using the Lasair Kafka system](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/tutorials/KAFKA_Listen_to_Alerts.ipynb): **Learn how to consume Kafka from an active filter.**
- [What is a Lasair Object](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/tutorials/What_is_an_Object.ipynb): Learn about the data associated with a Lasair object.

### Inspect object
- [See all the cutouts](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/notebooks/cutouts.ipynb): Shows all the cutout images for a given object in Lasair
- [Plot the BBB fit for an object](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/features/bazinBlackBody/api_plot_lsst.ipynb): This notebook runs the fit for an arbitrary object in the Lasair database. To see the result for another object, change the 2nd last line of the notebook where it says `diaObjectId = ...` to the `diaObjectId` of your chosen object.

### Little notebooks
- [Cone search](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/notebooks/cone.ipynb): The cone search method of the API finds objects within a cone, i.e. a point in the sky and radius in arcseconds. It can return:
    - A count of the number in the cone
    - The nearest of those in the cone
    - All of those in the cone
- [Object API method](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/notebooks/object.ipynb): For a given object, identified by its diaObjectId, the object API call has two additional arguments:
    - `lasair_added`: True if you want the attributes that Lasair computes the attributes in the schema, as well as the Sherlock association, TNS crossmatch, and links to all the image cutouts.
    - `lite`: True if you want the simplified version that is usually sufficient, or False if you want the large number of attributes that Rubin has supplied.
- [Database query](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/notebooks/query.ipynb): This notebook runs a Lasair filter using three strings: selected, 'tables', and 'conditions', as in the web interface. In this case we just fina a few objects that have a Sherlock host association.
- notebooks/sherlock_api.ipynb]: Demonstrates the two Sherlock calls: one by diaObjectId and the other by sky position ra, dec.
- [Query with watchlist](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/notebooks/watchlist.ipynb): This notebook runs a Lasair filter that includes a watchlist.
- [Consume Kafak](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/notebooks/consume_kafka.ipynb): Shows how to consume Kafka from your active filter.
- [Consume Kafka and plot](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/notebooks/consume_kafka_plot.ipynb): Shows how to consume Kafka and print the results. You will need to change the topic to the one listed in the webpage for your active filter.

### Little scripts
- [Consume Kafka](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/scripts/kafka_consumer.py): Small python code to consume (read) a kafka stream from an active filter
- [Annotate](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/scripts/annotator.py): Small python code to consume (read) a kafka stream from an active filter that has the `lightcurve_lite` mode, an plot the lightcurve.

### Lasair Features
Shows how some of the Lasair added value is made.
- [Jump Feature](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/features/jump.ipynb):
This simple feature is to filter out lightcurves with a significant change in brightness. The mean and standard deviation are computed from the time between 70 days ago and 10 days ago. Then the difference between the latest flux and the mean is divided by the standard deviation: this is jump1. The same is computed for the other 5 flux bands: this is jump2. If there is a true jump in brightness, we can expect both jump1 and jump2 to be larger than several sigma.
- [Extinction and galactic latitude](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/features/milky_way.ipynb): Calculation of the extinction E(B-V) and the galactic latitude. To run this notebook, you will need to install the dustmaps package that puts a 64 Mbyte file on your system.
- [Effective temperature from Pairs](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/features/pair_analysis.ipynb): The Rubin cadence includes the same object in different wavebands only ~30 minutes apart, so it is possible to separate rapid brightening from colour. While the actual colour is reported (eg magnitude difference is 0.99 between filters g and r), this is also converted to an effective temperature using the blackbody model.
- [Sherlock dive](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/features/sherlock_feature.ipynb): The Sherlock system classifies each Lasair alert based on its location in the sky, finding previously catalogued objects such as variable stars and host galaxy. In this notebook, we see all the crossmatches that sherlock finds, and plots them in position relative to the original alert.
- [Bazin black body fitting](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/features/bazinBlackBody): For alerts with a Sherlock host galaxy, a two-dimensional fit is made in both time and wavelength to look for fast risers and discern their colour. There are several notebooks in the directory.
   - [Introduction)(https://github.com/lsst-uk/lasair-examples/blob/merge/HS/features/bazinBlackBody/introduction.ipynb): Start here to see what precisely this code it doing. It is fitting a 2D surface to the lightcurve, with time in one dimension and wavelength in the other. The fit to the flux can be either exponential in time (linear in magnitude), or with a Bazin explosion model -- exponential rise in flux then exponential fall.
   - [Example](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/features/bazinBlackBody/example.ipynb): This notebook creates a BazinBlackbody lightcurve surface, then fits it and plots the result.
   - [Synthetic light curve](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/features/bazinBlackBody/synthetic.ipynb): This notebook reads a simulated supernova lightcurve from a file, then fits it and plots the result.
   - [Plot for arbitrary object](https://github.com/lsst-uk/lasair-examples/blob/merge/HS/features/bazinBlackBody/api_plot_lsst.ipynb): This notebook runs the fit for an arbitrary object in the Lasair database. To see the result for another object, change the 2nd last line of the notebook where it says `diaObjectId = ...` to the `diaObjectId` of your chosen object.

Please also [Contact us](mailto:lasair-help@mlist.is.ed.ac.uk?subject=Notebooks) with any notebooks that you would like to share.
