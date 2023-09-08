"""
REST service to handle Sherlock requests
"""

from flask import Flask, request, jsonify
import re
import yaml
import pymysql.cursors
from sherlock import transient_classifier

app = Flask(__name__)

conf = {
        'settings_file': 'sherlock_service_settings.yaml',
        'sherlock_settings': 'sherlock_settings.yaml'
        }

class NotFoundException(Exception):
    pass

# run the sherlock classifier
def classify(name,ra,dec,lite=False):
    with open(conf['sherlock_settings'], "r") as f:
        sherlock_settings = yaml.safe_load(f)
        classifier = transient_classifier(
            log=app.logger,
            settings=sherlock_settings,
            ra=ra,
            dec=dec,
            name=name,
            verbose=1,
            updateNed=False,
            lite=lite
        )
        classifications, crossmatches = classifier.classify()
        return classifications, crossmatches

# look up the dec and ra for a name
def lookup(names):
    ra = []
    dec = []
    with open(conf['settings_file'], "r") as f:
        settings = yaml.safe_load(f)
        connection = pymysql.connect(
            host=settings['database']['host'],
            port=settings['database']['port'],
            user=settings['database']['username'],
            password=settings['database']['password'],
            db=settings['database']['db'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor)        
        for name in names:
            query = "SELECT ra,decl FROM objects WHERE diaObjectID='{}'".format(name)
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                if result:
                    ra.append(result['ra'])
                    dec.append(result['decl'])
                else:
                    raise NotFoundException("Object {} not found".format(name))
        connection.close()
        return ra, dec

@app.route("/object/<string:name>", methods=['GET', 'POST'])
def object(name=""):
    """
    Get the Sherlock crossmatch results for a named object.

    Parameters:
        lite (boolean): produce top ranked matches only. Default False.
    """

    lite = str(request.args.get("lite", ""))
    if request.is_json:
        lite = str(request.json.get("lite", ""))
    if str(lite).casefold() == "lite":
        is_lite = True
    else:
        is_lite = False

    names = name.split(',')
    try:
        ra, dec = lookup(names)
    except NotFoundException as e:
        return {"message":str(e)}, 404

    classifications, crossmatches = classify(names, ra, dec, is_lite)
    result = {
        'classifications': classifications,
        'crossmatches': crossmatches
        }
    return result, 200

@app.route("/query", methods=['GET', 'POST'])
def query():
    """
    Run Sherlock for a given position.

    Parameters:
        name (string): Name of object. Optional.
        ra (float): right ascension. Required.
        dec (float): declination. Required.
        lite (boolean): produce top ranked matches only. Default False.
    """

    # get input
    name = str(request.args.get("name", ""))
    lite = str(request.args.get("lite", ""))
    ra = str(request.args.get("ra", ""))
    dec = str(request.args.get("dec", ""))
    if request.is_json:
        name = str(request.json.get("name", ""))
        lite = str(request.json.get("lite", ""))
        ra = str(request.json.get("ra", ""))
        dec = str(request.json.get("dec", ""))

    # validate input
    if not re.search("^[\w\-\+,]*$", name):
        return "Error parsing parameter name", 400
    if str(lite).casefold() == "lite":
        is_lite = True
    else:
        is_lite = False
    if not ra:
        return "Missing required parameter ra", 400
    if not re.search("^[0-9\.,]*$", ra):
        return "Error parsing parameter ra", 400
    if not dec:
        return "Missing required parameter dec", 400
    if not re.search("^[0-9\.,\-]*$", dec):
        return "Error parsing parameter dec", 400

    # split lists
    ra = ra.split(",")
    dec = dec.split(",")

    if len(ra) != len(dec):
        return "ra and dec lists must be equal length", 400

    # fill in names if not present
    if name == "":
        name = []
        for i in range(len(ra)):
            name.append("query"+str(i))
    else:
        name = name.split(",")

    if len(ra) != len(name):
        return "name list incorrect length", 400

    # run Sherlock
    classifications, crossmatches = classify(
            name,
            ra,
            dec,
            lite=is_lite)
    result = {
            'classifications': classifications,
            'crossmatches': crossmatches
            }

    return result, 200

if (__name__ == '__main__'):
    app.run(debug=True, port=5000)
