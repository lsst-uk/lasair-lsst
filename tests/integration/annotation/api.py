import lasair
import api_token
endpoint = "https://lasair-lsst-dev.lsst.ac.uk/api"

if __name__ == "__main__":
    L = lasair.lasair_client(api_token.API_TOKEN, endpoint=endpoint)
    topic_out = 'fanntest'

    classdict = {'hello there'}
        L.annotate(
        topic_out,
        170054984062730394,
        'hello',
        version='0.1',
        explanation='',
        classdict={'hello':1},
        url='')
