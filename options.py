import wx

HEADERS_ROW = 0
START_ROW = 1
END_ROW = 2
DURATION_ROW = 3
WIDTH_ROW = 4
HEIGHT_ROW = 5
FRAMERATE_ROW = 6
LABEL_COL = 0
ORIG_COL = 1
EDIT_BOX_COL = 2
NEW_COL = 3


class Property:
    def __init__(self, parent, name, *, label=None, orig=None, edit=None, new_class=None, new=None):
        self.handlers = []
        if label is None:
            label = wx.StaticText(parent, label=name)
        self.label = label
        if orig is None:
            orig = wx.StaticText(parent, label="N/A")
        self.orig = orig
        if edit is None:
            edit = wx.CheckBox(parent)
            edit.Bind(wx.EVT_CHECKBOX, self.handle_edit)
        self.edit = edit
        if new is None:
            if new_class is None:
                new_class = wx.TextCtrl
            new = new_class(parent)
            new.Bind(wx.EVT_SPINCTRLDOUBLE, self.handle_change)
            new.Bind(wx.EVT_SPINCTRL, self.handle_change)
            new.Disable()
        self.new = new

    def add_to(self, sizer, row):
        sizer.Add(self.label, wx.GBPosition(row, LABEL_COL))
        sizer.Add(self.orig, wx.GBPosition(row, ORIG_COL))
        sizer.Add(self.edit, wx.GBPosition(row, EDIT_BOX_COL))
        sizer.Add(self.new, wx.GBPosition(row, NEW_COL), flag=wx.EXPAND)

    def disable(self):
        self.enable(False)

    def enable(self, enabled=True):
        if enabled:
            self.edit.Enable()
        else:
            self.edit.SetValue(False)
            self.edit.Disable()
            self.new.Disable()

    def is_enabled(self):
        return self.edit.Enabled

    def is_edit(self):
        return self.edit.GetValue()

    def set_orig(self, val):
        self.orig.SetLabel(str(val))

    def get_orig(self):
        return self.orig.GetLabel()

    def set_calc_new(self, val):
        if not self.is_edit():
            if self.new.GetMin() > val:
                self.new.SetMin(val)
            if self.new.GetMax() < val:
                self.new.SetMax(val)
            self.new.SetValue(val)

    def set_range(self, min, max):
        self.new.SetRange(min, max)

    def get_final(self):
        if self.edit.GetValue():
            return self.new.GetValue()
        else:
            return self.orig.GetLabel()

    def handle_edit(self, _event):
        self.new.Enable(self.edit.GetValue())
        self.handle_change(None)

    def on_change(self, callback):
        self.handlers.append(callback)

    def handle_change(self, _event):
        for handler in self.handlers:
            handler()


class OptionsPanel(wx.Panel):
    """
    A Panel displaying ffmpeg options
    """

    def __init__(self, *args, **kw):
        super(OptionsPanel, self).__init__(*args, **kw)

        root_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, label="Options")
        self.SetSizer(root_sizer)
        main = wx.Panel(self)
        root_sizer.Add(main, proportion=1, flag=wx.EXPAND, border=5)
        main_sizer = wx.GridBagSizer(5, 5)
        main.SetSizer(main_sizer)

        def make_header(text):
            st = wx.StaticText(main, label=text, style=wx.ALIGN_CENTER_HORIZONTAL)
            st.SetFont(st.GetFont().Bold())
            return st

        main_sizer.Add(make_header("Field"), wx.GBPosition(HEADERS_ROW, LABEL_COL), flag=wx.EXPAND)
        main_sizer.Add(make_header("Original Value"), wx.GBPosition(HEADERS_ROW, ORIG_COL), flag=wx.EXPAND)
        main_sizer.Add(make_header("Edit?"), wx.GBPosition(HEADERS_ROW, EDIT_BOX_COL), flag=wx.EXPAND)
        main_sizer.Add(make_header("New Value"), wx.GBPosition(HEADERS_ROW, NEW_COL), flag=wx.EXPAND)

        self.start_time = Property(main, "Start time (seconds)", new_class=wx.SpinCtrlDouble)
        self.start_time.add_to(main_sizer, START_ROW)
        self.start_time.on_change(self.enforce_constraints)

        self.end_time = Property(main, "End time (seconds)", new_class=wx.SpinCtrlDouble)
        self.end_time.add_to(main_sizer, END_ROW)
        self.end_time.on_change(self.enforce_constraints)

        self.duration = Property(main, "Duration (seconds)", new_class=wx.SpinCtrlDouble)
        self.duration.add_to(main_sizer, DURATION_ROW)
        self.duration.on_change(self.enforce_constraints)

        self.width = Property(main, "Width", new_class=wx.SpinCtrl)
        self.width.add_to(main_sizer, WIDTH_ROW)
        self.width.on_change(self.enforce_constraints)

        self.height = Property(main, "Height", new_class=wx.SpinCtrl)
        self.height.add_to(main_sizer, HEIGHT_ROW)
        self.height.on_change(self.enforce_constraints)

        self.framerate = Property(main, "Framerate", new_class=wx.SpinCtrlDouble)
        self.framerate.add_to(main_sizer, FRAMERATE_ROW)
        self.framerate.on_change(self.enforce_constraints)

        self.Disable()

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

        if self.framerate.is_enabled():
            orig_framerate = float(self.framerate.get_orig())
            self.framerate.set_range(0, orig_framerate)
            self.framerate.set_calc_new(orig_framerate)

    def update(self, info):
        import fractions

        if info is None:
            self.Disable()
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
                self.width.set_orig(video_stream['width'])
                self.height.set_orig(video_stream['height'])

                framerate = round(float(fractions.Fraction(video_stream['avg_frame_rate'])), 3)
                self.framerate.set_orig(framerate)
            else:
                self.width.disable()
                self.height.disable()
                self.framerate.disable()

            self.Enable()
            self.Layout()
            self.enforce_constraints()

    def ffmpeg_opts(self):
        opts = []

        if self.start_time.is_edit():
            opts += ['-ss', str(self.start_time.get_final())]
        elif self.end_time.is_edit() and self.duration.is_edit():
            new_end = float(self.end_time.get_final())
            new_duration = float(self.duration.get_final())
            new_start = new_end - new_duration
            opts += ['-ss', str(new_start)]
        if self.end_time.is_edit():
            opts += ['-to', str(self.end_time.get_final())]
        if self.duration.is_edit():
            opts += ['-t', str(self.duration.get_final())]

        if self.width.is_edit() or self.height.is_edit():
            width = str(self.width.get_final())
            height = str(self.height.get_final())
            if not self.width.is_edit():
                width = "-1"
            if not self.height.is_edit():
                height = "-1"
            opts += ['-vf', 'scale=' + width + ':' + height]

        if self.framerate.is_edit():
            opts += ['-r', str(self.framerate.get_final())]

        return opts
