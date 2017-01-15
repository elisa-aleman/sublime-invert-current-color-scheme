#!/usr/bin/env python

import sublime
import os

# Returns path to root of sublime text directory relative to machine root
def return_st_root_dir():
	return sublime.packages_path().replace('Packages', '')

# returns current scheme file path retlative to sublime text root directory 
def return_current_color_scheme_relative_to_st_root():
	return sublime.load_settings('Preferences.sublime-settings').get('color_scheme')

# returns absolute path to current scheme file
def return_current_color_scheme_absolute_path():
	return os.path.join(return_st_root_dir(), return_current_color_scheme_relative_to_st_root())

# returns current scheme file's name only
def return_current_color_scheme_name():
	return os.path.basename(return_current_color_scheme_relative_to_st_root())

# returns path to inverted scheme relative to sublime text root directory
def return_inverted_color_scheme_relative_to_st_root():

	if ( return_current_color_scheme_relative_to_st_root().find('Color Scheme - Default') > -1 ):
		if not os.path.exists(os.path.join(sublime.packages_path(), 'Color Scheme - Inverted')):
			os.makedirs(os.path.join(sublime.packages_path(), 'Color Scheme - Inverted'))
		return os.path.join('Packages', 'Color Scheme - Inverted', return_inverted_color_scheme_name())

	return return_current_color_scheme_relative_to_st_root().replace(return_current_color_scheme_name(), return_inverted_color_scheme_name())

# returns color scheme path formatted for color_scheme key in preferences file (X and Windows both using forward slash there.)
def return_inverted_color_scheme_formatted_for_preferences_file():
	return return_inverted_color_scheme_relative_to_st_root().replace('\\', '/')

# returns inverted scheme's name
def return_inverted_color_scheme_name():
	return return_current_color_scheme_name().replace('.tmTheme', '_Inverted.tmTheme')

# returns absolute path to inverted scheme, checks if current scheme is in default scheme package and creates inverted scheme's path appropriately
def return_inverted_color_scheme_absolute_path():
	if ( return_current_color_scheme_relative_to_st_root().find('Color Scheme - Default') > -1 ):
		if not os.path.exists(os.path.join(sublime.packages_path(), 'Color Scheme - Inverted')):
			os.makedirs(os.path.join(sublime.packages_path(), 'Color Scheme - Inverted'))
		return os.path.join(sublime.packages_path(), 'Color Scheme - Inverted', return_inverted_color_scheme_name())
	
	return return_current_color_scheme_absolute_path().replace(return_current_color_scheme_name(), return_inverted_color_scheme_name())