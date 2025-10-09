import datetime
import fastavro
import re
import json
from cassandra.cluster import Cluster
from lasair.query_builder import check_query, build_query
from lasair.utils import objjson
import requests
from lasair.lightcurves import lightcurve_fetcher
from cassandra.query import dict_factory
from django.db import IntegrityError
from django.db import connection
from datetime import datetime
from confluent_kafka import Producer, KafkaError
from gkutils.commonutils import coneSearchHTM, FULL, QUICK, CAT_ID_RA_DEC_COLS, base26, Struct
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from src import db_connect
import settings as lasair_settings
import sys
sys.path.append('../common')

CAT_ID_RA_DEC_COLS['objects'] = [['diaObjectId', 'ra', 'decl'], 1018]

REQUEST_TYPE_CHOICES = (
    ('count', 'Count'),
    ('all', 'All'),
    ('nearest', 'Nearest'),
)


class ConeSerializer(serializers.Serializer):
    ra = serializers.FloatField(required=True)
    dec = serializers.FloatField(required=True)
    radius = serializers.FloatField(required=True)
    requestType = serializers.ChoiceField(choices=REQUEST_TYPE_CHOICES)

    def validate_ra(self, value):
        if value > 360 or value < 0:
            raise serializers.ValidationError('ra must be between 0 and 360')
        return value

    def validate_dec(self, value):
        if value > 90 or value < -90:
            raise serializers.ValidationError('dec must be between -90 and 90')
        return value

    def validate_radius(self, value):
        if value < 0:
            raise serializers.ValidationError('radius must be positive')
        return value

    def save(self):

        ra = self.validated_data['ra']
        dec = self.validated_data['dec']
        radius = self.validated_data['radius']
        requestType = self.validated_data['requestType']

        # Get the authenticated user, if it exists.
        userId = 'unknown'
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            userId = request.user

        if radius > 1000:
            replyMessage = "Max radius is 1000 arcsec."
            info = {"error": replyMessage}
            return info

        replyMessage = 'No object found ra=%.5f dec=%.5f radius=%.2f' % (ra, dec, radius)
        info = {"error": replyMessage}

        # Is there an object within RADIUS arcsec of this object? - KWS - need to fix the gkhtm code!!
        message, results = coneSearchHTM(ra, dec, radius, 'objects', queryType=QUICK, conn=connection, django=True, prefix='htm', suffix='')

        if requestType == "nearest":
            if len(results) > 0:
                obj = results[0][1]['diaObjectId']
                separation = results[0][0]
                info = {"nearest": {"object":obj, "separation": separation}}
            else:
                info = {}
        elif requestType == "count":
            info = {'count': len(results)}
        elif requestType == "all":
            objects = []
            nearest = {}
            min_separation = 10000000
            for row in results:
                diaObjectId = row[1]["diaObjectId"]
                separation = row[0]
                obj = {"object": diaObjectId, "separation": separation}
                if separation < min_separation:
                    min_separation = separation
                    nearest = obj
                objects.append(obj)
            info = {"objects":objects, "count":len(objects), "nearest":nearest}
        else:
            info = {"error": "Invalid request type"}

        return info

def reformat(old, lasair_added=True):
    new = {}
    new['diaObjectId'] = old['diaObjectId']
    diaObject = {
        'ra'               : old['objectData']['ra'],
        'decl'             : old['objectData']['decl'],
        'firstDiaSourceMjdTai': old['objectData']['mjdmin'],
        'lastDiaSourceMjdTai' : old['objectData']['mjdmax']
    }
    if lasair_added:
        lasairData = old['objectData']
        del lasairData['ra']
        del lasairData['decl']
        del lasairData['mjdmin']
        del lasairData['mjdmax']
        lasairData['sherlock']    = old['sherlock']
        lasairData['TNS']         = old['TNS']
        lasairData['annotations'] = old['annotations']
    diaSources = []
    imageUrls = []
    for ds in old['diaSources']:
        del ds['json']
        del ds['mjd']
#        del ds['imjd']
        del ds['since_now']
        del ds['utc']
        iu = ds['image_urls']
        del ds['image_urls']
        iu['diaSourceId'] = ds['diaSourceId']
        imageUrls.append(iu)
        diaSources.append(ds)
    if lasair_added:
        lasairData['imageUrls'] = imageUrls
        new['lasairData'] = lasairData
    new['diaObject'] = diaObject
    new['diaSources'] = diaSources
    new['diaForcedSources'] = old['diaForcedSources']
    return new

