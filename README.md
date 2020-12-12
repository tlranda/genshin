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
1. Specifying database connection
	You may utilize a standard MySQL *.cnf options file ([Refer to the MySQL 8.0 Documentation](https://dev.mysql.com/doc/refman/8.0/en/option-files.html)) or a *.db file as specified below:
		For each line in the file, specify a mysql command line argument, colon, and the appropriate value, such as given below:
			```
			user: tlranda
			database: genshin
			password: Y0uW!$h
			```
2. Initializing the database structure
	<TBD>
3. Populating saved data (optional)
	<TBD>
4. Adding additional data via Python
	<TBD>
5. Generating plots
	<TBD>

[Further Documentation and Examples]
db.py: See comments in script or higher-level design goals in <TBD>

[Contributors]
Please add your name to this list if you are approved for a merge:
Thomas Randall

