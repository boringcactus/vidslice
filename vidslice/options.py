import typing
from tkinter import *
from tkinter import ttk

HEADERS_ROW = 0
START_ROW = 1
END_ROW = 2
DURATION_ROW = 3
WIDTH_ROW = 4
HEIGHT_ROW = 5
FRAMERATE_ROW = 6
CROP_TOP_ROW = 7
CROP_BOTTOM_ROW = 8
CROP_LEFT_ROW = 9
CROP_RIGHT_ROW = 10
LABEL_COL = 0
ORIG_COL = 1
EDIT_BOX_COL = 2
NEW_COL = 3


class FFmpegOptions:
    def __init__(self, input, output, vf):
        self.input = input
        self.output = output
        self.vf = vf

    def output_with_vf(self):
        if len(self.vf) > 0:
            return self.output + ['-vf', ','.join(self.vf)]
        else:
            return self.output


class Property:
    def __init__(self, parent, name, row, convert: typing.Callable = int):
        self.handlers = []
        ttk.Label(parent, text=name).grid(column=LABEL_COL, row=row, sticky=(E, W))
        self.orig = StringVar(parent, value="N/A")
        ttk.Label(parent, textvariable=self.orig).grid(column=ORIG_COL, row=row, sticky=(E, W))
        self.edit = BooleanVar(parent)
        self.edit_widget = ttk.Checkbutton(parent, variable=self.edit, command=self.handle_edit)
        self.edit_widget.grid(column=EDIT_BOX_COL, row=row, sticky=(E, W))
        self.new = ttk.Spinbox(parent, command=self.handle_change)
        self.new.state(['disabled'])
        self.new.grid(column=NEW_COL, row=row, sticky=(E, W))
        self.convert = convert
        self.disable()

    def disable(self):
        self.enable(False)

    def enable(self, enabled=True):
        if enabled:
            self.edit_widget.state(['!disabled'])
        else:
            self.edit.set(False)
            self.edit_widget.state(['disabled'])
            self.new.state(['disabled'])

    def is_enabled(self):
        return self.edit_widget.instate(['!disabled'])

    def is_edit(self):
        return self.edit.get()

    def set_orig(self, val):
        self.orig.set(str(val))

    def get_orig(self):
        return self.orig.get()

    def set_calc_new(self, val):
        if not self.is_edit():
            if self.convert(self.new['from']) > val:
                self.new.configure(from_=val)
            if self.convert(self.new['to']) < val:
                self.new.configure(to=val)
            self.new.set(val)

    def set_range(self, min, max):
        self.new.configure(from_=min, to=max)

    def get_final(self):
        if len(self.new.get()) == 0:
            return self.orig.get()
        return self.new.get()

    def handle_edit(self, *args):
        if self.edit.get():
            self.new.state(['!disabled'])
        else:
            self.new.state(['disabled'])
        self.handle_change(None)

    def on_change(self, callback):
        self.handlers.append(callback)

    def handle_change(self, *args):
        for handler in self.handlers:
            handler()


