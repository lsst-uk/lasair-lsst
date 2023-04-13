# In order to run manage.py 
export PYTHONPATH=$PYTHONPATH:/home/ubuntu/lasair4/webserver/lasair
export PYTHONPATH=$PYTHONPATH:/home/ubuntu/lasair4/common

cd ~/lasair4/webserver/staticfiles/
gulp build
cd ..
python3 manage.py collectstatic --settings lasair.settings