class ObjectSerializer(serializers.Serializer):
    objectId     = serializers.CharField(required=True)
    lite         = serializers.BooleanField(default=False)
    lasair_added = serializers.BooleanField(default=True)

    def save(self):
        objectId = self.validated_data['objectId']
        lite = self.validated_data['lite']
        lasair_added = self.validated_data['lasair_added']

        # Get the authenticated user, if it exists.
        userId = 'unknown'
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            userId = request.user

        if lasair_added:
            try:
                result = objjson(objectId, lite=lite)
            except Exception as e:
                result = {'error': str(e)}
            if not result:
                raise NotFound()
            try:
                result = reformat(result, lasair_added=lasair_added)
            except Exception as e:
                result = {'error': str(e)}
        else:
            LF = lightcurve_fetcher(cassandra_hosts=lasair_settings.CASSANDRA_HEAD)

            try:
                if lite: 
                    (diaSources, diaForcedSources) = LF.fetch(objectId, lite=lite)
                    result = {
                        'diaObjectId':objectId, 
                        'diaSources':diaSources, 
                        'diaForcedSources':diaForcedSources}
                else:
                    (diaObject, diaSources, diaForcedSources) = LF.fetch(objectId, lite=lite)
                    result = {
                        'diaObjectId':objectId, 
                        'diaObject':diaObject, 
                        'diaSources':diaSources, 
                        'diaForcedSources':diaForcedSources}
            except Exception as e:
                result = {'error': str(e)}
            LF.close()
        return result

class SherlockObjectSerializer(serializers.Serializer):
    objectId = serializers.IntegerField(required=True)
    lite = serializers.BooleanField(default=False)

    def save(self):
        diaObjectId = None
        diaObjectId = self.validated_data['objectId']

        lite = self.validated_data['lite']

        # Get the authenticated user, if it exists.
        userId = 'unknown'
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            userId = request.user

        if not lasair_settings.SHERLOCK_SERVICE:
            return {"error": "This Lasair cluster does not have a Sherlock service"}

        datadict = {}
        data = {'lite': lite}
        r = requests.post(
            'http://%s/object/%s' % (lasair_settings.SHERLOCK_SERVICE, diaObjectId),
            headers={"Content-Type": "application/json"},
            data=json.dumps(data)
        )

        if r.status_code == 200:
            return r.json()
        if r.status_code == 404:
            raise NotFound(r.json())
        return {"error": r.text}


class SherlockPositionSerializer(serializers.Serializer):
    ra = serializers.FloatField(required=True)
    dec = serializers.FloatField(required=True)
    lite = serializers.BooleanField(default=False)

    def validate_ra(self, value):
        if value > 360 or value < 0:
            raise serializers.ValidationError('ra must be between 0 and 360')
        return value

    def validate_dec(self, value):
        if value > 90 or value < -90:
            raise serializers.ValidationError('dec must be between -90 and 90')
        return value

    def save(self):
        ra = self.validated_data['ra']
        dec = self.validated_data['dec']
        lite = self.validated_data['lite']

        # Get the authenticated user, if it exists.
        userId = 'unknown'
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            userId = request.user

        if not lasair_settings.SHERLOCK_SERVICE:
            return {"error": "This Lasair cluster does not have a Sherlock service"}

        data = {'lite': lite, 'ra': '%.7f' % ra, 'dec': '%.7f' % dec}
        r = requests.post(
            'http://%s/query' % lasair_settings.SHERLOCK_SERVICE,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data)
        )

        if r.status_code != 200:
            return {"error": r.text}
        else:
            return json.loads(r.text)


