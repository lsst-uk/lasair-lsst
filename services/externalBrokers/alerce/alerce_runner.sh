d=$(date +'%Y%m%d')
logfile='/mnt/cephfs/lasair/services_log/'$d'.log'
python3 /home/ubuntu/lasair4/services/externalBrokers/alerce/consume_alerce.py stamp_classifier_$d >> $logfile
python3 /home/ubuntu/lasair4/services/externalBrokers/alerce/consume_alerce.py lc_classifier_$d >> $logfile

