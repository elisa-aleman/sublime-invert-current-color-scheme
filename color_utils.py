# color conversion helper functions

def convert_hex_to_rgb(color):

	r = int(color[0:2] , 16)
	g = int(color[2:4] , 16)
	b = int(color[4:6] , 16)

	if( len(color) > 6 ):

		a = (float( int( color[6:8], 16 ) ) )/255

		return [r, g, b, a];

	return [r, g, b];


def convert_rgb_to_hex(color):

	a = format(color[0], '02X')
	b = format(color[1], '02X')
	c = format(color[2], '02X')

	if( len(color) > 3 ):

		d = format( int( round( color[3] * 255 ) ), '02X')

		return [a, b, c, d];

	return [a, b, c];

def invert_rgb(color):

	r = (color[0] * -1) + 255
	g = (color[1] * -1) + 255
	b = (color[2] * -1) + 255

	if( len(color) > 3 ):

		a = color[3]
		# perform alpha inversion here if needed
		# a = 1 - a

		return [r, g, b, a];

	return [r, g, b];
