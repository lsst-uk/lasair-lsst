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

        obj = None
        separation = None

        objectList = []
        if len(results) > 0:
            if requestType == "nearest":
                obj = results[0][1]['diaObjectId']
                separation = results[0][0]
                info = {"object": obj, "separation": separation}
            elif requestType == "all":
                for row in results:
                    objectList.append({"object": row[1]["diaObjectId"], "separation": row[0]})
                info = objectList
            elif requestType == "count":
                info = {'count': len(results)}
            else:
                info = {"error": "Invalid request type"}

        return info


class ObjectsSerializer(serializers.Serializer):
    objectIds = serializers.CharField(required=True)

    def save(self):
        diaObjectIds = self.validated_data['objectIds']

        olist = []
        for tok in diaObjectIds.split(','):
            olist.append(tok.strip())
        olist = olist[:10] # restrict to 10

        # Get the authenticated user, if it exists.
        userId = 'unknown'
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            userId = request.user

        result = []
        for diaObjectId in olist:
            if 1:
                obj = objjson(int(diaObjectId))
#            except:
#                obj = None
            result.append(obj)
        return result


class SherlockObjectSerializer(serializers.Serializer):
    objectId = serializers.CharField(required=True)
    lite = serializers.BooleanField()

    def save(self):
        diaObjectId = None
        lite = False
        diaObjectId = self.validated_data['objectId']

        if 'lite' in self.validated_data:
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
        else:
            return {"error": r.text}


class SherlockPositionSerializer(serializers.Serializer):
    ra = serializers.FloatField(required=True)
    dec = serializers.FloatField(required=True)
    lite = serializers.BooleanField()

    def save(self):
        lite = False
        ra = self.validated_data['ra']
        dec = self.validated_data['dec']
        if 'lite' in self.validated_data:
            lite = self.validated_data['lite']

        # Get the authenticated user, if it exists.
        userId = 'unknown'
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            userId = request.user
# can also send multiples, but not yet implemented
# http://192.41.108.29/query?ra=115.811388,97.486925&dec=-25.76404,-26.975506

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

class LightcurvesSerializer(serializers.Serializer):
    objectIds = serializers.CharField(max_length=16384, required=True)

    def save(self):
        diaObjectIds = self.validated_data['objectIds']
        olist = []
        for tok in diaObjectIds.split(','):
            olist.append(tok.strip())

        # Get the authenticated user, if it exists.
        userId = 'unknown'
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            userId = request.user

            # Fetch the lightcurve, either from cassandra or file system
        LF = lightcurve_fetcher(cassandra_hosts=lasair_settings.CASSANDRA_HEAD)

        lightcurves = []
        for diaObjectId in olist:
            candidates = LF.fetch(diaObjectId)
            lightcurves.append({'diaObjectId':diaObjectId, 'candidates':candidates})

        LF.close()
        return lightcurves


class AnnotateSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=256, required=True)
    objectId = serializers.CharField(max_length=256, required=True)
    classification = serializers.CharField(max_length=256, required=True)
    version = serializers.CharField(max_length=256, required=True)
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
