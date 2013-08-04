from flask import Flask
import array, urllib, urllib2, json
app = Flask(__name__)

UNIVERSE = 1
OLA_HOST = 'http://localhost:9090'

def read_dmx():
	response = urllib2.urlopen(OLA_HOST + '/get_dmx?u=%d' % UNIVERSE)
	res = response.read()
	dmx = json.loads(res)
	data = dmx['dmx'][0:63]
	return data

@app.route('/')
def index():
	return 'Hello webOLA!'

@app.route('/read')
def print_dmx():
	return repr(read_dmx())

@app.route('/channel/<int:channel>/value/<int:value>')
def set_channel_value(channel, value):

	dmx = read_dmx()
	# Set new value
	print dmx
	dmx[channel - 1] = value 
	query_args = { 'u': str(UNIVERSE), 'd': ",".join([str(x) for x in dmx])}

	# This urlencodes your data (that's why we need to import urllib at the top)
	data = urllib.urlencode(query_args)
 
	# Send HTTP POST request
	request = urllib2.Request(OLA_HOST+'/set_dmx', data)
	response = urllib2.urlopen(request)
 
	return repr(dmx[0:63])

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)