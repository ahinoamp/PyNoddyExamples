'''Noddy history file wrapper
Created on 24/03/2014

@author: Florian Wellmann
'''

import time  # for header in model generation
import numpy as np
# import numpy as np
# import matplotlib.pyplot as plt

from . import events


class NoddyHistory(object):
    """Class container for Noddy history files"""

    def __init__(self, history=None, **kwds):
        """Methods to analyse and change Noddy history files
        
        **Arguments**:
            - *history* = string : Name of Noddy history file
            
        **Optional Keywords**:
            - *url* = url : link to history file on web (e.g. to download 
            and open directly from Atlas of Structural Geophysics,
            http://virtualexplorer.com.au/special/noddyatlas/index.html
            
            - *verbose* = True if this function should print output to the printstream. Default is False.
            
        Note: if both a (local) history is given and a URL, the local
        file is opened!
        """

        vb = kwds.get('verbose', False)

        if history is None:
            if "url" in kwds:
                self.load_history_from_url(kwds['url'])
                self.determine_events(verbose=vb)
            else:
                # generate a new history
                self.create_new_history()
        else:
            # load existing history
            self.load_history(history)
            self.determine_events(verbose=vb)

    def __repr__(self):
        """Print out model information"""
        return self.get_info_string()

    def info(self, **kwds):
        """Print out model information
        
        **Optional keywords**:
            - *events_only* = bool : only information on events
        """
        print((self.get_info_string(**kwds)))

    def get_info_string(self, **kwds):
        """Get model information as string
        
        **Optional keywords**:
            - *events_only* = bool : only information on events
        """
        events_only = kwds.get("events_only", False)

        local_os = ""

        if not events_only:
            # First: check if all information available
            if not hasattr(self, 'extent_x'): self.get_extent()
            if not hasattr(self, 'origin_x'): self.get_origin()
            if not hasattr(self, 'cube_size'): self.get_cube_size()
            if not hasattr(self, 'filename'): self.get_filename()
            if not hasattr(self, 'date_saved'): self.get_date_saved()
            local_os += (60 * "*" + "\n\t\t\tModel Information\n" + 60 * "*")
            local_os += ("\n\n")
        if self.n_events == 0:
            local_os += ("The model does not yet contain any events\n")
        else:
            local_os += ("This model consists of %d events:\n" % self.n_events)
            for k, ev in list(self.events.items()):
                local_os += ("\t(%d) - %s\n" % (k, ev.event_type))
        if not events_only:
            local_os += ("The model extent is:\n")
            local_os += ("\tx - %.1f m\n" % self.extent_x)
            local_os += ("\ty - %.1f m\n" % self.extent_y)
            local_os += ("\tz - %.1f m\n" % self.extent_z)

            local_os += ("Number of cells in each direction:\n")
            local_os += ("\tnx = %d\n" % (self.extent_x / self.cube_size))
            local_os += ("\tny = %d\n" % (self.extent_y / self.cube_size))
            local_os += ("\tnz = %d\n" % (self.extent_z / self.cube_size))

            local_os += ("The model origin is located at: \n\t(%.1f, %.1f, %.1f)\n" % (self.origin_x,
                                                                                       self.origin_y,
                                                                                       self.origin_z))

            local_os += ("The cubesize for model export is: \n\t%d m\n" % self.cube_size)
            # and now some metadata
            local_os += ("\n\n")
            local_os += (60 * "*" + "\n\t\t\tMeta Data\n" + 60 * "*")
            local_os += ("\n\n")
            local_os += ("The filename of the model is:\n\t%s\n" % self.filename)
            local_os += ("It was last saved (if origin was a history file!) at:\n\t%s\n" % self.date_saved)

        return local_os

    def get_origin(self):
        """Get coordinates of model origin and return and store in local variables
        
        **Returns**: (origin_x, origin_y, origin_z)
        """
        # check if footer_lines exist (e.g. read in from file)
        # if not: create from template
        if not hasattr(self, "footer_lines"):
            self.create_footer_from_template()

        for i, line in enumerate(self.footer_lines):
            if "Origin X" in line:
                self.origin_x = float(self.footer_lines[i].split("=")[1])
                self.origin_y = float(self.footer_lines[i + 1].split("=")[1])
                self.origin_z = float(self.footer_lines[i + 2].split("=")[1])
                break

        return (self.origin_x, self.origin_y, self.origin_z)

    def set_origin(self, origin_x, origin_y, origin_z):
        """Set coordinates of model origin and update local variables
        
        **Arguments**:
            - *origin_x* = float : x-location of model origin
            - *origin_y* = float : y-location of model origin
            - *origin_z* = float : z-location of model origin
        """
        # check if footer_lines exist (e.g. read in from file)
        # if not: create from template
        if not hasattr(self, "footer_lines"):
            self.create_footer_from_template()

        self.origin_x = origin_x
        self.origin_y = origin_y
        self.origin_z = origin_z
        origin_x_line = "    Origin X    =   %.2f\n" % origin_x
        origin_y_line = "    Origin Y    =   %.2f\n" % origin_y
        origin_z_line = "    Origin Z    =   %.2f\n" % origin_z

        for i, line in enumerate(self.footer_lines):
            if "Origin X" in line:
                self.footer_lines[i] = origin_x_line
                self.footer_lines[i + 1] = origin_y_line
                self.footer_lines[i + 2] = origin_z_line
                break

    def get_extent(self):
        """Get model extent and return and store in local variables
        
        **Returns**: (extent_x, extent_y, extent_z)
        """
        # check if footer_lines exist (e.g. read in from file)
        # if not: create from template
        if not hasattr(self, "footer_lines"):
            self.create_footer_from_template()

        for i, line in enumerate(self.footer_lines):
            if "Length X" in line:
                self.extent_x = float(self.footer_lines[i].split("=")[1])
                self.extent_y = float(self.footer_lines[i + 1].split("=")[1])
                self.extent_z = float(self.footer_lines[i + 2].split("=")[1])
                break

        return (self.extent_x, self.extent_y, self.extent_z)

    def set_extent(self, extent_x, extent_y, extent_z):
        """Set model extent and update local variables
        
        **Arguments**:
            - *extent_x* = float : extent in x-direction
            - *extent_y* = float : extent in y-direction
            - *extent_z* = float : extent in z-direction
        """
        # check if footer_lines exist (e.g. read in from file)
        # if not: create from template
        if not hasattr(self, "footer_lines"):
            self.create_footer_from_template()

        self.extent_x = extent_x
        self.extent_y = extent_y
        self.extent_z = extent_z
        extent_x_line = "    Length X    =   %.2f\n" % extent_x
        extent_y_line = "    Length Y    =   %.2f\n" % extent_y
        extent_z_line = "    Length Z    =   %.2f\n" % extent_z

        for i, line in enumerate(self.footer_lines):
            if "Length X" in line:
                self.footer_lines[i] = extent_x_line
                self.footer_lines[i + 1] = extent_y_line
                self.footer_lines[i + 2] = extent_z_line
                break

    def get_drillhole_data(self, x, y, **kwds):
        """Get geology values along 1-D profile at position x,y with a 1 m resolution
        
        The following steps are performed:
        1. creates a copy of the entire object,
        2. sets values of origin, extent and geology cube size, 
        3. saves model to a temporary file, 
        4. runs Noddy on that file
        5. opens and analyses output
        6. deletes temporary files
        
        Note: this method only works if write access to current directory
        is enabled and noddy can be executed!
        
        **Arguments**:
            - *x* = float: x-position of drillhole
            - *y* = float: y-position of drillhole
        
        **Optional Arguments**:
            - *z_min* = float : minimum depth of drillhole (default: model range)
            - *z_max* = float : maximum depth of drillhole (default: model range)
            - *resolution* = float : resolution along profile (default: 1 m)
        """
        # resolve keywords
        resolution = kwds.get("resolution", 1)
        self.get_extent()
        self.get_origin()
        z_min = kwds.get("z_min", self.origin_z)
        z_max = kwds.get("z_max", self.extent_z)
        # 1. create copy
        import copy
        tmp_his = copy.deepcopy(self)
        tmp_his.write_history("test.his")
        # 2. set values
        tmp_his.set_origin(x, y, z_min)
        tmp_his.set_extent(resolution, resolution, z_max)
        tmp_his.change_cube_size(resolution)
        # 3. save temporary file
        tmp_his_file = "tmp_1D_drillhole.his"
        tmp_his.write_history(tmp_his_file)
        tmp_out_file = "tmp_1d_out"
        # 4. run noddy
        import pynoddy
        import pynoddy.output

        pynoddy.compute_model(tmp_his_file, tmp_out_file)
        # 5. open output
        tmp_out = pynoddy.output.NoddyOutput(tmp_out_file)
        # 6. 
        return tmp_out.block[0, 0, :]

    def load_history(self, history):
        """Load Noddy history
        
        **Arguments**:
            - *history* = string : Name of Noddy history file
        """
        self.history_lines = open(history, 'r').readlines()
        # set flag for model loaded from file
        self._from_file = True
        # get footer lines 
        self.get_footer_lines()

    def load_history_from_url(self, url):
        """Directly load a Noddy history from a URL
        
        This method is useful to load a model from the Structural Geophysics
        Atlas on the pages of the Virtual Explorer.
        See: http://tectonique.net/asg
        
        **Arguments**:
            - *url* : url of history file
        """
        # test if python 2 or 3 are running for appropriate urllib functionality
        import sys
        if sys.version_info[0] < 3:
            import urllib2
            response = urllib2.urlopen(url)
            tmp_lines = response.read().split("\n")
        else:
            # from urllib import urlopen # , urllib.error, urllib.parse
            import urllib
            with urllib.urlrequest.urlopen(url) as f:
                output = f.read().decode('utf-8')
            # response = urllib.request.urlopen(url)
            tmp_lines = output.split("\n")
            # tmp_lines = response.read().decode("utf-8").split("\n")

        self.history_lines = []
        for line in tmp_lines:
            # append EOL again for consistency
            self.history_lines.append(line + "\n")
        # set flag for model loaded from URL
        self._from_url = True
        # get footer lines 
        self.get_footer_lines()

    def determine_model_stratigraphy(self):
        """Determine stratigraphy of entire model from all events"""
        self.model_stratigraphy = []
        for e in np.sort(list(self.events.keys())):
            if self.events[e].event_type == 'STRATIGRAPHY':
                self.model_stratigraphy += self.events[e].layer_names
            if self.events[e].event_type == 'UNCONFORMITY':
                self.model_stratigraphy += self.events[e].layer_names
            if self.events[e].event_type == 'DYKE':
                self.model_stratigraphy += self.events[e].name
            if self.events[e].event_type == 'PLUG':
                self.model_stratigraphy += self.events[e].name

    def determine_events(self, **kwds):
        """Determine events and save line numbers
        
        .. note:: Parsing of the history file is based on a fixed Noddy output order. 
                  If this is, for some reason (e.g. in a changed version of Noddy) not the case, then
                  this parsing might fail!
        
          **Optional Keywords**:
           - verbose = True if this function is should write to the print bufffer, otherwise False. Default is False.
        """

        vb = kwds.get('verbose', False)

        self._raw_events = []
        for i, line in enumerate(self.history_lines):
            if "No of Events" in line:
                self.n_events = int(line.split("=")[1])
            elif "Event #" in line:
                event = {'type': line.split('=')[1].rstrip(), 'num': int(line[7:9]), 'line_start': i}
                self._raw_events.append(event)
            # finally: if the definition for BlockOptions starts, the event definition is over
            elif "BlockOptions" in line:
                last_event_stop = i - 2
        # now: find the line ends for the single event blocks
        for i, event in enumerate(self._raw_events[1:]):
            self._raw_events[i]['line_end'] = event['line_start'] - 1
        # now adjust for last event
        self._raw_events[-1]['line_end'] = last_event_stop

        self.events = {}  # idea: create events as dictionary so that it is easier
        # to swap order later!
        # now create proper event objects for these events
        if vb:
            print("Loaded model with the following events:")

        for e in self._raw_events:
            event_lines = self.history_lines[e['line_start']:e['line_end']+1]

            if vb:
                print((e['type']))

            if 'FAULT' in e['type']:
                ev = events.Fault(lines=event_lines)
            elif 'SHEAR_ZONE' in e['type']:
                ev = events.Shear(lines=event_lines)
            elif 'FOLD' in e['type']:
                ev = events.Fold(lines=event_lines)
            elif 'UNCONFORMITY' in e['type']:
                ev = events.Unconformity(lines=event_lines)
            elif 'STRATIGRAPHY' in e['type']:
                # event_lines = event_lines[:-1]
                ev = events.Stratigraphy(lines=event_lines)
            elif 'TILT' in e['type']:  # AK
                ev = events.Tilt(lines=event_lines)
            elif 'DYKE' in e['type']:
                ev = events.Dyke(lines=event_lines)
            elif 'PLUG' in e['type']:
                ev = events.Plug(lines=event_lines)
            elif 'STRAIN' in e['type']:
                ev = events.Strain(lines=event_lines)
            else:
                print(("Warning: event of type %s has not been implemented in PyNoddy yet" % e['type']))
                continue
            # now set shared attributes (those defined in superclass Event)
            order = e['num']  # retrieve event number
            self.events[order] = ev  # store events sequentially

        # determine overall begin and end of the history events
        self.all_events_begin = self._raw_events[0]['line_start']
        self.all_events_end = self._raw_events[-1]['line_end']

    def copy_events(self):
        """Create a copy of the current event state"""
        import copy
        return copy.deepcopy(self.events)

    def get_cube_size(self, **kwds):
        """Determine cube size for model export
           **Optional Args**
            -type: choose geology or geophysics cube size to return. Should be either 'Geology' (default) or 'Geophysics'
        """

        # get args
        sim_type = kwds.get("type", 'Geophysics')  # everything seems to use this
        cube_string = 'Geophysics Cube Size'  # get geology cube size by default
        if ('Geology' in sim_type):
            cube_string = 'Geology Cube Size'  # instead get geology cube size
            print("Warning: pynoddy uses the geophysics cube size for all calculations... changing the geology cube size will have no effect internally.")

            # check if footer exists, if not: create from template
        if not hasattr(self, "footer_lines"):
            self.create_footer_from_template()

        for line in self.footer_lines:
            if cube_string in line:
                self.cube_size = float(line.split('=')[1].rstrip())
                return self.cube_size

    def get_filename(self):
        """Determine model filename from history file/ header"""
        self.filename = self.history_lines[0].split('=')[1].rstrip()

    def get_date_saved(self):
        """Determine the last savepoint of the file"""
        self.date_saved = self.history_lines[1].split('=')[1].rstrip()

    def change_cube_size(self, cube_size, **kwds):
        """Change the model cube size (isotropic)
        
        **Arguments**:
            - *cube_size* = float : new model cube size
        """

        # check if footer_lines exist (e.g. read in from file)
        # if not: create from template
        if not hasattr(self, "footer_lines"):
            self.create_footer_from_template()

        #        lines_new = self.history_lines[:]
        for i, line in enumerate(self.footer_lines):
            if "Geophysics Cube Size" in line:  # correct line, make change
                l = line.split('=')
                l_new = '%7.2f\r\n' % cube_size
                line_new = l[0] + "=" + l_new
                self.footer_lines[i] = line_new

            if "Geology Cube Size" in line:  # change geology cube size also
                l = line.split('=')
                l_new = '%7.2f\r\n' % cube_size
                line_new = l[0] + "=" + l_new
                self.footer_lines[i] = line_new
                # assign changed lines back to object
            #        self.history_lines = lines_new[:]

    def get_footer_lines(self):
        """Get the footer lines from self.history_lines
        
        The footer contains everything below events (all settings, etc.)"""
        # get id of footer from history lines
        for i, line in enumerate(self.history_lines):
            if "#BlockOptions" in line:
                break
        self.footer_lines = self.history_lines[i:]

    def create_footer_from_template(self):
        """Create model footer (with all settings) from template"""
        self.footer_lines = []
        for line in _Templates().footer.split("\n"):
            line = line.replace("    ", "\t")
            self.footer_lines.append(line + "\n")

    def swap_events(self, event_num_1, event_num_2):
        """Swap two geological events in the timeline
        
        **Arguments**:
            - *event_num_1/2* = int : number of events to be swapped ("order")
        """
        # events have to be copied, otherwise only a reference is passed!
        event_tmp = self.events[event_num_1]
        self.events[event_num_1] = self.events[event_num_2]
        self.events[event_num_2] = event_tmp
        self.update_event_numbers()

    def reorder_events(self, reorder_dict):
        """Reorder events accoring to assignment in reorder_dict
        
        **Arguments**:
            - *reorder_dict* = dict : for example {1 : 2, 2 : 3, 3 : 1}
        """
        tmp_events = self.events.copy()
        for key, value in list(reorder_dict.items()):
            try:
                tmp_events[value] = self.events[key]
            except KeyError:
                print(("Event with id %d is not defined, please check!" % value))
        self.events = tmp_events.copy()
        self.update_event_numbers()

    def update_event_numbers(self):
        """Update event numbers in 'Event #' line in noddy history file"""
        for key, event in list(self.events.items()):
            event.set_event_number(key)

    def update_all_event_properties(self):
        """Update properties of all events - in case changes were made"""
        for event in list(self.events.values()):
            event.update_properties()

        #
        # class NewHistory():
        #    """Methods to create a Noddy model"""
        #

    def create_new_history(self):
        """Methods to create a Noddy model
        
        """
        # set event counter
        self.event_counter = 0
        self.all_events_begin = 7  # default after header
        self.all_events_end = 7
        # initialise history lines
        self.history_lines = []
        self.events = {}

    def get_ev_counter(self):
        """Event counter for implicit and continuous definition of events"""
        self.event_counter += 1
        return self.event_counter

    def add_event(self, event_type, event_options, **kwds):
        """Add an event type to history
        
        **Arguments**:
            - *event_type* = string : type of event, legal options to date are:
            'stratigraphy', 'fault', 'fold', 'unconformity'
            - *event_options* = list : required options to create event (event dependent)
        **Optional keywords**:
            - *event_num* = int : event number (default: implicitly defined with increasing counter)
        """

        event_num = kwds.get("event_num", self.get_ev_counter())

        if event_type == 'stratigraphy':
            ev = self._create_stratigraphy(event_options)
            ev.event_type = 'STRATIGRAPHY'

        elif event_type == 'fault':
            ev = self._create_fault(event_options)
            ev.event_type = 'FAULT'

        elif event_type == 'tilt':  # AK
            ev = self._create_tilt(event_options)
            ev.event_type = 'TILT'

        elif event_type == 'unconformity':  # AK
            ev = self._create_unconformity(event_options)
            ev.event_type = 'UNCONFORMITY'

        elif event_type == 'fold':
            ev = self._create_fold(event_options)
            ev.event_type = 'FOLD'


        else:
            raise NameError('Event type %s not (yet) implemented' % event_type)

        ev.set_event_number(event_num)
        self.events[event_num] = ev

        # update beginning and ending of events in history
        self.all_events_end = self.all_events_end + len(ev.event_lines)

        # add event to history lines, as well (for consistency with other methods)
        self.history_lines[:self.all_events_begin] + \
        ev.event_lines + \
        self.history_lines[self.all_events_end:]

    def _create_header(self):
        """Create model header, include actual date"""
        t = time.localtime()  # get current time
        time_string = "%d/%d/%d %d:%d:%d" % (t.tm_mday,
                                             t.tm_mon,
                                             t.tm_year,
                                             t.tm_hour,
                                             t.tm_min,
                                             t.tm_sec)
        self.header_lines = """#Filename = """ + self.filename + """ 
#Date Saved = """ + time_string + """
FileType = 111
Version = 7.11

"""

    @staticmethod
    def _create_stratigraphy(event_options):
        """Create a stratigraphy event
        
        **Arguments**:
            - *event_options* = list : list of required and optional settings for event
            Options are:
            'num_layers' = int : number of layers (required)
            'layer_names' = list of strings : names for layers (default names otherwise)
            'layer_thickness' = list of floats : thicknesses for all layers
        """
        ev = events.Stratigraphy()
        tmp_lines = [""]
        tmp_lines.append("\tNum Layers\t= %d" % event_options['num_layers'])
        for i in range(event_options['num_layers']):
            """Add stratigraphy layers"""
            layer_name = event_options['layer_names'][i]
            try:
                density = event_options['density'][i]
            except KeyError:
                density = 4.0
            cum_thickness = np.cumsum(event_options['layer_thickness'])
            layer_lines = _Templates().strati_layer
            # now replace required variables
            layer_lines = layer_lines.replace("$NAME$", layer_name)
            layer_lines = layer_lines.replace("$HEIGHT$", "%.1f" % cum_thickness[i])
            layer_lines = layer_lines.replace("    ", "\t")
            layer_lines = layer_lines.replace("$DENSITY$", "%e" % density)
            # split lines and add to event lines list:
            for layer_line in layer_lines.split("\n"):
                tmp_lines.append(layer_line)

        # append event name
        tmp_lines.append("""\tName\t= Strat""")

        # event lines are defined in list:
        tmp_lines_list = []
        for line in tmp_lines:
            tmp_lines_list.append(line + "\n")
        ev.set_event_lines(tmp_lines_list)
        ev.num_layers = event_options['num_layers']
        return ev

    def _create_fault(self, event_options):
        """Create a fault event
        
        **Arguments**:
            - *event_options* = list : list of required and optional settings for event;
            Options are:
            'name' = string : name of fault event
            'pos' = (x,y,z) : position of reference point (floats)
                .. note::     for convenience, it is possible to assign 'top' to z
                              for position at "surface"
            'dip_dir' = [0,360] : dip direction of fault
            'dip' = [0,90] : dip angle of fault
            'slip' = float : slip along fault
            'geometry' = 'Translation', 'Curved' : geometry of fault plane (default: 'Translation')
            'movement' = 'Hanging Wall', 'Foot Wall' : relative block movement (default: 'Hanging Wall')
            'rotation' = float: fault rotation (default: 30.0)
            'amplitude' = float: (default: 2000.0)
            'radius' = float: (default: 1000.0)
            'xaxis' = float: (default: 2000.0)
            'yaxis' = float: (default: 2000.0)
            'zaxis' = float: (default: 2000.0)
        """
        ev = events.Fault()
        tmp_lines = [""]
        fault_lines = _Templates.fault
        # substitute text with according values
        fault_lines = fault_lines.replace("$NAME$", event_options['name'])
        fault_lines = fault_lines.replace("$POS_X$", "%.1f" % event_options['pos'][0])
        fault_lines = fault_lines.replace("$POS_Y$", "%.1f" % event_options['pos'][1])
        if event_options['pos'] == 'top':
            # recalculate z-value to be at top of model
            z = self.zmax
            fault_lines = fault_lines.replace("$POS_Z$", "%.1f" % z)
        else:
            fault_lines = fault_lines.replace("$POS_Z$", "%.1f" % event_options['pos'][2])
        fault_lines = fault_lines.replace("$DIP_DIR$", "%.1f" % event_options['dip_dir'])
        fault_lines = fault_lines.replace("$DIP$", "%.1f" % event_options['dip'])
        fault_lines = fault_lines.replace("$SLIP$", "%.1f" % event_options['slip'])

        fault_lines = fault_lines.replace("$MOVEMENT$", "%s" % event_options.get('movement', 'Hanging Wall'))
        fault_lines = fault_lines.replace("$GEOMETRY$", "%s" % event_options.get('geometry', 'Translation'))
        fault_lines = fault_lines.replace("$ROTATION$", "%.1f" % event_options.get('rotation', 30.0))
        fault_lines = fault_lines.replace("$AMPLITUDE$", "%.1f" % event_options.get('amplitude', 2000.0))
        fault_lines = fault_lines.replace("$RADIUS$", "%.1f" % event_options.get('radius', 1000.0))
        fault_lines = fault_lines.replace("$XAXIS$", "%.1f" % event_options.get('xaxis', 2000.0))
        fault_lines = fault_lines.replace("$YAXIS$", "%.1f" % event_options.get('yaxis', 2000.0))
        fault_lines = fault_lines.replace("$ZAXIS$", "%.1f" % event_options.get('zaxis', 2000.0))
        # $GEOMETRY$ Translation


        # now split lines and add as list entries to event lines
        # event lines are defined in list:

        # split lines and add to event lines list:
        for layer_line in fault_lines.split("\n"):
            tmp_lines.append(layer_line)

        tmp_lines_list = []
        for line in tmp_lines:
            tmp_lines_list.append(line + "\n")
        ev.set_event_lines(tmp_lines_list)
        return ev

    def _create_fold(self, event_options):
        """Create a fold event

        **Arguments**:
            - *event_options* = list : list of required and optional settings for event;
            Options are:
            'name' = string : name of fault event
            'pos' = (x,y,z) : position of reference point (floats)
                .. note::     for convenience, it is possible to assign 'top' to z
                              for position at "surface"
            'amplitude' = float : amplitude of fold
            'wavelength' = float : wavelength of fold
            'dip_dir' = float : dip (plane) direction (default: 90)
            'dip' = float : fault (plane) dip (default: 90)
        """
        ev = events.Fault()
        tmp_lines = [""]
        fault_lines = _Templates.fold
        # substitute text with according values
        fault_lines = fault_lines.replace("$NAME$", event_options['name'])
        fault_lines = fault_lines.replace("$POS_X$", "%.1f" % event_options['pos'][0])
        fault_lines = fault_lines.replace("$POS_Y$", "%.1f" % event_options['pos'][1])
        if event_options['pos'] == 'top':
            # recalculate z-value to be at top of model
            z = self.zmax
            fault_lines = fault_lines.replace("$POS_Z$", "%.1f" % z)
        else:
            fault_lines = fault_lines.replace("$POS_Z$", "%.1f" % event_options['pos'][2])
        fault_lines = fault_lines.replace("$WAVELENGTH$", "%.1f" % event_options['wavelength'])
        fault_lines = fault_lines.replace("$AMPLITUDE$", "%.1f" % event_options['amplitude'])
        # fault_lines = fault_lines.replace("$SLIP$", "%.1f" % event_options['slip'])
        fault_lines = fault_lines.replace("$DIP_DIR$", "%.1f" % event_options.get('dip_dir', 90.0))
        fault_lines = fault_lines.replace("$DIP$", "%.1f" % event_options.get('dip', 90.0))

        # now split lines and add as list entries to event lines
        # event lines are defined in list:

        # split lines and add to event lines list:
        for layer_line in fault_lines.split("\n"):
            tmp_lines.append(layer_line)

        tmp_lines_list = []
        for line in tmp_lines:
            tmp_lines_list.append(line + "\n")
        ev.set_event_lines(tmp_lines_list)
        return ev

    # AK 2014-10    
    def _create_tilt(self, event_options):
        """Create a tilt event
        
        **Arguments**:
            - *event_options* = list : list of required and optional settings for event;
            Options are:
            'name' = string : name of tilt event
            'pos' = (x,y,z) : position of reference point (floats)
                .. note::     for convenience, it is possible to assign 'top' to z
                              for position at "surface"
            'rotation' = [0,360] : dip?
            'plunge_direction' = [0,360] : strike of plunge, measured from x axis
            'plunge' = float : ?
        """
        ev = events.Tilt()
        tmp_lines = [""]
        tilt_lines = _Templates.tilt
        # substitute text with according values
        tilt_lines = tilt_lines.replace("$NAME$", event_options['name'])
        tilt_lines = tilt_lines.replace("$POS_X$", "%.1f" % event_options['pos'][0])
        tilt_lines = tilt_lines.replace("$POS_Y$", "%.1f" % event_options['pos'][1])
        if event_options['pos'] == 'top':
            # recalculate z-value to be at top of model
            z = self.zmax
            tilt_lines = tilt_lines.replace("$POS_Z$", "%.1f" % z)
        else:
            tilt_lines = tilt_lines.replace("$POS_Z$", "%.1f" % event_options['pos'][2])
        tilt_lines = tilt_lines.replace("$ROTATION$", "%.1f" % event_options['rotation'])
        tilt_lines = tilt_lines.replace("$PLUNGE_DIRECTION$", "%.1f" % event_options['plunge_direction'])
        tilt_lines = tilt_lines.replace("$PLUNGE$", "%.1f" % event_options['plunge'])

        # now split lines and add as list entries to event lines
        # event lines are defined in list:

        # split lines and add to event lines list:
        for tilt_line in tilt_lines.split("\n"):
            tmp_lines.append(tilt_line)

        tmp_lines_list = []
        for line in tmp_lines:
            tmp_lines_list.append(line + "\n")
        ev.set_event_lines(tmp_lines_list)
        return ev

    # AK 2014-10    
    def _create_unconformity(self, event_options):
        """Create a unconformity event
        
        **Arguments**:
            - *event_options* = list : list of required and optional settings for event;
            Options are:
            'name' = string : name of unconformity event
            'pos' = (x,y,z) : position of reference point (floats)
                .. note::     for convenience, it is possible to assign 'top' to z
                              for position at "surface"
            'rotation' = [0,360] : dip?
            'plunge_direction' = [0,360] : strike of plunge, measured from x axis
            'plunge' = float : ?
        """
        ev = events.Unconformity()
        tmp_lines = [""]
        unconformity_lines = _Templates.unconformity
        # substitute text with according values
        unconformity_lines = unconformity_lines.replace("$NAME$", event_options['name'])
        unconformity_lines = unconformity_lines.replace("$POS_X$", "%.1f" % event_options['pos'][0])
        unconformity_lines = unconformity_lines.replace("$POS_Y$", "%.1f" % event_options['pos'][1])
        if event_options['pos'] == 'top':
            # recalculate z-value to be at top of model
            z = self.zmax
            unconformity_lines = unconformity_lines.replace("$POS_Z$", "%.1f" % z)
        else:
            unconformity_lines = unconformity_lines.replace("$POS_Z$", "%.1f" % event_options['pos'][2])
        unconformity_lines = unconformity_lines.replace("$DIP_DIRECTION$", "%.1f" % event_options['dip_direction'])
        unconformity_lines = unconformity_lines.replace("$DIP$", "%.1f" % event_options['dip'])

        # split lines and add to event lines list:
        for unconformity_line in unconformity_lines.split("\n"):
            tmp_lines.append(unconformity_line)

        # unconformity has a stratigraphy block
        tmp_lines.append("\tNum Layers\t= %d" % event_options['num_layers'])
        for i in range(event_options['num_layers']):
            """Add stratigraphy layers"""
            layer_name = event_options['layer_names'][i]
            cum_thickness = np.cumsum(event_options['layer_thickness'])
            layer_lines = _Templates().strati_layer
            # now replace required variables
            layer_lines = layer_lines.replace("$NAME$", layer_name)
            layer_lines = layer_lines.replace("$HEIGHT$", "%.1f" % cum_thickness[i])
            layer_lines = layer_lines.replace("    ", "\t")
            # split lines and add to event lines list:
            for layer_line in layer_lines.split("\n"):
                tmp_lines.append(layer_line)

        # append event name
        tmp_lines.append("""\tName\t= %s""" % event_options.get('name', 'Unconf'))

        tmp_lines_list = []
        for line in tmp_lines:
            tmp_lines_list.append(line + "\n")
        ev.set_event_lines(tmp_lines_list)
        return ev

    def set_event_params(self, params_dict):
        """set multiple event parameters according to settings in params_dict
        
        **Arguments**:
            - *params_dict* = dictionary : entries to set (multiple) parameters
            
        """
        for key, sub_dict in list(params_dict.items()):
            for sub_key, val in list(sub_dict.items()):
                self.events[key].properties[sub_key] = val

    def change_event_params(self, changes_dict):
        """Change multiple event parameters according to settings in changes_dict
        
        **Arguments**:
            - *changes_dict* = dictionary : entries define relative changes for (multiple) parameters
            
        Per default, the values in the dictionary are added to the event parameters.
        """
        # print changes_dict
        for key, sub_dict in list(changes_dict.items()):  # loop through events (key)
            for sub_key, val in list(sub_dict.items()):  # loop through parameters being changed (sub_key)
                if isinstance(sub_key, int): # in this case, it is the layer id of a stratigraphic layer!
                    self.events[key].layers[sub_key].properties[val['property']] += val['val']
                else:
                    self.events[key].properties[sub_key] += val

    def get_event_params(self, event_number):
        '''
        Returns the parameter dictionary for a given event.
        
        **Arguments**:
         - *event_number* = the event to get a parameter for (integer)
         
         **Returns**
          - Returns the parameter dictionary for the requested event
        '''
        return self.events[event_number].properties

    def get_event_param(self, event_number, name):
        '''
        Returns the value of a given parameter for a given event.
        
        **Arguments**:
         - *event_number* = the event to get a parameter for (integer)
         - *name* = the name of the parameter to retreive (string)
         
         **Returns**
          - Returns the value of the request parameter, or None if it does not 
            exists.
        '''
        try:
            ev = self.events[event_number].properties
            return ev[name]
        except KeyError:
            return None  # property does not exist

    def write_history(self, filename):
        """Write history to new file
        
        **Arguments**:
            - *filename* = string : filename of new history file
            
        .. hint:: Just love it how easy it is to 'write history' with Noddy ;-)
        
        """
        # before saving: update all event properties (in case changes were made)
        self.update_all_event_properties()

        # first: create header
        if not hasattr(self, "filename"):
            self.filename = filename
        self._create_header()

        # initialise history lines
        history_lines = []

        # add header
        for line in self.header_lines.split("\n"):
            history_lines.append(line + "\n")

        # add number of events
        history_lines.append("No of Events\t= %d\n" % len(self.events))
        # add events
        for event_id in sorted(self.events.keys()):
            for line in self.events[event_id].event_lines:
                history_lines.append(line)

        # add footer: from original footer or from template (if new file):
        if not hasattr(self, "footer_lines"):
            self.create_footer_from_template()

        # add footer
        for line in self.footer_lines:
            history_lines.append(line)

        f = open(filename, 'w')
        for i, line in enumerate(history_lines):
            # add empty line before "BlockOptions", if not there:
            if ('BlockOptions' in line) and (history_lines[i - 1] != "\n"):
                f.write("\n")

            # write line
            f.write(line)

        f.close()


