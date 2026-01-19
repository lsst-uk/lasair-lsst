# System Tests

These tests are intended to be run on a deployed Lasair system. They use ansible to perform the tests and are intended to be run from the
login instance.

## Deployment tests
```
$ ./deployment.sh
```

Runs the suite of deployment tests which validates that all Lasair components that should have been deployed are deployed and, where appropriate, responsive. 
The following command lists the checking that is done:
```
ansible-playbook deployment.yaml --list-tasks
```

## Pipeline tests
```
$ ./pipeline.sh
```

Injects sample alerts into a temporary Kafka topic, then runs ingest, sherlock and filter steps against them. The individual steps can be called as `ingest.sh`, `sherlock.sh` and `filter.sh`.
The following command lists the checking that is done:
```
ansible-playbook pipeline.yaml --list-tasks 
```

## API tests
```
$ ./api.sh
```

Test that the API is responsive and handles valid/invalid inputs correctly. The test does not evaluate the content of responses for correctness since the exact result will depend on the content of the database.
The following command lists the checking that is done:
```
ansible-playbook api.yaml --list-tasks 
```
