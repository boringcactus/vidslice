import subprocess
import sys

import wx
import wx.adv

from options import OptionsPanel
from output import OutputPanel
from sources import SourcesPanel, update_ytdl


def has_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False


class VidsliceFrame(wx.Frame):
    """
    A Frame that contains vidslice logic
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(VidsliceFrame, self).__init__(*args, **kw)

        root_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(root_sizer)
        main = wx.Panel(self)
        root_sizer.Add(main, proportion=1, flag=wx.EXPAND, border=5)
        main_sizer = wx.GridBagSizer(5, 5)
        main.SetSizer(main_sizer)

        # set up sources panel
        self.sources_panel = SourcesPanel(main)
        main_sizer.Add(self.sources_panel, wx.GBPosition(0, 0), wx.GBSpan(1, 2), flag=wx.EXPAND)

        # set up options panel
        self.options_panel = OptionsPanel(main)
        main_sizer.Add(self.options_panel, wx.GBPosition(1, 0), flag=wx.EXPAND)
        main_sizer.AddGrowableRow(1, proportion=1)
        self.sources_panel.on_update(self.options_panel.update)

        # set up output panel
        self.output_panel = OutputPanel(main, get_ffmpeg_args=self.options_panel.ffmpeg_opts)
        main_sizer.Add(self.output_panel, wx.GBPosition(1, 1), flag=wx.EXPAND)
        main_sizer.AddGrowableCol(1, proportion=1)
        self.sources_panel.on_update(lambda data: self.output_panel.set_input_path(self.sources_panel.get_file(), data))

        # create a menu bar
        self.make_menu_bar()

        size = root_sizer.GetMinSize()
        self.SetMinClientSize(size)

        if len(sys.argv) > 1:
            self.sources_panel.file_text.SetValue(sys.argv[1])

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
        update_item = file_menu.Append(-1, "Update youtube-dl")
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
        self.Bind(wx.EVT_MENU, self.on_update, update_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

    def on_exit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    def on_update(self, event):
        import threading
        threading.Thread(target=update_ytdl, args=(self,)).start()

    def on_about(self, event):
        """Display an About Dialog"""
        info = wx.adv.AboutDialogInfo()
        info.SetName("vidslice")
        info.SetVersion("1.1")
        info.SetDescription("video manipulator wrapping youtube-dl and ffmpeg")
        info.SetWebSite("https://github.com/boringcactus/vidslice")

        wx.adv.AboutBox(info)


if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    if not has_ffmpeg():
        answer = wx.MessageBox("Could not find ffmpeg. Open vidslice README?", "Error", wx.YES_NO, None)
        if answer == wx.YES:
            import webbrowser

            webbrowser.open("https://github.com/boringcactus/vidslice/blob/master/README.md")
    else:
        frm = VidsliceFrame(None, title='vidslice')
        app.SetTopWindow(frm)
        frm.Show()
    app.MainLoop()