# ===============================================================================
# End of NoddyHistory
# ===============================================================================

# ===============================================================================
# Two extra PyNoddy functions for creating history files based on fault traces
# ===============================================================================

def setUpFaultRepresentation(Data, SlipParam=0.04, xy_origin=[0,0,0], 
                             RefineFault=True, RefineDistance=350,
                             interpType = 'linear'):    
    '''
    This is a function that takes a csv files with fault vertices and manipulates
    the information so it can be easily input into PyNoddy
    
     Parameters
    ----------
    Data : A pandas table with the vertices of the faults. 
    Needs to contain four columns: id,DipDirecti,X,Y.
        id: an identifier for each fault (to which fault does the vertex belong)
        DipDirecti: dip direction: East, West, SS (strike slip)
        X,Y: the x and y of the fault vertices
    SlipParam : How much does the fault slip for the fault length, optional
        The default is 0.04.
    RefineFault: Should you refine the number of points with which the fault is modeled
    RefineDistance: Every how many units should you create another fault vertex
    interpType: The type of interpolation used when refining the fault trace. 
        choose from ‘linear’, ‘nearest’, ‘zero’, ‘slinear’, ‘quadratic’, ‘cubic’, ‘previous’, ‘next’
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html
    Returns
    -------
    parametersForGeneratingFaults: a dictionary with lists of Noddy-ready fault parameters.

    '''       
    import pandas as pd
    from sklearn.decomposition import PCA
    from scipy import interpolate

    #################################
    ## 1. initialize parameters
    #################################
    
    #the x, y, z centers of the fault
    XList, YList, ZList = [], [], []

    #the x, y, trace points of the fault, and the number of points per fault trace
    PtXList,PtYList = [],[] 
    nFaultPointsList = []

    #for elliptic faults, the radii of the fault
    XAxisList, YAxisList, ZAxisList = [], [], []

    #the dip, dip direction, and slip
    DipList, DipDirectionList, SlipList = [], [], []

    # the amplitude, pitch, and profile pitch
    AmplitudeList = []
    PitchList = []      
    ProfilePitchList = []      
              
    #clean the input data such that it is relative to the point of origin of the model
    Data['X'] = Data['X']-xy_origin[0]
    Data['Y'] = Data['Y']-xy_origin[1]
    
    #Get the number of input faults
    Faults = pd.unique(Data['id'])
    nFaults = len(Faults)
    
    #################################
    ## 2. Calculate initialized parameters for each input fault
    #################################
   
    for i in range(nFaults):
        
        #select the data points for each fault one at a time
        filterV = Data['id']==Faults[i]

        #get the xy points of the fault
        xy = Data.loc[filterV, ['X', 'Y']].values
        
        #get the dip direction information (you only need one value)
        EastWest =  Data.loc[filterV, ['DipDirecti']].values[0,0]
      
        # Perform a pca on the vertices in order to get the faults aligned on 
        # a major and minor axis
        pca = PCA(2)
        pca.fit(xy) 
        if(pca.components_[0, 0]>0):
            pca.components_[0, :] = pca.components_[0, :]*-1
        if(pca.components_[1, 1]>0):
            pca.components_[1, :] = pca.components_[1, :]*-1           
        xypca = pca.transform(xy)
    
        # Calculate the dip direction
        vectorPCA1 = pca.components_[0, :]       
        vectorNorth = [0,1]   
        if(vectorPCA1[0]<0):
            vectorPCA1= vectorPCA1*-1  
        angle = np.math.atan2(np.linalg.det([vectorPCA1,vectorNorth]),np.dot(vectorPCA1,vectorNorth))
        angle = np.degrees(angle)
        dipdirection= angle+90
        if(dipdirection<0):
            dipdirection=dipdirection+360
        
        # Calculate the fault length
        lengthFault = np.max(xypca[:,0])-np.min(xypca[:,0])

        # Get the fault center x and y        
        means = pca.inverse_transform([(np.max(xypca[:,0])+np.min(xypca[:,0]))/2, (np.max(xypca[:,1])+np.min(xypca[:,1]))/2])
        meanX = means[0]
        meanY = means[1]
 
        # You need to normalize the input fault data to be between 0-628 for x
        # and between -100 to 100 in the y direction.
        targetXmin = 0
        targetXmax = 628
        targetYmin = -100
        targetYmax = 100
        newRangeX = targetXmax-targetXmin
        newRangeY = targetYmax-targetYmin
        oldRangeX = (np.max(xypca[:,0])-np.min(xypca[:,0]))
        oldRangeY = (np.max(xypca[:,1])-np.min(xypca[:,1]))
        xypca[:,0]= ((xypca[:,0]-np.min(xypca[:,0]))/oldRangeX)*newRangeX
        #If the fault is straight, it does not need be re-calibrated in the y direction
        if(oldRangeY<0.0001):
            pass
        else:
            xypca[:,1]= ((xypca[:,1]-np.min(xypca[:,1]))/oldRangeY)*newRangeY+targetYmin
          
        #The trace needs to be flipped sometimes depending on the dipping direction
        if(EastWest=='East'):
            if(dipdirection<180):
                dip = 70
            else:
                dipdirection=dipdirection-180
                xypca[:,1]=-1*xypca[:,1]
                xypca[:,0]=-1*xypca[:,0]+newRangeX
                dip = 70
            ProfilePitch=0
            Pitch=90
        elif(EastWest=='SS'):
            if(dipdirection<180):
                dip = 80
            else:
                dipdirection=dipdirection-180
                xypca[:,1]=-1*xypca[:,1]
                dip = 80
            Pitch=180
            ProfilePitch=90
        else:
            if(dipdirection>180):
                dip = 70
            else:
                dipdirection=dipdirection+180
                xypca[:,1]=-1*xypca[:,1]
                xypca[:,0]=-1*xypca[:,0]+newRangeX
                dip = 70
            ProfilePitch=0
            Pitch=90
            
        #Just to be sure, I'm re-sorting the data by x. 
        #I'm not sure this is a necessary step.
        #This can most definitely be done using numpy and not pandas
        xypcapd = pd.DataFrame({'X': xypca[:,0], 'Y': xypca[:,1]})
        xypcapd = xypcapd.sort_values(['X','Y'], ascending='True')
        xypca = xypcapd.values
        
        traceXpts = xypca[:,0]
        traceYpts = xypca[:,1]

        #Refine the fault 
        maxPointsFault=30
        minPointsFault=2
        if(RefineFault==True):
            nPointsDivide = int(np.max([np.ceil(np.min([lengthFault/RefineDistance,maxPointsFault])), minPointsFault]))           
            f = interpolate.interp1d(traceXpts.copy(), traceYpts.copy(), kind='linear')
            traceXpts=np.linspace(0, 628, nPointsDivide)
            traceYpts=f(traceXpts)

        #Add the calculated fault information to the initialized list.
        PtXList.append(traceXpts)
        PtYList.append(traceYpts)
        XList.append(meanX)
        YList.append(meanY)
        ZList.append(4000)
        XAxisList.append(lengthFault/2)
        ZAxisList.append(lengthFault/2)
        YAxisList.append(lengthFault/2)
        DipDirectionList.append(dipdirection)
        DipList.append(dip)
        SlipList.append(lengthFault*SlipParam)
        AmplitudeList.append(oldRangeY/2)
        ProfilePitchList.append(ProfilePitch)
        PitchList.append(Pitch)
        nFaultPointsList.append(len(traceXpts))
    
    #Return all of the fault information in a list structure
    parametersForGeneratingFaults={}
    parametersForGeneratingFaults['nFaults']=nFaults
    parametersForGeneratingFaults['nFaultPoints']=nFaultPointsList
    parametersForGeneratingFaults['PtX'] = PtXList
    parametersForGeneratingFaults['PtY'] = PtYList
    parametersForGeneratingFaults['X'] = XList
    parametersForGeneratingFaults['Y'] = YList
    parametersForGeneratingFaults['Z'] = ZList
    parametersForGeneratingFaults['XAxis'] = XAxisList
    parametersForGeneratingFaults['YAxis'] = YAxisList
    parametersForGeneratingFaults['ZAxis'] = ZAxisList
    parametersForGeneratingFaults['Dip'] = DipList
    parametersForGeneratingFaults['Dip Direction'] = DipDirectionList
    parametersForGeneratingFaults['Slip'] = SlipList
    parametersForGeneratingFaults['Amplitude'] = AmplitudeList
    parametersForGeneratingFaults['Profile Pitch'] = ProfilePitchList
    parametersForGeneratingFaults['Pitch'] = PitchList
    
    return parametersForGeneratingFaults 

