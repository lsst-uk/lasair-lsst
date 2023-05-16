# In order to run manage.py 
export PYTHONPATH=$PYTHONPATH:/home/ubuntu/lasair-lsst/webserver/lasair
export PYTHONPATH=$PYTHONPATH:/home/ubuntu/lasair-lsst/common

cd ~/lasair-lsst/webserver/staticfiles/
gulp build
cd ..
python3 manage.py collectstatic --settings lasair.settings
