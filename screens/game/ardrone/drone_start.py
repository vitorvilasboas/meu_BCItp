# DEPENDENCIES ------------------------
# Generic:
import math

# Project's:
from SampleManager import SampleManager
from approach import Approach
from standards import PATH_TO_SESSION

# KIVY modules:
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.clock import Clock
from kivy.lang import Builder

# KV file:
Builder.load_file('screens/game/ardrone/drone_start.kv')

######################################################################


class DroneStart(Screen):

    inst_prob_left = NumericProperty(0)
    accum_prob_left = NumericProperty(0)
    accum_color_left = ListProperty([1, 0, 0, 1])

    inst_prob_right = NumericProperty(0)
    accum_prob_right = NumericProperty(0)
    accum_color_right = ListProperty([0, 0, 1, 1])

    label_on_toggle_button = StringProperty('Start')

    current_label = NumericProperty(None)

    label_color = ListProperty([0, 0, 0, 1])

    wt = NumericProperty(0.0)

    def __init__(self, session_header, **kwargs):
        super(DroneStart, self).__init__(**kwargs)
        self.sh = session_header

        self.stream_flag = False

        self.U = 0.0
        self.p = [0, 0]

    # BUTTON CALLBACKS
    # ----------------------
    def change_to_drone(self, *args):

        self.manager.current = 'DroneMenu'
        self.manager.transition.direction = 'right'

    def toogle_stream(self, *args):
        if self.stream_flag:
            self.stream_stop()
        else:
            self.stream_start()

    # ----------------------

    def start_drone(self):
        # Hardware:
        from ardrone_ros import ARDrone
        self.drone = ARDrone()

    def stream_stop(self):
        self.sm.stop_flag = True
        self.stream_flag = False
        self.sm.join()
        self.label_on_toggle_button = 'Start'
        self.clock_unscheduler()
        self.set_bar_default()
        self.drone.set_cmd(0, 0)
        self.drone.land()
        self.drone.reset()

    def stream_start(self):
        self.load_approach()

        self.sm = SampleManager(self.sh.acq.com_port,
                                self.sh.dp.buf_len, daisy=self.sh.acq.daisy,
                                mode=self.sh.acq.mode,
                                path=self.sh.acq.path_to_file,
                                labels_path=self.sh.acq.path_to_labels_file,
                                dummy=self.sh.acq.dummy)

        self.sm.daemon = True
        self.sm.stop_flag = False
        self.sm.start()
        self.label_on_toggle_button = 'Stop'
        self.stream_flag = True
        self.clock_scheduler()
        self.drone.takeoff()
        self.drone.set_cmd(1, 0)

    def clock_scheduler(self):
        Clock.schedule_interval(self.get_probs, 1. / 20.)
        Clock.schedule_interval(self.update_accum_bars,
                                self.sh.game.window_overlap)

        if self.sh.acq.mode == 'simu' and not self.sh.acq.dummy:
            Clock.schedule_interval(self.update_current_label, 1. / 20.)

    def clock_unscheduler(self):
        Clock.unschedule(self.get_probs)
        Clock.unschedule(self.update_current_label)
        Clock.unschedule(self.update_accum_bars)

    def get_probs(self, dt):

        t, buf = self.sm.GetBuffData()

        if buf.shape[0] == self.sh.dp.buf_len:

            self.p = self.ap.applyModelOnEpoch(buf.T, 'prob')[0]

            if self.sh.game.inst_prob:
                self.update_inst_bars()

    def update_inst_bars(self):

        if self.p is None:
            return

        p1 = self.p[0]
        p2 = self.p[1]

        u = p1 - p2

        if u > 0:
            self.inst_prob_left = int(math.floor(u * 100))
            self.inst_prob_right = 0
        else:
            self.inst_prob_right = int(math.floor(abs(u) * 100))
            self.inst_prob_left = 0

    def update_accum_bars(self, dt):

        if self.p is None:
            return

        p1 = self.p[0]
        p2 = self.p[1]

        u = p1 - p2

        self.U += u

        U1 = 100 * (self.U + self.sh.game.game_threshold) / \
            (2. * self.sh.game.game_threshold)

        U2 = 100 - U1

        U1_n = int(math.floor(U1))
        U2_n = int(math.floor(U2))

        if U1_n > self.sh.game.warning_threshold:
            self.accum_color_left = [1, 1, 0, 1]
        elif U2_n > self.sh.game.warning_threshold:
            self.accum_color_right = [1, 1, 0, 1]
        else:
            self.accum_color_left = [1, 0, 0, 1]
            self.accum_color_right = [0, 0, 1, 1]

        if U1_n in range(101):
            self.accum_prob_left = U1_n
        if U2_n in range(101):
            self.accum_prob_right = U2_n

        self.map_probs(U1, U2)

    def map_probs(self, U1, U2):

        if U1 > 100:
            self.drone.set_cmd(0, 1)
            Clock.schedule_once(self.move_drone_forward, 2)
            self.set_bar_default()
        elif U2 > 100:
            self.drone.set_cmd(0, -1)
            Clock.schedule_once(self.move_drone_forward, 2)
            self.set_bar_default()
        else:
            pass
            # dont send any cmd

    def move_drone_forward(self, dt):
        self.drone.set_cmd(1, 0)

    def set_bar_default(self):

        self.accum_prob_left = 0
        self.accum_prob_right = 0

        self.inst_prob_left = 0
        self.inst_prob_right = 0

        self.U = 0.0

    def update_current_label(self, dt):

        current_label = int(self.sm.current_playback_label[1])
        self.current_label = current_label

    def load_approach(self):

        self.ap = Approach()
        self.ap.loadFromPkl(PATH_TO_SESSION + self.sh.info.name)