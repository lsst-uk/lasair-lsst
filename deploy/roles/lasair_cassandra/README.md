Role Name
=========

Role for initial setup of the Lasair cassandra keyspace and tables. Run on ONE CASSANDRA NODE ONLY.

Role Variables
--------------

`replication_factor`: Replication Factor (default = 3)
`keyspace`: Cassandra keyspace (default `lasair`)
`git_raw_url`: The Raw git URL (default `https://raw.githubusercontent.com/lsst-uk/lasair-lsst`)
`branch`: The branch on github that contains the correct CQL schema files (default `main`)


These values do not need to be overridden and the default values should suffice.

Example Playbook
----------------

    # Apply to either standalone DB host or the first Galera backend
    - hosts: cassandranodes[0]
      roles:
        - lasair_cassandra


License
-------

Apache-2.0

