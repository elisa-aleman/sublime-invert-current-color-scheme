#!/usr/bin/env python

import sublime
import sublime_plugin
import sys
import os

from .color_utils import *
from .path_utils import *

class InvertCurrentColorSchemeCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		if (return_current_color_scheme_name().find('_Inverted') > -1):
			return sublime.error_message("Color scheme already inverted.")

		# store current scheme data into string using load_resource, simplifies accessing schemes like the default ones since the are packed in default package.
		current_scheme_text = sublime.load_resource(return_current_color_scheme_relative_to_st_root())

		# write out to temp file
		print('Creating temp scheme file.')
		with open(os.path.join(sublime.packages_path(), 'current_scheme_temp.tmTheme'), 'w', errors='ignore') as current_scheme_temp:
			current_scheme_temp.write(current_scheme_text)
		current_scheme_temp.close()

		# get the path we'll use for the inverted scheme
		inverted_scheme_path = return_inverted_color_scheme_absolute_path()

		# Invert and write out to inverted scheme file
		with open( os.path.join(sublime.packages_path(), 'current_scheme_temp.tmTheme'), 'r', errors='ignore') as scheme_text, open(inverted_scheme_path, 'w') as inverted_color_scheme:

			print('Inverting scheme.')

			# Loop through current scheme temp file
			for line in scheme_text:

				# Grabs lines with colors
				if ( line.find('<string>#') > -1 ):

					# extracts color from <string>#xxxxxx</string> (update this to regex later?)
					original_color = line[ line.find('<string>#') + 9: line.find('</string>') ]

					if ( len(original_color) > 0 ):

						# if color is fff etc convert to 6 char form (update to check if all chars are same later)
						if ( len( original_color ) == 3 ):
							original_color = original_color + original_color

						#inverts color
						color = convert_hex_to_rgb(original_color)
						color = invert_rgb(color)
						color = convert_rgb_to_hex(color)

						inverted_color = ''.join(str(e) for e in color)
						
						line = line.replace (original_color, inverted_color)

				# writes out to inverted scheme file
				inverted_color_scheme.write(line)
					
		# Close original file
		inverted_color_scheme.close()

		# Update the settings file with the new scheme.
		prefs = sublime.load_settings('Preferences.sublime-settings')	
		print('Updating preferences file with color scheme:' + return_inverted_color_scheme_formatted_for_preferences_file())
		prefs.set('color_scheme', return_inverted_color_scheme_formatted_for_preferences_file())
		sublime.save_settings('Preferences.sublime-settings')

		# Remove the temp file
		os.remove( os.path.join(sublime.packages_path(), 'current_scheme_temp.tmTheme') )