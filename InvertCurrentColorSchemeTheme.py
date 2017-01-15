#!/usr/bin/env python

import sublime
import sublime_plugin
import sys
import os
import xml.etree.ElementTree as ET

from .color_utils import *

class InvertCurrentColorSchemeCommand(sublime_plugin.TextCommand):
		 	
	# Returns path to root of sublime text directory relative to machine root
	def return_st_root_dir(self):
		return sublime.packages_path().replace('Packages', '')

	# returns current scheme file path retlative to sublime text root directory 
	def return_current_color_scheme_relative_to_st_root(self):
		return sublime.load_settings('Preferences.sublime-settings').get('color_scheme')

	# returns absolute path to current scheme file
	def return_current_color_scheme_absolute_path(self):
		return os.path.join(self.return_st_root_dir(), self.return_current_color_scheme_relative_to_st_root())

	# returns current scheme file's name only
	def return_current_color_scheme_name(self):
		return os.path.basename(self.return_current_color_scheme_relative_to_st_root())

	# returns path to inverted scheme relative to sublime text root directory
	def return_inverted_color_scheme_relative_to_st_root(self):
		return self.return_current_color_scheme_relative_to_st_root().replace(self.return_current_color_scheme_name(), self.return_inverted_color_scheme_name())

	# returns inverted scheme's name
	def return_inverted_color_scheme_name(self):
		return self.return_current_color_scheme_name().replace('.tmTheme', '_Inverted.tmTheme')

	# returns absolute path to inverted scheme, checks if current scheme is in default scheme package and creates inverted scheme's path appropriately
	def return_inverted_color_scheme_absolute_path(self):
		if ( self.return_current_color_scheme_name().find('Color Scheme - Default') > -1 ):
			if not os.path.exists(os.path.join(sublime.packages_path(), 'User', 'InvertedColorSchemes')):
				os.makedirs(os.path.join(sublime.packages_path(), 'User', 'InvertedColorSchemes'))
			return os.path.join(sublime.packages_path(), 'User', 'InvertedColorSchemes', self.return_inverted_color_scheme_name())
		
		return self.return_current_color_scheme_absolute_path().replace(self.return_current_color_scheme_name(), self.return_inverted_color_scheme_name())

	def run(self, edit):

		if ( self.return_current_color_scheme_name().find('_Inverted') > -1 ):
			return sublime.error_message("Color scheme already inverted.")

		# store current scheme data into string using load_resource, simplifies accessing schemes like the default ones since the are packed in default package.
		current_scheme_text = sublime.load_resource(self.return_current_color_scheme_relative_to_st_root())

		# write out to temp file
		with open(os.path.join(sublime.packages_path(), 'current_scheme_temp.tmTheme'), 'w') as current_scheme_temp:
			current_scheme_temp.write(current_scheme_text)
		current_scheme_temp.close()

		# get the path we'll use for the inverted scheme
		inverted_scheme_path = self.return_inverted_color_scheme_absolute_path()

		# Invert and write out to inverted scheme file
		with open( os.path.join(sublime.packages_path(), 'current_scheme_temp.tmTheme'), 'r', errors='ignore') as scheme_text, open(inverted_scheme_path, 'w') as inverted_color_scheme:

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
		prefs.set('color_scheme', self.return_inverted_color_scheme_relative_to_st_root())
		sublime.save_settings('Preferences.sublime-settings')

		# Remove the temp file
		os.remove(os.path.join(sublime.packages_path()), 'current_scheme_temp.tmTheme')