When the schema updates, a new sample alert can be made from the simple alert.
For example, if the new schema is 9_0, we do:
mkdir schema9_0
cd ../../../utility/
python3 make_sample_alert.py 9_0 ../tests/system/sample_alerts/simple ../tests/system/sample_alerts/schema9_0

