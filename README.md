# `py-db-migrate`

CLI migration tool for python.

**Usage**:

```console
$ py-db-migrate [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new sql file.
* `down`: Delete the latest migration file by using...
* `init`: Create an initial configuration file.
* `start`: Create an initial configuration file.
* `up`: Run the new migration files.

## `py-db-migrate create`

Create a new sql file.

**Usage**:

```console
$ py-db-migrate create [OPTIONS] NAME
```

**Arguments**:

* `NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `py-db-migrate down`

Delete the latest migration file by using down file.

**Usage**:

```console
$ py-db-migrate down [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `py-db-migrate init`

Create an initial configuration file.

You need to update this configuration file.

**Usage**:

```console
$ py-db-migrate init [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `py-db-migrate start`

Create an initial configuration file.

You need to update this configuration file.

**Usage**:

```console
$ py-db-migrate start [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `py-db-migrate up`

Run the new migration files.

**Usage**:

```console
$ py-db-migrate up [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
