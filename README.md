# genshin
Genshin DBMS project

[Dependencies]
* MySQL Server v8.0+: https://dev.mysql.com/downloads/mysql/
	* NOTE: You must initialize the database using the legacy password system, v8.0's stronger passwords are not supported by the python connector
* MySQL Connector/Python v8.0+: https://dev.mysql.com/downloads/connector/python/
	* Designed on Python v3.7.4, YMMV with older versions
* Other Python Dependencies:
	* Matplotlib

[Setup]
0. Create a MySQL server to host the DB.

1. Specifying database connection

Certain functionalities in this framework require a specially formatted `*.db` file. For each line in this file, specify a MySQL command line argument, colon, and the appropriate value, such as given below:

```
	user: tlranda
	database: genshin
	password: Y0uW!$h
```

This structure supports all MySQL command line options, including the specification of a more traditional `*.cnf` options file (refer to the [option files docs](https://dev.mysql.com/doc/refman/8.0/en/option-files.html)), however the options in the example above should be the minimum information directly included in your `*.db` as the current script is not capable of extracting parameters from option files.

2. Initializing the database structure

	Handle via Python API: `python3 db.py credentials.db --initialize --structure genshin.sql`

	Handle via Python API in code: `g = genshin('credentials.db', initialize_db=True, structure='genshin.sql')`

	Handle via command line: `mysql --user=<USER> --password=<PASSWORD> < genshin.sql`

	Either of these methods are equivalent.

4. Operating on DB via Python

	For any valid .sql scripts: `python3 db.py credentials.db --execute script1.sql script2.sql ...`

	For any interpretable .txt files: `python3 db.py credentials.db --execute interp1.txt interp2.txt ...`

		Optional: Save interpretation as .sql script by adding `--sqlify path/basename`

5. Generating plots

<TBD>

6. Backing up the Database

	Handle via Python API: `python3 db.py credentials.db --backup backup.sql --backup-frequency endpoints`

	Handle via Python API in code: `g = genshin('credentials.db'); g.backup('backup.sql')`

	Handle via command line: `mysqldump --user=<USER> --password=<PASSWORD> --databases genshin > backup.sql`

	Either of these methods are equivalent.

[Further Documentation and Examples]

db.py: See comments in script or higher-level design goals in <TBD>

[Contributors]

Please add your name to this list if you are approved for a merge:

Thomas Randall

