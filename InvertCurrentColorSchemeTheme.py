import sublime
import sublime_plugin
import sys
import os

from .color_utils import *

class InvertCurrentColorSchemeCommand(sublime_plugin.TextCommand):

	# Returns path witout extension
	def return_current_color_scheme(self):

		# when using this you will need to work out the first part of the run method since it doesn't expect the file extension
		preferences = sublime.load_settings('Preferences.sublime-settings')
		return preferences.get('color_scheme')

	def run(self, edit):
		
		current_color_scheme = self.return_current_color_scheme() 
		new_color_scheme     = current_color_scheme.replace('.tmTheme', '_Inverted.tmTheme')


		if ( current_color_scheme.find('_Inverted') > -1 ):
			return sublime.error_message("Color scheme already inverted.")


		# 

		if not os.path.exists(os.path.join(sublime.packages_path(), 'User', 'InvertedColorSchemes')):
			os.makedirs(os.path.join(sublime.packages_path(), 'User', 'InvertedColorSchemes'))

		original_name = os.path.splitext(os.path.basename(current_color_scheme))[0]
		name = original_name + '_Inverted'
		scheme_path = os.path.join(sublime.packages_path(), 'User', 'InvertedColorSchemes', name + '.tmTheme')

		#






		scheme_text = sublime.load_resource(current_color_scheme)

		# Opens scheme 
		with open(scheme_path, 'w') as inverted_color_scheme:

			# original_color_scheme = original_color_scheme.decode('utf-8')

			# Loop through file
			for line in scheme_text:

				# line=line.strip()

				# Grabs lines with colors
				if ( line.find('<string>#') > -1 ):

					# extracts color from <string>#xxxxxx</string> (update this to regex later)
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

				# writes out to new scheme file
				inverted_color_scheme.write(line)
					
		# Close original file
		inverted_color_scheme.close()

		# Replace the settings file with a new one containing the inverted theme
		packages_path        = sublime.packages_path()
		preferences_path     = packages_path + '/User/Preferences.sublime-settings'
		new_preferences_path = packages_path + '/User/Preferences.sublime-settings-new'

		with open( preferences_path, 'r' ) as sublime_settings, open(new_preferences_path, 'w') as new_sublime_settings:
			for line in sublime_settings:
				if ( line.find('"color_scheme":') > -1 ):

					new_color_scheme = line[ 0 : line.find('.tmTheme') ] + '_Inverted.tmTheme",'

					line = line.replace(line, new_color_scheme)

				new_sublime_settings.write(line)

		sublime_settings.close()

		os.remove(preferences_path)
		os.rename(new_preferences_path, new_preferences_path.replace('-new', ''))