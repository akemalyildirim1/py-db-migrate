## 0.3.0 (2023-09-11)

### Feat

- **main.py**: add down command to app
- **service/migration_down**: add migration down service

### Refactor

- **database**: update import order
- **service**: refactor service layer

## 0.2.0 (2023-09-09)

### Feat

- **main.py**: add up command to app
- **service/migration**: add migration class for running migration
- **service/service.py**: add sql service class which has a database field
- **database**: add context manager to sql classes to use for transactions
- **service/migration_files**: add migration files service
- **main.py**: add start service to main for testing
- **service/start**: add start service
- **src/logger**: add logger file
- **scripts**: add test scripts
- **src/**: add src module to project

### Refactor

- **py_db_migrate**: use py_db_migrate instead of src
- **main.py**: use migration file in the main file
