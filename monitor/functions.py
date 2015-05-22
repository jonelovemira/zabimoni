
import os,StringIO,ConfigParser,string,random,time
from config import REMOTE_COMMAND_LOG

def get_zabbix_server_ip():
	config = StringIO.StringIO()
	config.write('[dummysection]\n')
	config.write(open('/etc/zabbix/zabbix_agentd.conf').read())
	config.seek(0, os.SEEK_SET)
	cp = ConfigParser.ConfigParser()
	cp.readfp(config)
	Hostname = cp.get('dummysection', 'Hostname')
	config.close()
	return Hostname

def construct_random_str(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))


def log_for_callback_command(args):
	# WRITE LOG 
	time_format = '%Y-%m-%d %H:%M:%S %Z'
	current_time = time.strftime(time_format,time.gmtime(time.time()))
	output = open(REMOTE_COMMAND_LOG,'a')
	output.write( '\n' + current_time + ' ')

	for a in args:
		output.write(a + ' ')

	output.close()

def str_2_clock(time_str, format):
	if time_str is None or format is None:
		return None
	
	time_clock = time.mktime(time.strptime(time_str, format))
	return time_clock

def opentime_from_month_csv(month, year):

	if month is None or year is None:
		return None

	result_str = str(year) + '/' + str(month) + '/' + '1' + ' 0:00:00'

	return result_str

def clock_2_str(clock, format):
	if clock is None or format is None:
		return None

	time_str = time.strftime(format, time.gmtime(clock))

	return time_str

def function_input_checker(*invalid_values):
	def check_accepts(f):
		def new_f(*args, **kwds):
			for a in args:
				for iv in invalid_values:
					assert a is not iv, 'some args in %s are not valid' \
						% (f.func_name)
			return f(*args, **kwds)
		new_f.func_name = f.func_name
		return new_f
	return check_accepts


