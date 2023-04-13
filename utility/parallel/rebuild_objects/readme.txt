#For full instructions see
#https://lsst-uk.atlassian.net/wiki/spaces/LUSC/pages/2888663041/Feature+Set+Evolution+for+Lasair


-- to use par_runner_files
cat tmp.sql
select * from missingobjs

mysql --user=ztf --host=lasair-ztf-cluster_control --port=9001 -p ztf < tmp.sql > missingobjs.txt

mv missingobjs.txt /mnt/cephfs/roy
cd /mnt/cephfs/roy

split -n 32 missingobjs.txt
mkdir tasks
mv x* tasks

mkdir tasksout

# use 4 processes = 4 files per node
python3 par_runner_files.py 4 /mnt/cephfs/roy/tasks /mnt/cephfs/roy/tasksout

