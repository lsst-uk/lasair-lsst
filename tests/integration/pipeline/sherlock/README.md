### Sherlock integration
`integration_test_sherlock_wrapper.py`

This test gets some alerts from Kafka, annotates them with the Sherlock classifier,
then pushes them back into Kafka. It requires a functional Kafka and database
running on localhost and Sherlock. 
It also uese the database to check the cache capability.
It uses the following auxiliary files and directories:
* sherlock_test.yaml

