import mysql.connector as mysql, os, subprocess, json
from argparse import ArgumentParser as AP

# Build command line arguments
def build():
	p = AP()
	p.add_argument("credentials", metavar="*.db", type=str,
				   help="Credential file (minimum requirement: username, password, database)")
	p.add_argument("--execute", metavar="*.sql|*.json", type=str, default=[], action='append',
				   help="Scripts and files to execute (*.sql) or interpret (*.json)")
	p.add_argument("--sqlify", type=str, default=None,
				   help="Path to save SQL interpretations of *.json files to (not saved if not specified)")
	p.add_argument("--backup", metavar="*.sql", type=str, default=None,
				   help="FilePath to push backups to")
	p.add_argument("--backup-frequency", choices=["never", "endpoints", "every"], default="never",
				   help="How often to save a backup (endpoints=start and finish; every=after execution) (default: never)")
	p.add_argument("--structure", metavar="*.sql", type=str, default=None,
				   help="File defining minimum DB state")
	p.add_argument("--initialize", action="store_true",
				   help="Reset DB using <args.structure> file")
	p.add_argument("--warnings", action="store_true",
				   help="Emit warnings out loud")
	p.add_argument("--delay_connection", action="store_true",
				   help="Do not immediately connect to DB")
	p.add_argument("-mysql", type=str, default='mysql',
				   help="MySQL executable to use (default: mysql)")
	p.add_argument("-mysqldump", type=str, default='mysqldump',
				   help="MySQLDump executable to use (default: mysqldump)")
	return p

# Parse command line arguments
def parse(p, a=None):
	if a is None:
		a = p.parse_args()
	else:
		# If string, convert to list
		if type(a) is str:
			a = a.split(' ')
		# Interactive mode may miss globbing
		from glob import glob
		globbed = []
		for arg in a:
			if '*' in arg:
				globbed.extend(glob(arg))
			else:
				globbed.append(arg)
		a = p.parse_args(globbed)
	return a

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
		self.backup_count = 0
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
			structure_exists = self.execute(structure)
		# Connection
		if not delay_connect:
			self.db = db_wrapper(self.creds, as_options=False, warnings=warnings)

	# Use command line redirection to run arbitrary SQL, return whether operation is successful or not
	def execute(self, fname):
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

	def maybe_int(self, x):
		try:
			return int(x)
		except ValueError:
			return x

	def sqlify(self, build):
		print(build)

	# Current issues:
		# type: weapon -> weapon: subtype -> subtype: value (weapon should not be a key)
		# multiple lists at the same level triggers static ruling on the lists
		# empty lists are not discarded
	# SPECIAL KEYS TO RECOGNIZE:
		# 'table': for FROM statement
		# 'promoted': count indicating top-n elements to set IS_PROMOTED to TRUE on a `drop` table entry
	def recursive_build(self, xjson, build=dict(), save_as=None, this_level=None):
		# Safe type conversion for identification
		q = [self.maybe_int(x) for x in xjson.keys()]
		# Split into keyable data (defines build at this level) and traversable data (defines new recursion depth)
		static = [_ for _ in q if type(_) is not int and type(xjson[_]) is not dict]
		deeper = [str(_) for _ in q if type(_) is int or type(xjson[_]) is dict]
		traverse = [type(xjson[str(_)]) for _ in q if type(_) is int or type(xjson[_]) is dict]
		# Add keys for subsequent depth
		for key in static:
			build[key] = xjson[key] #('static', xjson[key])
		# Traverse depths
		for depth, typed in zip(deeper, traverse):
			if this_level is not None and type(self.maybe_int(this_level)) is not int:
				build[this_level] = depth #('leveled', depth)
			'''
				print(f"{this_level} with type {typed} and this_level type {self.maybe_int(this_level)} is a trigger for {depth} to be a key")
			else:
				if this_level is not None:
					print(f"NOT TRIGGER: {this_level} with type {typed} and this_level type {self.maybe_int(this_level)} means {depth} isn't a key")
				else:
					print(f"NOT TRIGGER: this_level is none with type {typed} meaning {depth} isn't a key")
			'''
			self.recursive_build(xjson[depth], build=build, save_as=save_as, this_level=depth if typed is dict else None)
			if this_level is not None and this_level in build.keys():
				del build[this_level]
		# Interpret
		#print(f"Recursion done for {q}")
		if deeper == []:
			#print(f"Rising out from depth: {static}")
			self.sqlify(build)
		#else:
		#	#print(f"Rising out from depth: {deeper}")
		# Remove keys from depth
		for key in static:
			del build[key]

	# Interpret a text file into SQL, optionally save the SQL interpretation as it is built
	def interpret(self, script, save_as=None):
		with open(script, 'r') as f:
			ins = json.load(f)
		if save_as is not None:
			save_as = open(save_as, 'w')
		# Recursive? Interpretation
		self.recursive_build(ins, save_as=save_as)
		if save_as is not None:
			save_as.close()

	# Use command line redirection to create basic SQL DB backup, return whether operation is successful or not
	def backup(self, fname):
		command = [self.mysqldump,
				   '--user='+self.creds['user'],
				   '--password='+self.creds['password'],
				   '--databases', 'genshin']
		# Modify fname with versioning
		fname = fname[:fname.index('.sql')]+'_'+str(self.backup_count)+'.sql'
		self.backup_count = self.backup_count + 1
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

if __name__ == '__main__':
	args = parse(build())
	g = genshin(args.credentials, warnings=args.warnings, structure=args.structure,
				initialize_db=args.initialize, delay_connect=args.delay_connection,
				mysql=args.mysql, mysqldump=args.mysqldump)
	if args.backup_frequency != "never" and args.backup is not None:
		g.backup(args.backup)
	for script in args.execute:
		if script.endswith('.sql'):
			g.execute(script)
		elif script.endswith('.json'):
			g.interpret(script, args.sqlify)
		else:
			print(f"Unrecognized execution extension: {script[script.index('.'):]} for {script}")
		if args.backup_frequency == "every" and args.backup is not None:
			g.backup(args.backup)

