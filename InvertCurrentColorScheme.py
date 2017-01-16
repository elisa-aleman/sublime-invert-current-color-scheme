import sublime
import sublime_plugin
import os
import re


class InvertCurrentColorSchemeCommand(sublime_plugin.TextCommand):

    def convert_hex_to_rgb(self, color):

        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)

        if(len(color) > 6):

            a = (float(int(color[6:8], 16))) / 255

            return [r, g, b, a]

        return [r, g, b]

    def convert_rgb_to_hex(self, color):

        a = format(color[0], '02X')
        b = format(color[1], '02X')
        c = format(color[2], '02X')

        if(len(color) > 3):

            d = format(int(round(color[3] * 255)), '02X')

            return [a, b, c, d]

        return [a, b, c]

    def invert_rgb(self, color):

        r = (color[0] * -1) + 255
        g = (color[1] * -1) + 255
        b = (color[2] * -1) + 255

        if(len(color) > 3):

            a = color[3]
            # perform alpha inversion here if needed
            # a = 1 - a

            return [r, g, b, a]

        return [r, g, b]

    def current_scheme_name(self):
        return os.path.basename(self.current_scheme_relative_to_st_root())

    def current_scheme_text(self):
        return sublime.load_resource(self.current_scheme_relative_to_st_root())

    def current_scheme_relative_to_st_root(self):
        return sublime.load_settings('Preferences.sublime-settings').get('color_scheme')

    def inverted_scheme_name(self):
        return self.current_scheme_name().replace('.tmTheme', '_Inverted.tmTheme')

    def inverted_scheme_absolute_path(self):
        if not os.path.exists(os.path.join(sublime.packages_path(), 'Color Scheme - Inverted')):
            os.makedirs(os.path.join(sublime.packages_path(),
                                     'Color Scheme - Inverted'))
        return os.path.join(sublime.packages_path(), 'Color Scheme - Inverted', self.inverted_scheme_name())

    # returns color scheme path formatted for color_scheme key in preferences
    # file (X and Windows both using forward slash there.)
    def inverted_scheme_path_formatted_for_preferences_file(self):
        return os.path.join('Packages', 'Color Scheme - Inverted', self.inverted_scheme_name()).replace('\\', '/')

    def create_temp_scheme_file(self, text):
        # write out to temp file
        print('Creating temp scheme file.')
        with open(self.temp_scheme_file_path(), 'w', errors='ignore') as current_scheme_temp:
            current_scheme_temp.write(text)
        current_scheme_temp.close()

    def temp_scheme_file_path(self):
        return os.path.join(sublime.packages_path(), 'current_scheme_temp.tmTheme')

    def find_color_in_string(self, string):
        try:
            return re.search('(?:#|0x)?(?:[0-9a-fA-F]{2}){3,4}', string).group(0).replace('#', '')
        except AttributeError:
            # no color found in the original string
            return ''

    def run(self, edit):

        if (self.current_scheme_name().find('_Inverted') > -1):
            return sublime.error_message("Color scheme already inverted.")

        # store current scheme data into string using load_resource, simplifies
        # accessing schemes like the default ones since the are packed in
        # default package.
        self.create_temp_scheme_file(self.current_scheme_text())

        # Invert and write out to inverted scheme file
        with open(self.temp_scheme_file_path(), 'r', errors='ignore') as scheme_text, open(self.inverted_scheme_absolute_path(), 'w') as inverted_color_scheme:

            print('Inverting scheme.')

            # Loop through current scheme temp file
            for line in scheme_text:

                # Grabs lines with colors
                if (line.find('<string>#') > -1):

                    # extracts color from <string>#xxxxxx</string> (update this to regex later?)
                    # original_color = line[ line.find('<string>#') + 9:
                    # line.find('</string>') ]
                    original_color = self.find_color_in_string(line)

                    if (len(original_color) > 0):

                        # if color is fff etc convert to 6 char form (update to
                        # check if all chars are same later)
                        if (len(original_color) == 3):
                            original_color = original_color + original_color

                        # inverts color
                        color = self.convert_hex_to_rgb(original_color)
                        color = self.invert_rgb(color)
                        color = self.convert_rgb_to_hex(color)

                        inverted_color = ''.join(str(e) for e in color)

                        line = line.replace(original_color, inverted_color)

                # writes out to inverted scheme file
                inverted_color_scheme.write(line)

        # Close original file
        inverted_color_scheme.close()

        # Update the settings file with the new scheme.
        prefs = sublime.load_settings('Preferences.sublime-settings')
        print('Updating preferences file with color scheme:' +
              self.inverted_scheme_path_formatted_for_preferences_file())
        prefs.set('color_scheme',
                  self.inverted_scheme_path_formatted_for_preferences_file())
        sublime.save_settings('Preferences.sublime-settings')

        # Remove the temp file
        os.remove(self.temp_scheme_file_path())