def createPyNoddyHistoryFile(noddyFormattedFaultData, StratDict, 
                             filename = 'faultmodel.his', joinType = 'LINES',
                             cubesize=150, origin=[0,0,4000], extent=[9000,9400,4000]):
    '''
    This is a function that created a PyNoddy history file from a dictionary
    with information regarding faults and a dictionary with information regarding 
    the stratigraphy.
    
     Parameters
    ----------
    noddyFormattedFaultData: the output from setUpFaultRepresentation
    StratDict: a dictionary with information regarding the stratigraphy, the bottom layer first.
    for example:
        StratDict = {}
        StratDict['Heights'] = [2000, 2500, 3000, 3700]
        StratDict['Names'] = ['Intrusive', 'Felsic', 'Mafic','Sed'] 
        StratDict['Density'] =  [2.65, 2.5, 2.4, 2.3] 
        StratDict['MagSus'] = [0.0015, 0.0012, 0.0018, 0.001]

    filename: a name for the history file
    joinType: in Noddy, fault traces be interpolated via LINES, CURVES, SQUARE  
    cubesize: the size of the cube that will determine the resolution
    origin: the minimum x and y values of the model and the top z point of the model
    extent: the extent of the model in the x, y, and z directions
    Returns
    -------
    nothing. Just writes out the history file.
    '''
    import pynoddy
    
    nFaults = noddyFormattedFaultData['nFaults']
    nEvents = nFaults + 1
    nLayers = len(StratDict['Names'])
              
    #Open the history file and write out the top header
    file1 = open(filename,"w") 
    headerTxt = pynoddy.history._Templates().header
    file1.write(headerTxt+ '\n') 
    
    #Write out the number of events
    numEventsText = "No of Events\t= %d\n" % (nEvents)
    file1.write(numEventsText) 
    
    #Make the stratigraphy event
    #By copying a template and then replacing the key words identified by $key$
    EventTitle = 'Event #1	= STRATIGRAPHY'
    file1.write(EventTitle + '\n') 
    SubTitle = "	Num Layers = %d" % (nLayers) 
    file1.write(SubTitle + '\n') 
    for i in range(nLayers):
        stratTxt = pynoddy.history._Templates().strati_layerExpanded
        stratTxt = stratTxt.replace("$NAME$", StratDict['Names'][i])
        stratTxt = stratTxt.replace("$RED$", str(np.random.randint(0, 255)))
        stratTxt = stratTxt.replace("$GREEN$", str(np.random.randint(0, 255)))
        stratTxt = stratTxt.replace("$BLUE$", str(np.random.randint(0, 255)))
        stratTxt = stratTxt.replace("$Height$", "{:.5f}".format(StratDict['Heights'][i]))
        stratTxt = stratTxt.replace("$Density$", "{:.5f}".format(StratDict['Density'][i]))
        stratTxt = stratTxt.replace("$MagSus$", "{:.5f}".format(StratDict['MagSus'][i]))        
        file1.write(stratTxt + '\n') 
    file1.write("	Name	= Strat\n")


    #Make an event for each fault  
    FaultProperties = ['X', 'Y', 'Z', 'Dip Direction', 
                       'Dip', 'Slip', 'Amplitude', 'XAxis', 'YAxis',
                       'ZAxis','Profile Pitch', 'Pitch'] 

    for i in range(nFaults):
        nPoints= noddyFormattedFaultData['nFaultPoints'][i]
        EventTitle = 'Event #%d	= FAULT' % (i+2)  
        file1.write(EventTitle + '\n') 

        #start
        faultTxt = pynoddy.history._Templates().fault_start
        for prop in FaultProperties:
            faultTxt = faultTxt.replace("$"+prop+"$", "{:.5f}".format(noddyFormattedFaultData[prop][i]))
        faultTxt = faultTxt.replace('$Join Type$', joinType)
        file1.write(faultTxt+ '\n') 

        #middle --> add the fault trace information           
        faultPointTxt= "    Num Points    = %d" % (nPoints) 
        file1.write(faultPointTxt+ '\n')
        for p in range(nPoints):
            ptX = " 		Point X = "+"{:.5f}".format(noddyFormattedFaultData['PtX'][i][p])
            file1.write(ptX+ '\n') 
            ptY = " 		Point Y = "+"{:.5f}".format(noddyFormattedFaultData['PtY'][i][p])
            file1.write(ptY+ '\n')             

        #end            
        faultTxt = pynoddy.history._Templates().fault_end
        faultTxt = faultTxt.replace("$NAME$", 'Fault'+str(i))
        file1.write(faultTxt+ '\n') 

    #replace the origin information            
    footerTxt = pynoddy.history._Templates().footer_expanded
    footerTxt = footerTxt.replace('$origin_z$', str(origin[2]))
    footerTxt = footerTxt.replace('$extent_x$', str(extent[0]))
    footerTxt = footerTxt.replace('$extent_y$', str(extent[1]))
    footerTxt = footerTxt.replace('$extent_z$', str(extent[2]))
    footerTxt = footerTxt.replace('$cube_size$', str(cubesize))
    file1.write(footerTxt) 
    
    file1.close()


