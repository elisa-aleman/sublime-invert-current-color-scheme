import sublime
import sublime_plugin
import os
import re
import colorsys

class InvertCurrentColorSchemeCommand(sublime_plugin.TextCommand):

    #### COLORS

    def convert_hsl_str_to_rgb(self, color_str):
        '''
        Before using colorsys:
            Divide Hue by 360
            Divide Saturation by 100
            Divide Lightness by 100
        After using colorsys:
            Multiply rgb by 255
        '''
        if color_str.startswith("hsl("):
            h_str,s_str,l_str = color_str.replace("hsl(","").replace(")","").replace(" ","").split(",")
            h = int(h_str)/360
            s = float(s_str.replace("%",""))/100
            l = float(l_str.replace("%",""))/100
            rgb_float = colorsys.hls_to_rgb(h,l,s)
            rgb = [i*255 for i in rgb_float]
            rgb = [round(i) for i in rgb]
        if color_str.startswith("hsla("):
            h_str,s_str,l_str,a_str = color_str.replace("hsla(","").replace(")","").replace(" ","").split(",")
            h = int(h_str)/360
            s = float(s_str.replace("%",""))/100
            l = float(l_str.replace("%",""))/100
            a = float(a_str)
            rgb_float = colorsys.hls_to_rgb(h,l,s)
            rgb = [i*255 for i in rgb_float]
            rgb = [round(i) for i in rgb]
            rgb.append(a)
        return rgb

    def convert_rgb_to_hsl_str(self, rgb_color):
        '''
        Before using colorsys:
            Divide rgb by 255
        After using colorsys:
            Multipy Hue by 360
            Multipy Saturation by 100
            Multipy Lightness by 100
        '''
        r = rgb_color[0]/255
        g = rgb_color[1]/255
        b = rgb_color[2]/255
        hls_float = colorsys.rgb_to_hls(r,g,b)
        h = round(hls_float[0]*360)
        l = round(hls_float[1]*100)
        s = round(hls_float[2]*100)
        if len(rgb_color) == 3:
            color_str = "hsl({}, {}%, {}%)".format(h,s,l)
        elif len(rgb_color) == 4:
            a = rgb_color[3]
            color_str = "hsla({}, {}%, {}%, {})".format(h,s,l,a)
        return color_str

    def invert_rgb(self, rgb_color):

        r = (rgb_color[0] * -1) + 255
        g = (rgb_color[1] * -1) + 255
        b = (rgb_color[2] * -1) + 255

        if(len(rgb_color) > 3):

            a = rgb_color[3]
            # perform alpha inversion here if needed
            # a = 1 - a

            return [r, g, b, a]

        return [r, g, b]

    def invert_color_str(self, color_str):
        # inverts color
        rgb_color = self.convert_hsl_str_to_rgb(color_str)
        # inverted_color = self.convert_hex_to_rgb(inverted_color)
        inverted_color = self.invert_rgb(rgb_color)
        # inverted_color = self.convert_rgb_to_hex(inverted_color)
        inverted_color_str = self.convert_rgb_to_hsl_str(inverted_color)
        return inverted_color_str

    def find_color_in_string(self, string):
        '''
        Finds hsl() and hsla() colors that are used in the newer builds
        '''
        try:
            return re.search("hsl(a*)\((.*?)\)",string).group(0)
        except AttributeError:
            # no color found in the original string
            return ''

    #### SCHEMES

    def current_scheme_name(self):
        return sublime.load_settings("Preferences.sublime-settings").get("color_scheme")

    def current_scheme_text(self):
        cur_resources = sublime.find_resources(self.current_scheme_name())
        return sublime.load_resource(cur_resources[0])
    
    def current_scheme_dict(self):
        return sublime.decode_value(self.current_scheme_text())

    def inverted_scheme_name(self):
        return self.current_scheme_name().replace('.sublime-color-scheme', '_Inverted.sublime-color-scheme')

    def inverted_scheme_absolute_path(self):
        if not os.path.exists(os.path.join(sublime.packages_path(), 'User')):
            os.makedirs(os.path.join(sublime.packages_path(),
                                     'User'))
        # Has to be saved under the User folder for it to be read by the preferences file
        return os.path.join(sublime.packages_path(), 'User', self.inverted_scheme_name())

    def write_sublime_file(self, attr_dict, path):
        sublime_text = sublime.encode_value(attr_dict, pretty=True)
        with open(path, 'w', errors='ignore') as f:
            f.write(sublime_text)

    def temp_scheme_file_path(self):
        return os.path.join(sublime.packages_path(), 'User', 'current_scheme_temp.sublime-color-scheme')

    def invert_scheme(self):
        # Load current scheme into a dictionary to easily access the keys
        scheme_dict = self.current_scheme_dict()
        
        # Tried to add inverted_ to variable names but ended up repeat replacing some
        # current_var_names = scheme_dict['variables']
        # inverted_keys = {}

        # # Invert colors in a dictionary first to access the same keys later
        # for key in current_var_names.keys():
        #     new_key = "inverted_"+key
        #     inverted_keys[key] = new_key

        # Empty string to keep changes
        inverted_scheme_text = ""

        # Load current scheme into temp file to read line by line
        self.write_sublime_file(scheme_dict, self.temp_scheme_file_path())

        # Invert and write out to inverted scheme file
        with open(self.temp_scheme_file_path(), 'r', errors='ignore') as scheme_text:
            # Loop through current scheme temp file
            for line in scheme_text:
                # Grabs lines with colors
                if (line.find('hsl') > -1):
                    original_color = self.find_color_in_string(line)
                    inverted_color = self.invert_color_str(original_color)
                    new_line = line.replace(original_color,inverted_color)
                else:
                    new_line = line
                if not new_line.endswith('\n'):
                    new_line+='\n'
                inverted_scheme_text += new_line

        inverted_scheme_dict = sublime.decode_value(inverted_scheme_text)

        # Remove the temp file
        os.remove(self.temp_scheme_file_path())

        return inverted_scheme_dict

    ##### THEMES (Not working properly yet)

    # def current_theme_name(self):
    #     return sublime.load_settings("Preferences.sublime-settings").get("theme")

    # def current_theme_text(self):
    #     cur_resources = sublime.find_resources(self.current_theme_name())
    #     return sublime.load_resource(cur_resources[0])

    # def current_theme_dict(self):
    #     return sublime.decode_value(self.current_theme_text())

    # def inverted_theme_name(self):
    #     return self.current_theme_name().replace('.sublime-theme', '_Inverted.sublime-theme')

    # def inverted_theme_absolute_path(self):
    #     if not os.path.exists(os.path.join(sublime.packages_path(), 'User')):
    #         os.makedirs(os.path.join(sublime.packages_path(),
    #                                  'User'))
    #     # Has to be saved under the User folder for it to be read by the preferences file
    #     return os.path.join(sublime.packages_path(), 'User', self.inverted_theme_name())

    # def temp_theme_file_path(self):
    #     return os.path.join(sublime.packages_path(), 'User', 'current_theme_temp.sublime-theme')

    # def invert_theme(self):
    #     # Load current theme into a dictionary to easily access the keys
    #     theme_dict = self.current_theme_dict()

    #     # Empty string to keep changes
    #     inverted_theme_text = ""

    #     # Load current theme into temp file to read line by line
    #     self.write_sublime_file(theme_dict, self.temp_theme_file_path())

    #     # Invert and write out to inverted theme file
    #     with open(self.temp_theme_file_path(), 'r', errors='ignore') as theme_text:
    #         # Loop through current theme temp file
    #         for line in theme_text:
    #             # Grabs lines with colors
    #             if (line.find('hsl') > -1):
    #                 original_color = self.find_color_in_string(line)
    #                 inverted_color = self.invert_color_str(original_color)
    #                 new_line = line.replace(original_color,inverted_color)

    #             ## Unlike schemes, not all colors are hsl, some are based around a base color and the light values are changed
    #             ## This results in an incomplete inversion.

    #             else:
    #                 new_line = line
    #             if not new_line.endswith('\n'):
    #                 new_line+='\n'
    #             inverted_theme_text += new_line

    #     # Invert white variable
    #     inverted_theme_text = inverted_theme_text.replace("white","black")

    #     # Invert dark to light themes... I'd have to set up for both possibilities
    #     inverted_theme_text = inverted_theme_text.replace("dark","light")

    #     inverted_theme_dict = sublime.decode_value(inverted_theme_text)

    #     # Remove the temp file
    #     os.remove(self.temp_theme_file_path())

    #     return inverted_theme_dict

    #### MAIN

    def run(self, edit):
        ##### SCHEME INVERT
        print("Color Scheme Invert process started")
        if (self.current_scheme_name().find('_Inverted') > -1):
            print("Reversing the inverted color scheme to the original")
            original_name = self.current_scheme_name().replace("_Inverted","")
            sublime.load_settings("Preferences.sublime-settings").erase("color_scheme")
            sublime.load_settings("Preferences.sublime-settings").set("color_scheme", original_name)
            sublime.save_settings('Preferences.sublime-settings')
        else:
            # Check if there's already an inverted scheme file
            if not os.path.exists(self.inverted_scheme_absolute_path()):
                print('Inverted scheme file not already made. Inverting scheme.')
                inverted_scheme_dict = self.invert_scheme()
                self.write_sublime_file(inverted_scheme_dict, self.inverted_scheme_absolute_path())

            # Update the settings file with the new scheme.
            print('Updating preferences file with color scheme:' +
                  self.inverted_scheme_name())

            sublime.load_settings("Preferences.sublime-settings").erase("color_scheme")
            sublime.load_settings("Preferences.sublime-settings").set("color_scheme",
                      self.inverted_scheme_name())
            
            sublime.save_settings('Preferences.sublime-settings')
        print("Color Scheme Invert process completed")
        # Works properly
        #####
        ##### THEME INVERT (currently not working)
        # print("Proceeding with Theme Invert process")
        # if (self.current_theme_name().find('_Inverted') > -1):
        #     print("Reversing the inverted theme to the original")
        #     original_name = self.current_theme_name().replace("_Inverted","")
        #     sublime.load_settings("Preferences.sublime-settings").erase("theme")
        #     sublime.load_settings("Preferences.sublime-settings").set("theme", original_name)
        #     sublime.save_settings('Preferences.sublime-settings')
        # else:
        #     # Check if there's already an inverted theme file
        #     if not os.path.exists(self.inverted_theme_absolute_path()):
        #         print('Inverted theme file not already made. Inverting theme.')
        #         inverted_theme_dict = self.invert_theme()
        #         self.write_sublime_file(inverted_theme_dict, self.inverted_theme_absolute_path())

        #     # Update the settings file with the new theme.
        #     print('Updating preferences file with theme:' +
        #           self.inverted_theme_name())

        #     sublime.load_settings("Preferences.sublime-settings").erase("theme")
        #     sublime.load_settings("Preferences.sublime-settings").set("theme",
        #               self.inverted_theme_name())
            
        #     sublime.save_settings('Preferences.sublime-settings')
        # print("Theme Invert process completed")
        #####
        # Sublime fails to read theme and resets to "auto"
