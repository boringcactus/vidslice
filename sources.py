import glob
import json
import subprocess
import tempfile
import threading

import wx


def has_ytdl():
    try:
        subprocess.run(["youtube-dl", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False


class SourcesPanel(wx.Panel):
    """
    A Panel representing source info
    """

    def __init__(self, *args, **kw):
        super(SourcesPanel, self).__init__(*args, **kw)
        self.update_listeners = []

        root_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, label="Sources")
        self.SetSizer(root_sizer)
        main = wx.Panel(self)
        root_sizer.Add(main, proportion=1, flag=wx.EXPAND, border=5)
        main_sizer = wx.GridBagSizer(5, 5)
        main.SetSizer(main_sizer)

        if has_ytdl():
            main_sizer.Add(wx.StaticText(main, label="URL"), wx.GBPosition(0, 0), flag=wx.EXPAND)
            self.url_text = wx.TextCtrl(main)
            main_sizer.Add(self.url_text, wx.GBPosition(0, 1), flag=wx.EXPAND)
            self.url_download_button = wx.Button(main, label="Download")
            self.url_download_button.Bind(wx.EVT_BUTTON, self.handle_url_download_pressed)
            main_sizer.Add(self.url_download_button, wx.GBPosition(0, 2), flag=wx.EXPAND)
        else:
            no_ytdl_label = wx.StaticText(main, label="Could not find youtube-dl, can't download videos automatically")
            main_sizer.Add(no_ytdl_label, wx.GBPosition(0, 0), wx.GBSpan(1, 3), flag=wx.EXPAND)

        main_sizer.Add(wx.StaticText(main, label="File"), wx.GBPosition(1, 0), flag=wx.EXPAND)
        self.file_text = wx.TextCtrl(main)
        self.file_text.Bind(wx.EVT_TEXT, self.handle_file_changed)
        main_sizer.Add(self.file_text, wx.GBPosition(1, 1), flag=wx.EXPAND)
        self.file_browse_button = wx.Button(main, label="Browse")
        self.file_browse_button.Bind(wx.EVT_BUTTON, self.handle_file_browse_pressed)
        main_sizer.Add(self.file_browse_button, wx.GBPosition(1, 2), flag=wx.EXPAND)

        self.status_label = wx.StaticText(main, label="Status: Select a file")
        main_sizer.Add(self.status_label, wx.GBPosition(2, 0), wx.GBSpan(1, 3))

        main_sizer.AddGrowableCol(1, proportion=1)

    def set_status(self, text):
        self.status_label.SetLabel("Status: " + text)

    def handle_url_download_pressed(self, _):
        self.set_status("Downloading...")

        def download():
            file = tempfile.NamedTemporaryFile(delete=False)
            # noinspection PyArgumentList
            proc = subprocess.Popen([
                'youtube-dl', '-o', file.name + '.%(ext)s', self.url_text.GetValue()
            ], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            while proc.poll() is None:
                out_data = proc.stdout.readline()
                if out_data != '':
                    wx.CallAfter(lambda: self.set_status("Downloading: " + out_data.strip()))
            if proc.returncode == 0:
                output_file = glob.glob(glob.escape(file.name) + '.*')[0]
                wx.CallAfter(lambda: self.set_status("Downloaded!"))
                wx.CallAfter(lambda: self.file_text.SetValue(output_file))
            else:
                error = ''.join(proc.stderr.readlines()).strip()
                wx.CallAfter(lambda: self.set_status("Couldn't download: " + error))

        threading.Thread(target=download).start()

    def handle_file_browse_pressed(self, _):
        dialog = wx.FileDialog(self, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            self.file_text.SetValue(dialog.GetPath())

    def handle_file_changed(self, _event):
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-of', 'json',
            '-show_entries', 'format=start_time,duration:stream=index,codec_type,avg_frame_rate,width,height',
            self.file_text.GetValue()
        ], capture_output=True, text=True)
        if result.returncode == 0:
            ffprobe_data = json.loads(result.stdout)
            self.set_status("Successfully loaded media info")
            for listener in self.update_listeners:
                listener(ffprobe_data)
        else:
            self.set_status("Failed to load media info: " + result.stderr)
            for listener in self.update_listeners:
                listener(None)

    def on_update(self, callback):
        self.update_listeners.append(callback)

    def get_file(self):
        return self.file_text.GetValue()