# ===============================================================================
# Templates for Noddy history file
# ===============================================================================

class _Templates():
    header = """#Filename = simple_two_faults.his
#Date Saved = 24/3/2014 14:21:0
FileType = 111
Version = 7.11"""

    strati_layer = """    Unit Name    = $NAME$
    Height    = $HEIGHT$
    Apply Alterations    = ON
    Density    = $DENSITY$
    Anisotropic Field    = 0
    MagSusX    = 1.60e-003
    MagSusY    = 1.60e-003
    MagSusZ    = 1.60e-003
    MagSus Dip    = 9.00e+001
    MagSus DipDir    = 9.00e+001
    MagSus Pitch    = 0.00e+000
    Remanent Magnetization    = 0
    Inclination    =  30.00
    Angle with the Magn. North    =  30.00
    Strength    = 1.60e-003
    Color Name    = Color 92
    Red    = 0
    Green    = 153
    Blue    = 48 """
  
    strati_layerExpanded = """    Unit Name    = $NAME$
    Height    = $Height$
    Apply Alterations    = ON
    Density    = $Density$
    Anisotropic Field    = 0
    MagSusX    = $MagSus$
    MagSusY    = $MagSus$
    MagSusZ    = $MagSus$
    MagSus Dip    = 9.00e+001
    MagSus DipDir    = 9.00e+001
    MagSus Pitch    = 0.00e+000
    Remanent Magnetization    = 0
    Inclination    =  30.00
    Angle with the Magn. North    =  30.00
    Strength    = 1.60e-003
    Color Name    = Color 92
    Red    = $RED$
    Green    = $GREEN$
    Blue    = $BLUE$ """

    fault_start = """    Geometry    = Curved
    Movement    = Hanging Wall
    X    = $X$
    Y    = $Y$
    Z    =   $Z$
    Dip Direction    =  $Dip Direction$
    Dip    =  $Dip$
    Pitch    =  $Pitch$
    Slip    = $Slip$
    Rotation    = 30
    Amplitude    = $Amplitude$
    Radius    = 1000
    XAxis    = $XAxis$
    YAxis    = $YAxis$
    ZAxis    = $ZAxis$
    Cyl Index    =   0.00
    Profile Pitch    = $Profile Pitch$
    Color Name    = Custom Colour 8
    Red    = 0
    Green    = 0
    Blue    = 254
    Fourier Series
        Term A 0    =   0.00
        Term B 0    =   0.00
        Term A 1    =   0.00
        Term B 1    =   1.00
        Term A 2    =   0.00
        Term B 2    =   0.00
        Term A 3    =   0.00
        Term B 3    =   0.00
        Term A 4    =   0.00
        Term B 4    =   0.00
        Term A 5    =   0.00
        Term B 5    =   0.00
        Term A 6    =   0.00
        Term B 6    =   0.00
        Term A 7    =   0.00
        Term B 7    =   0.00
        Term A 8    =   0.00
        Term B 8    =   0.00
        Term A 9    =   0.00
        Term B 9    =   0.00
        Term A 10    =   0.00
        Term B 10    =   0.00
    Name    = Fault Plane
    Type    = 1
    Join Type     = $Join Type$
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 6.280000
    Min Y Scale    = -1.000000
    Max Y Scale    = 1.000000
    Scale Origin    = 0.000000
    Min Y Replace    = -1.000000
    Max Y Replace    = 1.000000"""
    
    fault_end = """    Alteration Type     = NONE
    Num Profiles    = 12
    Name    = Density
    Type    = 2
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = 0.000000
    Max Y Scale    = 4.000000
    Scale Origin    = 1.000000
    Min Y Replace    = 0.000000
    Max Y Replace    = 10.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = -50
        Point X    = 628
        Point Y    = -50
    Name    = Anisotropy
    Type    = 3
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -10.000000
    Max Y Scale    = 10.000000
    Scale Origin    = 0.000000
    Min Y Replace    = -10.000000
    Max Y Replace    = 10.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = - X Axis (Sus)
    Type    = 4
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -5.000000
    Max Y Scale    = 5.000000
    Scale Origin    = 0.000000
    Min Y Replace    = 2.000000
    Max Y Replace    = 8.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = - Y Axis (Sus)
    Type    = 5
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -5.000000
    Max Y Scale    = 5.000000
    Scale Origin    = 0.000000
    Min Y Replace    = 2.000000
    Max Y Replace    = 8.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = - Z Axis (Sus)
    Type    = 6
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -5.000000
    Max Y Scale    = 5.000000
    Scale Origin    = 0.000000
    Min Y Replace    = 2.000000
    Max Y Replace    = 8.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = - Dip (Sus)
    Type    = 7
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -180.000000
    Max Y Scale    = 180.000000
    Scale Origin    = 1.000000
    Min Y Replace    = -180.000000
    Max Y Replace    = 180.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 1
        Point X    = 628
        Point Y    = 1
    Name    = - Dip Dir (Sus)
    Type    = 8
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -360.000000
    Max Y Scale    = 360.000000
    Scale Origin    = 1.000000
    Min Y Replace    = -360.000000
    Max Y Replace    = 360.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = - Pitch (Sus)
    Type    = 9
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -360.000000
    Max Y Scale    = 360.000000
    Scale Origin    = 1.000000
    Min Y Replace    = -360.000000
    Max Y Replace    = 360.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = Remanence
    Type    = 10
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -10.000000
    Max Y Scale    = 10.000000
    Scale Origin    = 0.000000
    Min Y Replace    = -10.000000
    Max Y Replace    = 10.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = - Declination (Rem)
    Type    = 11
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -360.000000
    Max Y Scale    = 360.000000
    Scale Origin    = 1.000000
    Min Y Replace    = -360.000000
    Max Y Replace    = 360.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = - Inclination (Rem)
    Type    = 12
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -360.000000
    Max Y Scale    = 360.000000
    Scale Origin    = 1.000000
    Min Y Replace    = -360.000000
    Max Y Replace    = 360.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = - Intensity (Rem)
    Type    = 13
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -5.000000
    Max Y Scale    = 5.000000
    Scale Origin    = 0.000000
    Min Y Replace    = -5.000000
    Max Y Replace    = 5.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Surface Type    = FLAT_SURFACE
    Surface Filename    =      
    Surface Directory    = \\psf\Home
    Surface XDim    = 0.000000
    Surface YDim    = 0.000000
    Surface ZDim    = 0.000000
    Name    = $NAME$"""

    fault = """    Geometry    = $GEOMETRY$
    Movement    = $MOVEMENT$
    X    = $POS_X$
    Y    = $POS_Y$
    Z    =   $POS_Z$
    Dip Direction    =  $DIP_DIR$
    Dip    =  $DIP$
    Pitch    =  90.00
    Slip    = $SLIP$
    Rotation    = $ROTATION$
    Amplitude    = $AMPLITUDE$
    Radius    = $RADIUS$
    XAxis    = $XAXIS$
    YAxis    = $YAXIS$
    ZAxis    = $ZAXIS$
    Cyl Index    =   0.00
    Profile Pitch    =  90.00
    Color Name    = Custom Colour 8
    Red    = 0
    Green    = 0
    Blue    = 254
    Fourier Series
        Term A 0    =   0.00
        Term B 0    =   0.00
        Term A 1    =   0.00
        Term B 1    =   1.00
        Term A 2    =   0.00
        Term B 2    =   0.00
        Term A 3    =   0.00
        Term B 3    =   0.00
        Term A 4    =   0.00
        Term B 4    =   0.00
        Term A 5    =   0.00
        Term B 5    =   0.00
        Term A 6    =   0.00
        Term B 6    =   0.00
        Term A 7    =   0.00
        Term B 7    =   0.00
        Term A 8    =   0.00
        Term B 8    =   0.00
        Term A 9    =   0.00
        Term B 9    =   0.00
        Term A 10    =   0.00
        Term B 10    =   0.00
    Name    = Fault Plane
    Type    = 1
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 6.280000
    Min Y Scale    = -1.000000
    Max Y Scale    = 1.000000
    Scale Origin    = 0.000000
    Min Y Replace    = -1.000000
    Max Y Replace    = 1.000000
    Num Points    = 21
        Point X    = 0
        Point Y    = 0
        Point X    = 31
        Point Y    = 30
        Point X    = 62
        Point Y    = 58
        Point X    = 94
        Point Y    = 80
        Point X    = 125
        Point Y    = 94
        Point X    = 157
        Point Y    = 99
        Point X    = 188
        Point Y    = 95
        Point X    = 219
        Point Y    = 81
        Point X    = 251
        Point Y    = 58
        Point X    = 282
        Point Y    = 31
        Point X    = 314
        Point Y    = 0
        Point X    = 345
        Point Y    = -31
        Point X    = 376
        Point Y    = -59
        Point X    = 408
        Point Y    = -81
        Point X    = 439
        Point Y    = -95
        Point X    = 471
        Point Y    = -100
        Point X    = 502
        Point Y    = -96
        Point X    = 533
        Point Y    = -82
        Point X    = 565
        Point Y    = -59
        Point X    = 596
        Point Y    = -32
        Point X    = 628
        Point Y    = -1
    Alteration Type     = NONE
    Num Profiles    = 12
    Name    = Density
    Type    = 2
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = 0.000000
    Max Y Scale    = 4.000000
    Scale Origin    = 1.000000
    Min Y Replace    = 0.000000
    Max Y Replace    = 10.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = -50
        Point X    = 628
        Point Y    = -50
    Name    = Anisotropy
    Type    = 3
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -10.000000
    Max Y Scale    = 10.000000
    Scale Origin    = 0.000000
    Min Y Replace    = -10.000000
    Max Y Replace    = 10.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = - X Axis (Sus)
    Type    = 4
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -5.000000
    Max Y Scale    = 5.000000
    Scale Origin    = 0.000000
    Min Y Replace    = 2.000000
    Max Y Replace    = 8.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = - Y Axis (Sus)
    Type    = 5
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -5.000000
    Max Y Scale    = 5.000000
    Scale Origin    = 0.000000
    Min Y Replace    = 2.000000
    Max Y Replace    = 8.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = - Z Axis (Sus)
    Type    = 6
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -5.000000
    Max Y Scale    = 5.000000
    Scale Origin    = 0.000000
    Min Y Replace    = 2.000000
    Max Y Replace    = 8.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = - Dip (Sus)
    Type    = 7
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -180.000000
    Max Y Scale    = 180.000000
    Scale Origin    = 1.000000
    Min Y Replace    = -180.000000
    Max Y Replace    = 180.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 1
        Point X    = 628
        Point Y    = 1
    Name    = - Dip Dir (Sus)
    Type    = 8
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -360.000000
    Max Y Scale    = 360.000000
    Scale Origin    = 1.000000
    Min Y Replace    = -360.000000
    Max Y Replace    = 360.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = - Pitch (Sus)
    Type    = 9
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -360.000000
    Max Y Scale    = 360.000000
    Scale Origin    = 1.000000
    Min Y Replace    = -360.000000
    Max Y Replace    = 360.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = Remanence
    Type    = 10
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -10.000000
    Max Y Scale    = 10.000000
    Scale Origin    = 0.000000
    Min Y Replace    = -10.000000
    Max Y Replace    = 10.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = - Declination (Rem)
    Type    = 11
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -360.000000
    Max Y Scale    = 360.000000
    Scale Origin    = 1.000000
    Min Y Replace    = -360.000000
    Max Y Replace    = 360.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = - Inclination (Rem)
    Type    = 12
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -360.000000
    Max Y Scale    = 360.000000
    Scale Origin    = 1.000000
    Min Y Replace    = -360.000000
    Max Y Replace    = 360.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Name    = - Intensity (Rem)
    Type    = 13
    Join Type     = LINES
    Graph Length    = 200.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = -5.000000
    Max Y Scale    = 5.000000
    Scale Origin    = 0.000000
    Min Y Replace    = -5.000000
    Max Y Replace    = 5.000000
    Num Points    = 2
        Point X    = 0
        Point Y    = 0
        Point X    = 628
        Point Y    = 0
    Surface Type    = FLAT_SURFACE
    Surface Filename    =      
    Surface Directory    = \\psf\Home
    Surface XDim    = 0.000000
    Surface YDim    = 0.000000
    Surface ZDim    = 0.000000
    Name    = $NAME$"""

    fold = """	Type	= Sine
	Single Fold	= FALSE
	X	=   $POS_X$
	Y	=   $POS_Y$
	Z	=   $POS_Z$
	Dip Direction	=  $DIP_DIR$
	Dip	=  $DIP$
	Pitch	=   0.00
	Wavelength	= $WAVELENGTH$
	Amplitude	= $AMPLITUDE$
	Cylindricity	=   0.00
	Fourier Series
		Term A 0	=   0.00
		Term B 0	=   0.00
		Term A 1	=   0.00
		Term B 1	=   1.00
		Term A 2	=   0.00
		Term B 2	=   0.00
		Term A 3	=   0.00
		Term B 3	=   0.00
		Term A 4	=   0.00
		Term B 4	=   0.00
		Term A 5	=   0.00
		Term B 5	=   0.00
		Term A 6	=   0.00
		Term B 6	=   0.00
		Term A 7	=   0.00
		Term B 7	=   0.00
		Term A 8	=   0.00
		Term B 8	=   0.00
		Term A 9	=   0.00
		Term B 9	=   0.00
		Term A 10	=   0.00
		Term B 10	=   0.00
	Name	= Fold Profile
	Type	= 1
	Join Type 	= LINES
	Graph Length	= 200.000000
	Min X	= 0.000000
	Max X	= 6.280000
	Min Y Scale	= -1.000000
	Max Y Scale	= 1.000000
	Scale Origin	= 0.000000
	Min Y Replace	= -1.000000
	Max Y Replace	= 1.000000
	Num Points	= 21
		Point X	= 0
		Point Y	= 0
		Point X	= 31
		Point Y	= 30
		Point X	= 62
		Point Y	= 58
		Point X	= 94
		Point Y	= 80
		Point X	= 125
		Point Y	= 94
		Point X	= 157
		Point Y	= 99
		Point X	= 188
		Point Y	= 95
		Point X	= 219
		Point Y	= 81
		Point X	= 251
		Point Y	= 58
		Point X	= 282
		Point Y	= 31
		Point X	= 314
		Point Y	= 0
		Point X	= 345
		Point Y	= -31
		Point X	= 376
		Point Y	= -59
		Point X	= 408
		Point Y	= -81
		Point X	= 439
		Point Y	= -95
		Point X	= 471
		Point Y	= -100
		Point X	= 502
		Point Y	= -96
		Point X	= 533
		Point Y	= -82
		Point X	= 565
		Point Y	= -59
		Point X	= 596
		Point Y	= -32
		Point X	= 628
		Point Y	= -1
	Name	= $NAME$"""

    # AK 2014-10
    tilt = """X    =   $POS_X$
    Y    =   $POS_Y$
    Z    =   $POS_Z$
    Rotation     =  $ROTATION$
    Plunge Direction     = $PLUNGE_DIRECTION$
    Plunge     =   $PLUNGE$
    Name    = $NAME$"""

    unconformity = """X    =   $POS_X$
    Y    =   $POS_Y$
    Z    = $POS_Z$
    Dip Direction    =  $DIP_DIRECTION$
    Dip    =   $DIP$
    Alteration Type     = NONE
    Num Profiles    = 1
    Name    =    
    Type    = 0
    Join Type     = LINES
    Graph Length    = 0.000000
    Min X    = 0.000000
    Max X    = 0.000000
    Min Y Scale    = 0.000000
    Max Y Scale    = 0.000000
    Scale Origin    = 0.000000
    Min Y Replace    = 0.000000
    Max Y Replace    = 0.000000
    Num Points    = 0
    Surface Type    = FLAT_SURFACE
    Surface Filename    =       
    Surface Directory    = /tmp_mnt/sci6/users/mark/Atlas/case
    Surface XDim    = 0.000000
    Surface YDim    = 0.000000
    Surface ZDim    = 0.000000"""
    temp = """
    Num Layers    = 5
    Unit Name    = UC Base
    Height    = -32000
    Apply Alterations    = ON
    Density    = 3.50e+00
    Anisotropic Field    = 0
    MagSusX    = 1.50e-06
    MagSusY    = 1.60e-03
    MagSusZ    = 1.60e-03
    MagSus Dip    = 9.00e+01
    MagSus DipDir    = 9.00e+01
    MagSus Pitch    = 0.00e+00
    Remanent Magnetization    = 0
    Inclination    =  30.00
    Angle with the Magn. North    =  30.00
    Strength    = 1.60e-03
    Color Name    = Color 98
    Red    = 84
    Green    = 153
    Blue    = 0
    Unit Name    = UC Layer 1
    Height    = 5650
    Apply Alterations    = ON
    Density    = 3.50e+00
    Anisotropic Field    = 0
    MagSusX    = 1.50e-06
    MagSusY    = 1.60e-03
    MagSusZ    = 1.60e-03
    MagSus Dip    = 9.00e+01
    MagSus DipDir    = 9.00e+01
    MagSus Pitch    = 0.00e+00
    Remanent Magnetization    = 0
    Inclination    =  30.00
    Angle with the Magn. North    =  30.00
    Strength    = 1.60e-03
    Color Name    = Color 68
    Red    = 204
    Green    = 117
    Blue    = 0
    Name    = $NAME$"""

    footer_expanded = """
#BlockOptions
    Number of Views    = 1
    Current View    = 0
    NAME    = Default
    Origin X    =   0.00
    Origin Y    =   0.00
    Origin Z    = $origin_z$
    Length X    = $extent_x$
    Length Y    = $extent_y$
    Length Z    = $extent_z$
    Geology Cube Size    =  $cube_size$
    Geophysics Cube Size    = $cube_size$

#GeologyOptions
    Scale    =  10.00
    SectionDec    =  90.00
    WellDepth    = 5000.00
    WellAngleZ    =   0.00
    BoreholeX    =   0.00
    BoreholeX    =   0.00
    BoreholeX    = 5000.00
    BoreholeDecl    =  90.00
    BoreholeDip    =   0.00
    BoreholeLength    = 5000.00
    SectionX    =   0.00
    SectionY    =   0.00
    SectionZ    = 5000.00
    SectionDecl    =  90.00
    SectionLength    = 10000.00
    SectionHeight    = 5000.00
    topofile    = FALSE
    Topo Filename    =    
    Topo Directory    = .
    Topo Scale    =   1.00
    Topo Offset    =   0.00
    Topo First Contour    = 100.00
    Topo Contour Interval    = 100.00
    Chair Diagram    = FALSE
    Chair_X    = 5000.00
    Chair_Y    = 3500.00
    Chair_Z    = 2500.00

#GeophysicsOptions
    GPSRange     = 1200
    Declination    =   0.00
    Inclination    = -67.00
    Intensity    = 63000.00
    Field Type    = FIXED
    Field xPos    =   0.00
    Field yPos    =   0.00
    Field zPos    = 5000.00
    Inclination Ori    =   0.00
    Inclination Change    =   0.00
    Intensity Ori    =  90.00
    Intensity Change    =   0.00
    Declination Ori    =   0.00
    Declination Change    =   0.00
    Altitude    =  80.00
    Airborne=     TRUE
    Calculation Method    = SPATIAL
    Spectral Padding Type    = RECLECTION_PADDING
    Spectral Fence    = 100
    Spectral Percent    = 100
    Constant Boxing Depth    =   0.00
    Clever Boxing Ratio    =   1.00
    Deformable Remanence=     FALSE
    Deformable Anisotropy=     TRUE
    Vector Components=     FALSE
    Project Vectors=     TRUE
    Pad With Real Geology=     FALSE
    Draped Survey=     FALSE

#3DOptions
    Declination    = 150.000000
    Elevation    = 30.000000
    Scale    = 1.000000
    Offset X    = 1.000000
    Offset Y    = 1.000000
    Offset Z    = 1.000000
    Fill Type    = 2

#ProjectOptions
    Susceptibility Units    = CGS
    Geophysical Calculation    = 2
    Calculation Type    = LOCAL_JOB
    Length Scale    = 0
    Printing Scale    = 1.000000
    Image Scale    = 10.000000
    New Windows    = FALSE
    Background Red Component    = 254
    Background Green Component    = 254
    Background Blue Component    = 254
    Internet Address    = 255.255.255.255
    Account Name    =       
    Noddy Path    = ./noddy
    Help Path    = iexplore %h
    Movie Frames Per Event    = 3
    Movie Play Speed    =  10.00
    Movie Type    = 0
    Gravity Clipping Type    = RELATIVE_CLIPPING
    Gravity Image Display Clip Min    = 0.000000
    Gravity Image Display Clip Max    = 100.000000
    Gravity Image Display Type    = GREY
    Gravity Image Display Num Contour    = 25
    Magnetics Clipping Type    = RELATIVE_CLIPPING
    Magnetics Image Display Clip Min    = 0.000000
    Magnetics Image Display Clip Max    = 100.000000
    Magnetics Image Display Type    = GREY
    Magnetics Image Display Num Contour    = 25
    False Easting    = 0.000000
    False Northing    = 0.000000

#Window Positions
    Num Windows    = 16
    Name    = Block Diagram
    X    = 60
    Y    = 60
    Width    = 500
    Height    = 300
    Name    = Movie
    X    = 60
    Y    = 60
    Width    = -1
    Height    = -1
    Name    = Well Log
    X    = 60
    Y    = 60
    Width    = 400
    Height    = 430
    Name    = Section
    X    = 14
    Y    = 16
    Width    = 490
    Height    = -1
    Name    = Topography Map
    X    = 60
    Y    = 60
    Width    = 490
    Height    = 375
    Name    = 3D Topography Map
    X    = 60
    Y    = 60
    Width    = 490
    Height    = 375
    Name    = 3D Stratigraphy
    X    = 60
    Y    = 60
    Width    = 490
    Height    = 375
    Name    = Line Map
    X    = 60
    Y    = 60
    Width    = 490
    Height    = -1
    Name    = Profile - From Image
    X    = 60
    Y    = 60
    Width    = 490
    Height    = 600
    Name    = Sterographic Projections
    X    = 60
    Y    = 60
    Width    = 430
    Height    = 430
    Name    = Stratigraphic Column
    X    = 60
    Y    = 60
    Width    = 230
    Height    = 400
    Name    = Image
    X    = 30
    Y    = 30
    Width    = -1
    Height    = -1
    Name    = Contour
    X    = 30
    Y    = 30
    Width    = -1
    Height    = -1
    Name    = Toolbar
    X    = 10
    Y    = 0
    Width    = -1
    Height    = -1
    Name    = History
    X    = 229
    Y    = 160
    Width    = 762
    Height    = 898
    Name    = History
    X    = 229
    Y    = 160
    Width    = 762
    Height    = 898

#Icon Positions
    Num Icons    = 3
    Row    = 1
    Column    = 1
    X Position    = 1
    Y Position    = 1
    Row    = 1
    Column    = 2
    X Position    = 4
    Y Position    = 1
    Row    = 1
    Column    = 3
    X Position    = 7
    Y Position    = 1
    Floating Menu Rows    = 1
    Floating Menu Cols    = 24
End of Status Report"""


    # everything below events
    footer = """
#BlockOptions
    Number of Views    = 1
    Current View    = 0
    NAME    = Default
    Origin X    =   0.00
    Origin Y    =   0.00
    Origin Z    = 5000.00
    Length X    = 10000.00
    Length Y    = 7000.00
    Length Z    = 5000.00
    Geology Cube Size    =  50.00
    Geophysics Cube Size    = 50.00

#GeologyOptions
    Scale    =  10.00
    SectionDec    =  90.00
    WellDepth    = 5000.00
    WellAngleZ    =   0.00
    BoreholeX    =   0.00
    BoreholeX    =   0.00
    BoreholeX    = 5000.00
    BoreholeDecl    =  90.00
    BoreholeDip    =   0.00
    BoreholeLength    = 5000.00
    SectionX    =   0.00
    SectionY    =   0.00
    SectionZ    = 5000.00
    SectionDecl    =  90.00
    SectionLength    = 10000.00
    SectionHeight    = 5000.00
    topofile    = FALSE
    Topo Filename    =    
    Topo Directory    = .
    Topo Scale    =   1.00
    Topo Offset    =   0.00
    Topo First Contour    = 100.00
    Topo Contour Interval    = 100.00
    Chair Diagram    = FALSE
    Chair_X    = 5000.00
    Chair_Y    = 3500.00
    Chair_Z    = 2500.00

#GeophysicsOptions
    GPSRange     = 0
    Declination    =   0.00
    Inclination    = -67.00
    Intensity    = 63000.00
    Field Type    = FIXED
    Field xPos    =   0.00
    Field yPos    =   0.00
    Field zPos    = 5000.00
    Inclination Ori    =   0.00
    Inclination Change    =   0.00
    Intensity Ori    =  90.00
    Intensity Change    =   0.00
    Declination Ori    =   0.00
    Declination Change    =   0.00
    Altitude    =  80.00
    Airborne=     FALSE
    Calculation Method    = SPATIAL
    Spectral Padding Type    = RECLECTION_PADDING
    Spectral Fence    = 100
    Spectral Percent    = 100
    Constant Boxing Depth    =   0.00
    Clever Boxing Ratio    =   1.00
    Deformable Remanence=     FALSE
    Deformable Anisotropy=     TRUE
    Vector Components=     FALSE
    Project Vectors=     TRUE
    Pad With Real Geology=     FALSE
    Draped Survey=     FALSE

#3DOptions
    Declination    = 150.000000
    Elevation    = 30.000000
    Scale    = 1.000000
    Offset X    = 1.000000
    Offset Y    = 1.000000
    Offset Z    = 1.000000
    Fill Type    = 2

#ProjectOptions
    Susceptibility Units    = CGS
    Geophysical Calculation    = 2
    Calculation Type    = LOCAL_JOB
    Length Scale    = 0
    Printing Scale    = 1.000000
    Image Scale    = 10.000000
    New Windows    = FALSE
    Background Red Component    = 254
    Background Green Component    = 254
    Background Blue Component    = 254
    Internet Address    = 255.255.255.255
    Account Name    =       
    Noddy Path    = ./noddy
    Help Path    = iexplore %h
    Movie Frames Per Event    = 3
    Movie Play Speed    =  10.00
    Movie Type    = 0
    Gravity Clipping Type    = RELATIVE_CLIPPING
    Gravity Image Display Clip Min    = 0.000000
    Gravity Image Display Clip Max    = 100.000000
    Gravity Image Display Type    = GREY
    Gravity Image Display Num Contour    = 25
    Magnetics Clipping Type    = RELATIVE_CLIPPING
    Magnetics Image Display Clip Min    = 0.000000
    Magnetics Image Display Clip Max    = 100.000000
    Magnetics Image Display Type    = GREY
    Magnetics Image Display Num Contour    = 25
    False Easting    = 0.000000
    False Northing    = 0.000000

#Window Positions
    Num Windows    = 16
    Name    = Block Diagram
    X    = 60
    Y    = 60
    Width    = 500
    Height    = 300
    Name    = Movie
    X    = 60
    Y    = 60
    Width    = -1
    Height    = -1
    Name    = Well Log
    X    = 60
    Y    = 60
    Width    = 400
    Height    = 430
    Name    = Section
    X    = 14
    Y    = 16
    Width    = 490
    Height    = -1
    Name    = Topography Map
    X    = 60
    Y    = 60
    Width    = 490
    Height    = 375
    Name    = 3D Topography Map
    X    = 60
    Y    = 60
    Width    = 490
    Height    = 375
    Name    = 3D Stratigraphy
    X    = 60
    Y    = 60
    Width    = 490
    Height    = 375
    Name    = Line Map
    X    = 60
    Y    = 60
    Width    = 490
    Height    = -1
    Name    = Profile - From Image
    X    = 60
    Y    = 60
    Width    = 490
    Height    = 600
    Name    = Sterographic Projections
    X    = 60
    Y    = 60
    Width    = 430
    Height    = 430
    Name    = Stratigraphic Column
    X    = 60
    Y    = 60
    Width    = 230
    Height    = 400
    Name    = Image
    X    = 30
    Y    = 30
    Width    = -1
    Height    = -1
    Name    = Contour
    X    = 30
    Y    = 30
    Width    = -1
    Height    = -1
    Name    = Toolbar
    X    = 10
    Y    = 0
    Width    = -1
    Height    = -1
    Name    = History
    X    = 229
    Y    = 160
    Width    = 762
    Height    = 898
    Name    = History
    X    = 229
    Y    = 160
    Width    = 762
    Height    = 898

#Icon Positions
    Num Icons    = 3
    Row    = 1
    Column    = 1
    X Position    = 1
    Y Position    = 1
    Row    = 1
    Column    = 2
    X Position    = 4
    Y Position    = 1
    Row    = 1
    Column    = 3
    X Position    = 7
    Y Position    = 1
    Floating Menu Rows    = 1
    Floating Menu Cols    = 24
End of Status Report"""


if __name__ == '__main__':
    # some testing and debugging:
    import os

    os.chdir(r'C:\Users\Sam\OneDrive\Documents\Masters\Models\Mt Painter')
    H1 = NoddyHistory("mt_pa_simplified.his")
    H1.swap_events(2, 3)
    H1.write_history("test")
    H2 = NoddyHistory("test")
    H2.events[10].properties['Radius'] = 2000
    H2.write_history("test2")