class QuerySerializer(serializers.Serializer):
    selected = serializers.CharField(max_length=4096, required=True)
    tables = serializers.CharField(max_length=1024, required=True)
    conditions = serializers.CharField(max_length=4096, required=True, allow_blank=True)
    limit = serializers.IntegerField(max_value=1000000, required=False)
    offset = serializers.IntegerField(required=False)

    def save(self):
        selected = self.validated_data['selected']
        tables = self.validated_data['tables']
        conditions = self.validated_data['conditions']
        limit = None
        if 'limit' in self.validated_data:
            limit = self.validated_data['limit']
        offset = None
        if 'offset' in self.validated_data:
            offset = self.validated_data['offset']

        # Get the authenticated user, if it exists.
        userId = 'unknown'
        request = self.context.get("request")
        maxlimit = 1000
        if request and hasattr(request, "user"):
            userId = request.user
            if str(userId) != 'dummy':
                maxlimit = 10000
            for g in request.user.groups.all():
                if g.name == 'powerapi':
                    maxlimit = 1000000

        page = 0
        limitseconds = 300

        if limit == None:
            limit = 1000
        else:
            limit = int(limit)
        limit = min(maxlimit, limit)

        if offset == None:
            offset = 0
        else:
            offset = int(offset)

        error = check_query(selected, tables, conditions)
        if error:
            return {"error": error}

        try:
            sqlquery_real = build_query(selected, tables, conditions)
        except Exception as e:
            return {"error": str(e)}

        sqlquery_real += ' LIMIT %d OFFSET %d' % (limit, offset)

        msl = db_connect.readonly()
        cursor = msl.cursor(buffered=True, dictionary=True)
        result = []
        try:
            cursor.execute(sqlquery_real)
            for row in cursor:
                result.append(row)
            return result
        except Exception as e:
            error = 'Your query:<br/><b>' + sqlquery_real + '</b><br/>returned the error<br/><i>' + str(e) + '</i>'
            return {"error": error}



class AnnotateSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=255, required=True)
    objectId = serializers.IntegerField(required=True)
    classification = serializers.CharField(max_length=80, required=True)
    version = serializers.CharField(max_length=80, required=True)
    explanation = serializers.CharField(max_length=1024, required=True, allow_blank=True)
    classdict = serializers.CharField(max_length=4096, required=True)
    url = serializers.CharField(max_length=1024, required=True, allow_blank=True)

    def save(self):
        topic = self.validated_data['topic']
        diaObjectId = self.validated_data['objectId']
        classification = self.validated_data['classification']
        version = self.validated_data['version']
        explanation = self.validated_data['explanation']
        classdict = self.validated_data['classdict']
        url = self.validated_data['url']
        # Get the authenticated user, if it exists.
        userId = 'unknown'
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            userId = request.user
            user_name = userId.first_name + ' ' + userId.last_name

        # make sure the user submitting the annotation is the owner of the annotator
        is_owner = False
        try:
            msl = db_connect.remote()
            cursor = msl.cursor(buffered=True, dictionary=True)
        except MySQLdb.Error as e:
            return {'error': "Cannot connect to master database %d: %s\n" % (e.args[0], e.args[1])}

        cursor = msl.cursor(dictionary=True)
        cursor.execute('SELECT * from annotators where topic="%s"' % topic)
        nrow = 0
        for row in cursor:
            nrow += 1
            if row['user'] == userId.id:
                is_owner = True
                active = row['active']

        if nrow == 0:
            return {'error': "Annotator error: topic %s does not exist" % topic}
        if not is_owner:
            return {'error': "Annotator error: %s is not allowed to submit to topic %s" % (user_name, topic)}
        if active == 0:
            return {'error': "Annotator error: topic %s is not active -- ask Lasair team" % topic}

        # form the insert query
        query = 'REPLACE INTO annotations ('
        query += 'diaObjectId, topic, version, classification, explanation, classdict, url'
        query += ') VALUES ('
        query += "'%s', '%s', '%s', '%s', '%s', '%s', '%s')"
        query = query % (diaObjectId, topic, version, classification, explanation, classdict, url)

        try:
            cursor = msl.cursor(dictionary=True)
            cursor.execute(query)
            cursor.close()
            msl.commit()
        except Exception as e:
            return {'error': "Query failed %d: %s\n" % (e.args[0], e.args[1])}

        if active < 2:
            return {'status': 'success', 'query': query}

        # when active=2, we push a kafka message to make sure queries are run immediately
        message = {'diaObjectId': diaObjectId, 'annotator': topic}
        conf = {
            'bootstrap.servers': lasair_settings.INTERNAL_KAFKA_PRODUCER,
            'client.id': 'client-1',
        }
        producer = Producer(conf)
        topicout = lasair_settings.ANNOTATION_TOPIC
        try:
            s = json.dumps(message)
            producer.produce(topicout, s)
        except Exception as e:
            return {'error': "Kafka production failed: %s\n" % e}
        producer.flush()

        return {'status': 'success', 'query': query, 'annotation_topic': topicout, 'message': s}
