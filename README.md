# py-db-migrate

[![coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg)](https://github.com/akemalyildirim1/py-db-migrate/actions)


It will be a CLI app.

Commands:
* migrate (It will run the migrations (up))
* up (Same with migrate)
* down (Undo the last migrations...-down.sql)
* create (It will create a migration file with the given name. For example, car-table is given, car-table-up.sql and car-table-down.sql will be created).
* start (It will create a configuration file of the project. If it will exists, skip. do not overwrite)
