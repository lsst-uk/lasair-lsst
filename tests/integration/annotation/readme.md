### Using the API for annotations and tags
Two annotations are made via Kafka, and it will take a minute for them to arrive
For classic, we just get papaya, for tags we get mango and papaya

- classic: `python3 ann_test.py royg __annot api`
- tags: `python3 ann_test.py royg tags_royg api`

### Using direct function calls, this is what the webserver does
Two annotations are made, should happen immediately
For classic, we just get pear, for tags we get apple and pear

- classic: `python3 ann_test.py royg __annot direct`
- tags: `python3 ann_test.py royg tags_roy direct`

