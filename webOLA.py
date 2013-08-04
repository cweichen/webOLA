from flask import Flask, request
import array, urllib, urllib2, json, math
app = Flask(__name__)

UNIVERSE = 1
OLA_HOST = 'http://localhost:9090'
PAN_CHANNEL = 1
PAN_MIN_DEGREES = 0
PAN_MAX_DEGREES = 630
TILT_CHANNEL = 3
TILT_MIN_DEGREES = 0
TILT_MAX_DEGREES = 135
TILT_PRESETS = { 	'up': 0,
					'wall': 55 }
COLOR_CHANNEL = 5
COLOR_MAP = { 	'white': 0,
				'red': 14,
				'blue': 28,
				'green': 42,
				'yellow': 56,
				'magenta': 70,
				'orange': 84,
				'uv': 98,
				'pink':112,
				'rainbow':156 }
FOCUS_CHANNEL = 10
PATTERN_MAP = {	'bars': {'channel': 6, 'value': 10, 'slow': 85, 'medium': 90, 'fast': 99},
				'sun1': {'channel': 6, 'value': 20, 'slow': 105, 'medium': 110, 'fast': 119},
				'spiral': {'channel': 6, 'value': 30, 'slow': 125, 'medium': 130, 'fast': 139},
				'eclipse': {'channel': 6, 'value': 40, 'slow': 145, 'medium': 150, 'fast': 159},
				'sun2': {'channel': 6, 'value': 50, 'slow': 165, 'medium': 170, 'fast': 179},
				'cells': {'channel': 6, 'value': 60, 'slow': 185, 'medium': 190, 'fast': 199},
				'dots1': {'channel': 6, 'value': 70, 'slow': 205, 'medium': 210, 'fast': 230},
				'stars': {'channel': 8, 'value': 14, 'slow': 115, 'medium': 121, 'fast': 127},
				'mandala': {'channel': 8, 'value': 28, 'slow': 131, 'medium': 137, 'fast': 143},
				'sun3': {'channel': 8, 'value': 42, 'slow': 147, 'medium': 153, 'fast': 159},
				'triangles': {'channel': 8, 'value': 56, 'slow': 163, 'medium': 169, 'fast': 175},
				'sun4': {'channel': 8, 'value': 70, 'slow': 179, 'medium': 185, 'fast': 191},
				'croquet': {'channel': 8, 'value': 84, 'slow': 195, 'medium': 201, 'fast': 207},
				'dots2': {'channel': 8, 'value': 98, 'slow': 211, 'medium': 217, 'fast': 223}}
SHAKE_MAP = ['slow', 'medium', 'fast']

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
def set_dmx(channel, value):

	dmx = read_dmx()
	# Set new value
	dmx[channel - 1] = value 
	query_args = { 'u': str(UNIVERSE), 'd': ",".join([str(x) for x in dmx])}

	# This urlencodes your data (that's why we need to import urllib at the top)
	data = urllib.urlencode(query_args)
 
	# Send HTTP POST request
	request = urllib2.Request(OLA_HOST+'/set_dmx', data)
	response = urllib2.urlopen(request)
 
	return repr(dmx[0:63])

@app.route('/color/<color>')
def set_color(color):
	if color in COLOR_MAP:
		set_dmx(COLOR_CHANNEL, COLOR_MAP[color])
		return 'Set color to %s' % color
	else:
		return 'Color %s not supported' % color

@app.route('/pan/<int:degrees>')
def set_pan(degrees):
	if (degrees >= PAN_MIN_DEGREES) and (degrees <= PAN_MAX_DEGREES):
		dmx_value = math.floor(float(degrees) / PAN_MAX_DEGREES * 255)
		set_dmx(PAN_CHANNEL, dmx_value)
		return 'Set pan to %d degrees (DMX value %d)' % (degrees, dmx_value)
	else:
		return 'Pan must be between %d and %d degrees' % (PAN_MIN_DEGREES, PAN_MAX_DEGREES)

@app.route('/tilt/<int:degrees>')
def set_tilt(degrees):
	if (degrees >= TILT_MIN_DEGREES) and (degrees <= TILT_MAX_DEGREES):
		dmx_value = 128 + math.floor(float(degrees) / TILT_MAX_DEGREES * 127)
		set_dmx(TILT_CHANNEL, dmx_value)
		return 'Set tilt to %d degrees (DMX value %d)' % (degrees, dmx_value)
	else:
		return 'Tilt must be between %d and %d degrees' % (TILT_MIN_DEGREES, TILT_MAX_DEGREES)

@app.route('/tilt/<preset>')
def set_tilt_preset(preset):
	if preset in TILT_PRESETS:
		set_tilt(TILT_PRESETS[preset])
		return 'Set tilt to preset %s' % preset
	else:
		return 'Unsupported preset'

@app.route('/focus/<int:percent>')
def set_focus(percent):
	if (percent >= 0) and (percent <= 100):
		set_dmx(FOCUS_CHANNEL, math.floor(float(percent) / 100 * 255))
		return 'Set focus to %d' % percent
	else:
		return 'Focus must be between 0 and 100'

@app.route('/pattern/<pattern>')
def set_pattern(pattern):
	if pattern in PATTERN_MAP:
		# Remove previous patterns
		set_dmx(6,0)
		set_dmx(8,0)

		# Check for extra effects
		shake = request.args.get('shake', '')
		if shake in SHAKE_MAP:
			set_dmx(PATTERN_MAP[pattern]['channel'], PATTERN_MAP[pattern][shake])
		else:
			# Set new pattern
			set_dmx(PATTERN_MAP[pattern]['channel'], PATTERN_MAP[pattern]['value'])
		return 'Set pattern to %s' % pattern
	else:
		return 'Pattern %s not supported' % pattern

@app.route('/brightness/<int:brightness>')
def set_brightness(brightness):
	if (brightness >= 0) and (brightness <= 100):
		set_dmx(12,128)
		set_dmx(12,math.floor(float(brightness) / 100 * 255))
		return 'Set brightness to %d percent' % brightness
	else:
		return 'Brightness must be between 0 and 100'

@app.route('/reset')
def reset():
	dmx = read_dmx()
	for channel in range(4,14):
		set_dmx(channel, 0)
	set_dmx(11, 255)
	set_dmx(12, 128)
	set_dmx(12, 255)
	return 'Light reset'

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)