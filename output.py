import os
import subprocess
import threading

import wx

from options import FFmpegOptions


class OutputPanel(wx.Panel):
    def __init__(self, *args, get_ffmpeg_args=lambda: FFmpegOptions([], []), **kw):
        super(OutputPanel, self).__init__(*args, **kw)
        self.update_listeners = []
        self.input_path = None
        self.get_ffmpeg_args = get_ffmpeg_args

        root_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, label="Output")
        self.SetSizer(root_sizer)

        file_panel = wx.Panel(self)
        root_sizer.Add(file_panel, flag=wx.EXPAND, border=5)
        file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        file_panel.SetSizer(file_sizer)
        file_sizer.Add(wx.StaticText(file_panel, label="File"), flag=wx.EXPAND, border=5)
        self.file_text = wx.TextCtrl(file_panel)
        self.file_text.Bind(wx.EVT_TEXT, self.handle_file_changed)
        file_sizer.Add(self.file_text, proportion=1, flag=wx.EXPAND, border=5)
        self.file_browse_button = wx.Button(file_panel, label="Browse")
        self.file_browse_button.Bind(wx.EVT_BUTTON, self.handle_file_browse_pressed)
        file_sizer.Add(self.file_browse_button, flag=wx.EXPAND, border=5)

        options_panel = wx.Panel(self)
        root_sizer.Add(options_panel, flag=wx.EXPAND, border=5)
        options_sizer = wx.BoxSizer(wx.HORIZONTAL)
        options_panel.SetSizer(options_sizer)
        self.silence = wx.CheckBox(options_panel, label="Silence")
        options_sizer.Add(self.silence, proportion=1, flag=wx.EXPAND, border=5)
        self.deepfry = wx.CheckBox(options_panel, label="Compress beyond recognition")
        options_sizer.Add(self.deepfry, proportion=1, flag=wx.EXPAND, border=5)

        self.run_panel = wx.Panel(self)
        root_sizer.Add(self.run_panel, flag=wx.EXPAND, border=5)
        run_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.run_panel.SetSizer(run_sizer)
        run_button = wx.Button(self.run_panel, label="Run")
        run_button.Bind(wx.EVT_BUTTON, self.handle_run_pressed)
        run_sizer.Add(run_button, proportion=1, flag=wx.EXPAND, border=5)
        run_preview_button = wx.Button(self.run_panel, label="Run && Preview")
        run_preview_button.Bind(wx.EVT_BUTTON, self.handle_run_preview_pressed)
        run_sizer.Add(run_preview_button, proportion=1, flag=wx.EXPAND, border=5)
        run_quit_button = wx.Button(self.run_panel, label="Run && Quit")
        run_quit_button.Bind(wx.EVT_BUTTON, self.handle_run_quit_pressed)
        run_sizer.Add(run_quit_button, proportion=1, flag=wx.EXPAND, border=5)
        self.run_panel.Disable()

        self.logs = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        root_sizer.Add(self.logs, proportion=1, flag=wx.EXPAND, border=5)

        self.Disable()

    def handle_file_changed(self, _):
        path = self.file_text.GetValue()
        (folder, name) = os.path.split(path)
        try:
            os.stat(folder)
            self.run_panel.Enable()
        except FileNotFoundError:
            self.run_panel.Disable()

    def handle_file_browse_pressed(self, _):
        dialog = wx.FileDialog(self, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dialog.ShowModal() == wx.ID_OK:
            self.file_text.SetValue(dialog.GetPath())

    def handle_run_pressed(self, _, callback=lambda _: None):
        self.logs.Clear()
        self.run_panel.Disable()
        real_args = self.get_ffmpeg_args()
        input_args = real_args.input
        output_args = real_args.output
        output_path = self.file_text.GetValue()
        (folder, name) = os.path.split(output_path)
        (name, ext) = os.path.splitext(name)
        if self.silence.GetValue():
            output_args += ['-an']
        if ext == '.gif':
            filter_before = '[0:v] '
            filter_after = 'split [a][b];[a] palettegen [p];[b][p] paletteuse'
            filter_during = ''
            if '-vf' in output_args:
                for i in range(len(output_args) - 1):
                    [a, b] = output_args[i:i + 2]
                    if a == '-vf':
                        filter_during = b + ','
                    output_args[i:i + 2] = []
                    break
            output_args += ['-filter_complex', filter_before + filter_during + filter_after]
        if self.deepfry.GetValue():
            if ext == '.mp3':
                output_args += ['-q:a', '9']
            else:
                output_args += ['-q:a', '0.1', '-crf', '51']
        args = ['ffmpeg', '-hide_banner', '-y'] + input_args + ['-i', self.input_path] + output_args + [output_path]
        print(args)

        def run():
            # noinspection PyArgumentList
            proc = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True)
            while proc.poll() is None:
                out_data = proc.stdout.readline()
                if out_data != '':
                    wx.CallAfter(lambda: self.add_log(out_data))
            wx.CallAfter(lambda: self.run_panel.Enable())
            wx.CallAfter(lambda: callback(proc.returncode))

        threading.Thread(target=run).start()

    def handle_run_preview_pressed(self, _event):
        def preview(code):
            if code == 0:
                out_file = self.file_text.GetValue()
                subprocess.Popen(['ffplay', '-autoexit', out_file])

        self.handle_run_pressed(_event, callback=preview)

    def handle_run_quit_pressed(self, _event):
        def quit(code):
            if code == 0:
                parent = self.GetTopLevelParent()
                parent.Close(True)

        self.handle_run_pressed(_event, callback=quit)

    def set_input_path(self, path, data):
        if data is None:
            self.input_path = None
            self.Disable()
        else:
            self.input_path = path
            self.Enable()

    def add_log(self, data):
        self.logs.AppendText(data)
