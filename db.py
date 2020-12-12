import mysql.connector as mysql, os, subprocess

# Module-level file parsing to read credentials
def parse_db_credentials(fname, warn=True):
	conn_params = ["user", "password", "database", "host", "port", # The ones you will probably need
				   # The additional valid specs
				   "unix_socket", "auth_plugin", "use_unicode", "charset", "collation", "autocommit",
				   "time_zone", "sql_mode", "get_warnings", "raise_on_warnings", "connection_timeout",
				   "client_flags", "buffered", "raw", "consume_results", "ssl_ca", "ssl_cert", "ssl_disabled",
				   "ssl_key", "ssl_verify_cert", "ssl_verify_identity", "force_ipv6", "dsn", "pool_name",
				   "pool_size", "pool_reset_session", "compress", "converter_class", "failover", "option_files",
				   "option_groups", "allow_local_infile", "use_pure",
	]
	# Initialize dictionary
	creds = dict((k, None) for k in conn_params)
	if not os.path.isfile(fname):
		raise ValueError(f"Invalid file path: {fname}")
	with open(fname, 'r') as f:
		# Each line specifies a parameter
		for line in f.readlines():
			line = line.rstrip().lstrip()
			# Parameter and values delimited by ':'
			try:
				param, *value = [_.lstrip().rstrip() for _ in line.split(':') if _ != '']
			except ValueError: # Empty or misformatted line
				if line != '' and warn:
					print(f"Unable to parse credential line '{line}' from '{fname}', skipping...")
				continue
			if param in conn_params:
				if len(value) == 1:
					creds[param] = value[0]
				else:
					creds[param] = value
	# Return initialized values only
	return dict((k,v) for k,v in zip(creds.keys(), creds.values()) if v is not None)

class genshin(object):
	def __init__(self, credentials, as_options=False, warnings=True,
					   initialize_db=False, structure=None,
					   mysql='mysql', mysqldump='mysqldump', delay_connect=False):
		# Object's own data
		self.error = False
		self.db = None
		self.mysql = mysql
		self.mysqldump = mysqldump
		# Parse options
		self.structure = structure
		if as_options:
			self.creds = {'option_files': credentials}
		else:
		  if type(credentials) is dict:
			  self.creds = credentials
		  elif type(credentials) is str:
			  self.creds = parse_db_credentials(credentials, warn=warnings)
		  else:
			  raise ValueError(f"Cannot initialize connection with type '{type(credentials)}'")
		# Reinitialization Check
		if initialize_db and structure is not None:
			structure_exists = self.recreate_structure(structure)
		# Connection
		if not delay_connect:
			self.db = db_wrapper(self.creds, as_options=False, warnings=warnings)

	# Use command line redirection to create basic SQL DB structure, return whether operation is successful or not
	def recreate_structure(self, fname):
		command = [self.mysql,
				   '--user='+self.creds['user'],
				   '--password='+self.creds['password']]
		with open(fname, 'r') as f:
			process = subprocess.run(command, stdin=f, capture_output=True)
			if process.returncode != 0:
				print(process.returncode)
				print(process.stderr)
				print(command)
				self.error = True
		return self.error

	# Use command line redirection to create basic SQL DB backup, return whether operation is successful or not
	def backup(self, fname):
		command = [self.mysqldump,
				   '--user='+self.creds['user'],
				   '--password='+self.creds['password'],
				   '--databases', 'genshin']
		with open(fname, 'w') as f:
			process = subprocess.run(command, stdout=f, stderr=subprocess.PIPE)
			if process.returncode != 0:
				print(process.returncode)
				print(process.stderr)
				print(command)
				self.error = True
		return self.error

	# Mark error as handled
	def clearError(self):
		self.error = False

	# Mark db error as handled
	def clearDBError(self):
		self.db.errorState = False

	def __del__(self):
		del self.db

