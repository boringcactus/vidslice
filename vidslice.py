# First things, first. Import the wxPython package.
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
        root_sizer.Add(main, proportion=1, flag=wx.EXPAND, border=3)
        main_sizer = wx.GridBagSizer()
        main.SetSizer(main_sizer)

        url_label = wx.StaticText(main, label="URL")
        main_sizer.Add(url_label, wx.GBPosition(0, 0), flag=wx.EXPAND)
        self.url_text = wx.TextCtrl(main)
        main_sizer.Add(self.url_text, wx.GBPosition(0, 1), flag=wx.EXPAND)
        self.url_download_button = wx.Button(main, label="Download")
        self.url_download_button.Bind(wx.EVT_BUTTON, self.handle_url_download_pressed)
        main_sizer.Add(self.url_download_button, wx.GBPosition(0, 2), flag=wx.EXPAND)
        if not has_ytdl():
            tooltip = "Could not find youtube-dl"
            url_label.Disable()
            self.url_text.Disable()
            self.url_text.SetToolTip(tooltip)
            self.url_download_button.Disable()
            self.url_download_button.SetToolTip(tooltip)

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
            output_file = glob.glob(glob.escape(file.name) + '.*')[0]
            wx.CallAfter(lambda: self.set_status("Downloaded!"))
            wx.CallAfter(lambda: self.file_text.SetValue(output_file))

        threading.Thread(target=download).start()

    def handle_file_browse_pressed(self, _):
        dialog = wx.FileDialog(self, message="message")
        if dialog.ShowModal() == wx.ID_OK:
            self.file_text.SetValue(dialog.GetPath())

    def handle_file_changed(self, event):
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-of', 'json',
            '-show_entries', 'format=start_time,duration:stream=index,codec_type,avg_frame_rate,width,height',
            self.file_text.GetValue()
        ], capture_output=True, text=True)
        if result.stderr != "":
            print(result.stderr)
        ffprobe_data = json.loads(result.stdout)
        del ffprobe_data['programs']
        print(ffprobe_data)
        if result.returncode == 0:
            self.set_status("Successfully loaded media info")
            for listener in self.update_listeners:
                listener(ffprobe_data)
        else:
            self.set_status("Failed to load media info: " + result.stderr)

    def on_update(self, callback):
        self.update_listeners.append(callback)


class HelloFrame(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(HelloFrame, self).__init__(*args, **kw)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # set up sources panel
        sources_panel = SourcesPanel(self)
        main_sizer.Add(sources_panel, proportion=0, flag=wx.EXPAND)

        # create a panel in the frame
        options_panel = wx.Panel(self)
        main_sizer.Add(options_panel, proportion=1, flag=wx.EXPAND)

        # and put some text with a larger bold font on it
        st = wx.StaticText(options_panel, label="Hello World!")
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)

        # create a menu bar
        self.make_menu_bar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Welcome to wxPython!")

        # main_sizer.SetSizeHints(self)
        self.SetSizer(main_sizer)

    def make_menu_bar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        file_menu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        hello_item = file_menu.Append(-1, "&Hello...\tCtrl-H",
                                      "Help string shown in status bar for this menu item")
        file_menu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exit_item = file_menu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(help_menu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menu_bar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.on_hello, hello_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

    def on_exit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    def on_hello(self, event):
        """Say hello to the user."""
        wx.MessageBox("Hello again from wxPython")

    def on_about(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK | wx.ICON_INFORMATION)


if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = HelloFrame(None, title='Hello World 2')
    frm.Show()
    app.MainLoop()