class OptionsPanel(ttk.LabelFrame):
    """
    A Panel displaying ffmpeg options
    """

    def __init__(self, *args, **kw):
        super(OptionsPanel, self).__init__(*args, text="Options", **kw)

        def place_header(text, **kwargs):
            ttk.Label(self, text=text, font='TkHeadingFont', justify='center', anchor='center'
                      ).grid(sticky=(E, W), **kwargs)

        place_header("Field", column=LABEL_COL, row=HEADERS_ROW)
        place_header("Original Value", column=ORIG_COL, row=HEADERS_ROW)
        place_header("Edit?", column=EDIT_BOX_COL, row=HEADERS_ROW)
        place_header("New Value", column=NEW_COL, row=HEADERS_ROW)

        self.start_time = Property(self, "Start time (seconds)", START_ROW, float)
        self.start_time.on_change(self.enforce_constraints)

        self.end_time = Property(self, "End time (seconds)", END_ROW, float)
        self.end_time.on_change(self.enforce_constraints)

        self.duration = Property(self, "Duration (seconds)", DURATION_ROW, float)
        self.duration.on_change(self.enforce_constraints)

        self.width = Property(self, "Width", WIDTH_ROW, int)
        self.width.on_change(self.enforce_constraints)

        self.height = Property(self, "Height", HEIGHT_ROW, int)
        self.height.on_change(self.enforce_constraints)

        self.framerate = Property(self, "Framerate", FRAMERATE_ROW, float)
        self.framerate.on_change(self.enforce_constraints)

        self.crop_top = Property(self, "Crop Top", CROP_TOP_ROW, int)
        self.crop_top.on_change(self.enforce_constraints)

        self.crop_bottom = Property(self, "Crop Bottom", CROP_BOTTOM_ROW, int)
        self.crop_bottom.on_change(self.enforce_constraints)

        self.crop_left = Property(self, "Crop Left", CROP_LEFT_ROW, int)
        self.crop_left.on_change(self.enforce_constraints)

        self.crop_right = Property(self, "Crop Right", CROP_RIGHT_ROW, int)
        self.crop_right.on_change(self.enforce_constraints)

        for child in self.winfo_children():
            child.grid_configure(padx=2, pady=2)

        self.state(['disabled'])

    def enforce_constraints(self):
        self.start_time.enable()
        self.end_time.enable()
        self.duration.enable()
        orig_start = float(self.start_time.get_orig())
        orig_end = float(self.end_time.get_orig())
        orig_duration = float(self.duration.get_orig())
        if self.start_time.is_edit() and self.end_time.is_edit():
            new_start = float(self.start_time.get_final())
            new_end = float(self.end_time.get_final())
            new_duration = new_end - new_start
            self.start_time.set_range(orig_start, new_end)
            self.end_time.set_range(new_start, orig_end)
            self.duration.disable()
            self.duration.set_calc_new(new_duration)
        elif self.start_time.is_edit() and self.duration.is_edit():
            new_start = float(self.start_time.get_final())
            new_duration = float(self.duration.get_final())
            new_end = new_start + new_duration
            self.start_time.set_range(orig_start, orig_end - new_duration)
            self.duration.set_range(0, orig_end - new_start)
            self.end_time.disable()
            self.end_time.set_calc_new(new_end)
        elif self.end_time.is_edit() and self.duration.is_edit():
            new_end = float(self.end_time.get_final())
            new_duration = float(self.duration.get_final())
            new_start = new_end - new_duration
            self.end_time.set_range(orig_start + new_duration, orig_end)
            self.duration.set_range(0, new_end - orig_start)
            self.start_time.disable()
            self.start_time.set_calc_new(new_start)
        else:
            new_start = float(self.start_time.get_final())
            new_end = float(self.end_time.get_final())
            new_duration = new_end - new_start
            if self.duration.is_edit():
                new_duration = float(self.duration.get_final())
                new_end = new_start + new_duration
            self.start_time.set_range(orig_start, orig_end)
            self.end_time.set_range(orig_start, orig_end)
            self.duration.set_range(0, orig_duration)
            self.start_time.set_calc_new(new_start)
            self.end_time.set_calc_new(new_end)
            self.duration.set_calc_new(new_duration)

        if self.width.is_enabled() and self.height.is_enabled():
            orig_width = int(self.width.get_orig())
            orig_height = int(self.height.get_orig())
            new_width = int(self.width.get_final())
            new_height = int(self.height.get_final())
            self.width.set_range(1, 10 * orig_width)
            self.height.set_range(1, 10 * orig_height)

            self.width.set_calc_new(round(orig_width / orig_height * new_height))
            self.height.set_calc_new(round(orig_height / orig_width * new_width))

            self.crop_top.set_calc_new(0)
            self.crop_top.set_range(0, int(self.height.get_final()) - int(self.crop_bottom.get_final()))
            self.crop_bottom.set_calc_new(0)
            self.crop_bottom.set_range(0, int(self.height.get_final()) - int(self.crop_top.get_final()))

            self.crop_right.set_calc_new(0)
            self.crop_right.set_range(0, int(self.width.get_final()) - int(self.crop_left.get_final()))
            self.crop_left.set_calc_new(0)
            self.crop_left.set_range(0, int(self.width.get_final()) - int(self.crop_right.get_final()))

        if self.framerate.is_enabled():
            orig_framerate = float(self.framerate.get_orig())
            self.framerate.set_range(0, orig_framerate)
            self.framerate.set_calc_new(orig_framerate)

    def update_info(self, info):
        import fractions

        if info is None:
            self.state(['disabled'])
            for prop in [self.start_time, self.duration, self.end_time, self.width, self.height, self.framerate]:
                prop.disable()
        else:
            start_time = float(info['format']['start_time'])
            self.start_time.set_orig(start_time)

            duration = float(info['format']['duration'])
            self.duration.set_orig(duration)

            self.end_time.set_orig(start_time + duration)

            video_streams = [stream for stream in info['streams'] if
                             stream['codec_type'] == 'video' and stream['avg_frame_rate'] != '0/0']
            if len(video_streams) > 0:
                video_stream = video_streams[0]
                self.width.enable()
                self.width.set_orig(video_stream['width'])
                self.height.enable()
                self.height.set_orig(video_stream['height'])
                self.crop_top.enable()
                self.crop_top.set_orig(0)
                self.crop_bottom.enable()
                self.crop_bottom.set_orig(0)
                self.crop_left.enable()
                self.crop_left.set_orig(0)
                self.crop_right.enable()
                self.crop_right.set_orig(0)

                framerate = round(float(fractions.Fraction(video_stream['avg_frame_rate'])), 3)
                self.framerate.enable()
                self.framerate.set_orig(framerate)
            else:
                self.width.disable()
                self.height.disable()
                self.framerate.disable()
                self.crop_top.disable()
                self.crop_bottom.disable()
                self.crop_left.disable()
                self.crop_right.disable()

            self.state(['!disabled'])
            self.enforce_constraints()

    def ffmpeg_opts(self):
        input_opts = []
        output_opts = []
        vf = []

        if self.start_time.is_edit():
            input_opts += ['-ss', str(self.start_time.get_final())]
        elif self.end_time.is_edit() and self.duration.is_edit():
            new_end = float(self.end_time.get_final())
            new_duration = float(self.duration.get_final())
            new_start = new_end - new_duration
            input_opts += ['-ss', str(new_start)]
        if self.end_time.is_edit():
            input_opts += ['-to', str(self.end_time.get_final())]
        if self.duration.is_edit():
            output_opts += ['-t', str(self.duration.get_final())]

        if self.width.is_edit() or self.height.is_edit():
            width = str(self.width.get_final())
            height = str(self.height.get_final())
            if not self.width.is_edit():
                width = "-1"
            if not self.height.is_edit():
                height = "-1"
            vf += ['scale=' + width + ':' + height]

        if self.crop_top.is_edit() or self.crop_bottom.is_edit() or \
                self.crop_left.is_edit() or self.crop_right.is_edit():
            out_w = int(self.width.get_final()) - int(self.crop_left.get_final()) - int(self.crop_right.get_final())
            out_h = int(self.height.get_final()) - int(self.crop_top.get_final()) - int(self.crop_bottom.get_final())
            vf += [f'crop={out_w}:{out_h}:{self.crop_left.get_final()}:{self.crop_top.get_final()}']

        if self.framerate.is_edit():
            output_opts += ['-r', str(self.framerate.get_final())]

        return FFmpegOptions(input_opts, output_opts, vf)

    def frame_count(self):
        return float(self.duration.get_final()) * float(self.framerate.get_final())