# Make MySQL API more convenient to use
class db_wrapper(object):
	# Create connection upon initialization
	def __init__(self, db_credentials, as_options=False, warnings=True):
		# Argument options to the class
		self.warnings = warnings
		self.errorState = False
		# Set up connection info
		if as_options:
			self.creds = {'option_files': db_credentials}
		else:
		  if type(db_credentials) is dict:
			  self.creds = db_credentials
		  elif type(db_credentials) is str:
			  self.creds = parse_db_credentials(db_credentials, warn=self.warnings)
		  else:
			  raise ValueError(f"Cannot initialize connection with type '{type(db_credentials)}'")
		# Connect using info
		self.connect()

	# Properly shut down connection
	def __del__(self):
		self.disconnect()

	# Activate connection
	def connect(self):
		try:
			self.conn = mysql.connect(**self.creds)
		except mysql.Error as err:
			raise ValueError(f"Failed to connect: {err}")
		self.is_connected = True
		# Create cursors
		self.cursor = self.conn.cursor(dictionary=True, buffered=True)
		self.proccursor = self.conn.cursor(dictionary=True, buffered=False)

	# Remove connection
	def disconnect(self):
		if self.is_connected:
			self.is_connected = False
			self.conn.close()
			self.cursor = None
			self.proccursor = None

	# Mark error as handled
	def clearError(self):
		self.errorState = False

	# Get auto_increment value if it was used, None means it wasn't
	def lastrowid(self):
		return self.cursor.lastrowid

	# Get rowcount for affected rows
	def rowcount(self):
		return self.cursor.rowcount

	# Get cursor's last statement
	def statement(self):
		return self.cursor.statement

	# Navigate intricacies of ways to use API
		# STRING
		# STRING with %s, TUPLE with ordered replacements
		# STRING with %(name)s, DICT with DICT[name] = replacement
		# STRING with either of above, LIST with either corresponding matching method
	# Return tuple of resulting rows, affected row counts, and any warnings generated by the statements
	def query(self, qstring, qvals=tuple()):
		results = []
		affected = []
		try:
			# Empty tuple == no qvals to submit
			if qvals != tuple():
				if ';' in qstring:
					raise ValueError("Multi-statements with variable substitution not supported")
				else:
				  if type(qvals) is list:
					  # Multiple sets of values to pass
					  queryres = self.cursor.executemany(qstring, qvals)
				  elif type(qvals) is tuple:
					  # Just the one tuple
					  queryres = self.cursor.execute(qstring, qvals)
				  elif type(qvals) is dict:
					  # Other kind of substitution to be carried out
					  queryres = self.cursor.execute(qstring, qvals)
				# Parse an individual statement's results
				if self.cursor.with_rows:
					results.extend(queryres.fetchall())
				else:
					results.extend([])
				affected.append(self.cursor.rowcount)
			else:
				# No values, just a string
				multi = ';' in qstring[:-1] # In case they put it on the end, discount that
				iterator = self.cursor.execute(qstring, multi=multi)
				# Have to separately parse each statement's results
				if multi:
					for queryres in iterator:
						results.append(queryres.fetchall())
						affected.append(queryres.rowcount)
				else:
					if self.cursor.with_rows:
						results.append(self.cursor.fetchall())
					else:
						results.append([])
					affected.append(self.cursor.rowcount)
		except mysql.Error as err:
			if self.warnings:
				print(f"{err}")
				# REAL DEBUG: actually raise the error within this function (ie: query() is problematic, not user code)
				# raise err
			self.errorState = True
			return err # Return error object after setting errorState
		# OPTIONAL: call cursor.fetchwarnings() to see if statement had any warnings
		warned = self.cursor.fetchwarnings()
		# At some point have to commit to database with connection.commit()
		self.conn.commit()
		return results, affected, warned

	# Call procedure, returns dictionary with named variables and values from tups
	def procedure(self, procedurename, tups=tuple()):
		try:
			result = self.proccursor.callproc(procedurename, tups)
			# May need to use cursor.stored_results() to retrieve sets of data returned by a procedure
		except mysql.Error as err:
			if self.warnings:
				print(f"{err}")
			self.errorState = True
			return err # Return error object after setting errorState
		# At some point have to commit to database with connection.commit()
		self.conn.commit()
		return result

