# System Tests

These tests are intended to be run on a deployed Lasair system.

## Deployment tests
```
$ ./deployment_tests.sh
```

Runs the suite of deployment tests which validates that all Lasair components that should have been deployed are
deployed and, where appropriate, responsive. Uses ansible to perform the tests and is intended to be run from the
login instance.

## API tests
```
$ ./api_tests.sh --url=https://lasair-ztf.lsst.ac.uk/api --token=a*************************************2
```

Runs a suite of tests against the Lasair API. `--url` and `--token` can be given as options or taken from the
`settings.py` if available. The output may require some interpretation since results will depend on the content
of the database and some failures may be expected.