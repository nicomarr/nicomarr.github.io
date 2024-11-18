# My website


### Update citation counts
To update citation counts in the `test_data` directory:
```sh
python ./_py/utils/main.py --update-citations ./_py/test_data
```
To update citation counts in the `_data` directory:
```sh
python ./_py/utils/main.py --update-citations ./_data
```
Or in quiet mode:
```sh
python ./_py/utils/main.py --update-citations ./_data --quiet
```

### Append metadata with new articles
To append metadata in the `test_data` directory:
```sh
python ./_py/utils/main.py --append-metadata ./_py/test_data
```

To append metadata in the `_data` directory:
```sh
python ./_py/utils/main.py --append-metadata ./_data
```
To include errata and run in quiet mode:
```sh
python ./_py/utils/main.py --append-metadata ./_data --quiet
```

### Perform both update and append operations
```sh
python ./_py/utils/main.py --update-and-append ./_data
```

### Help
```sh
python ./_py/utils/main.py --help
```