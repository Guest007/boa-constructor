#Boa:Dialog:MakePyDialog

import wx
from wx.lib.anchors import LayoutAnchors
from win32com.client import selecttlb, makepy
import traceback, types

def create(parent):
    return MakePyDialog(parent)

[wxID_MAKEPYDIALOG, wxID_MAKEPYDIALOGBFORDEMAND, wxID_MAKEPYDIALOGCANCEL, 
 wxID_MAKEPYDIALOGDIRECTSPECIFICATION, wxID_MAKEPYDIALOGOK, 
 wxID_MAKEPYDIALOGTYPELIBRARYLIST, 
] = [wx.NewId() for _init_ctrls in range(6)]

class MakePyDialog(wx.Dialog):
    def _init_coll_typeLibraryList_Columns(self, parent):
        # generated method, don't edit

        parent.InsertColumn(col=0, format=wx.LIST_FORMAT_CENTRE,
              heading='Library Name', width=372)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_MAKEPYDIALOG, name='MakePyDialog',
              parent=prnt, pos=wx.Point(498, 119), size=wx.Size(420, 433),
              style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
              title='COM Library Generator')
        self.SetAutoLayout(True)
        self.SetClientSize(wx.Size(412, 406))
        self.Bind(wx.EVT_INIT_DIALOG, self.OnMakepydialogInitDialog)

        self.typeLibraryList = wx.ListCtrl(id=wxID_MAKEPYDIALOGTYPELIBRARYLIST,
              name='typeLibraryList', parent=self, pos=wx.Point(16, 40),
              size=wx.Size(376, 280), style=wx.LC_NO_HEADER | wx.LC_REPORT,
              validator=wx.DefaultValidator)
        self.typeLibraryList.SetToolTipString('List of the registered COM type libraries on your system')
        self.typeLibraryList.SetConstraints(LayoutAnchors(self.typeLibraryList,
              True, True, True, True))
        self._init_coll_typeLibraryList_Columns(self.typeLibraryList)
        self.typeLibraryList.Bind(wx.EVT_LEFT_DCLICK,
              self.OnTypelibrarylistLeftDclick)

        self.OK = wx.Button(id=wxID_MAKEPYDIALOGOK, label='Generate', name='OK',
              parent=self, pos=wx.Point(200, 360), size=wx.Size(88, 27),
              style=0)
        self.OK.SetToolTipString('Click to generate a wrapper for the selected library')
        self.OK.SetConstraints(LayoutAnchors(self.OK, False, False, True, True))
        self.OK.Bind(wx.EVT_BUTTON, self.OnOkButton, id=wxID_MAKEPYDIALOGOK)

        self.Cancel = wx.Button(id=wx.ID_CANCEL, label='Cancel', name='Cancel',
              parent=self, pos=wx.Point(304, 360), size=wx.Size(88, 27),
              style=0)
        self.Cancel.SetToolTipString('Cancel wrapper generation')
        self.Cancel.SetConstraints(LayoutAnchors(self.Cancel, False, False,
              True, True))

        self.bForDemand = wx.CheckBox(id=wxID_MAKEPYDIALOGBFORDEMAND,
              label='Generate Classes on Demand', name='bForDemand',
              parent=self, pos=wx.Point(144, 328), size=wx.Size(248, 20),
              style=0)
        self.bForDemand.SetToolTipString('Minimises amount of code generated by only wrapping used classes (recommended).  Clear to generate a single-file wrapper.')
        self.bForDemand.SetValue(True)
        self.bForDemand.SetConstraints(LayoutAnchors(self.bForDemand, False,
              False, True, True))
        self.bForDemand.Bind(wx.EVT_CHECKBOX, self.OnBfordemandCheckbox,
              id=wxID_MAKEPYDIALOGBFORDEMAND)

        self.directSpecification = wx.TextCtrl(id=wxID_MAKEPYDIALOGDIRECTSPECIFICATION,
              name='directSpecification', parent=self, pos=wx.Point(16, 8),
              size=wx.Size(376, 28), style=0, value='')
        self.directSpecification.SetToolTipString('Type text here to search for matching type libraries')
        self.directSpecification.SetConstraints(LayoutAnchors(self.directSpecification,
              True, True, True, False))
        self.directSpecification.Bind(wx.EVT_TEXT,
              self.OnDirectspecificationText,
              id=wxID_MAKEPYDIALOGDIRECTSPECIFICATION)

    def __init__(self, parent):
        self._init_ctrls(parent)

        self.generatedFilename =''

    def OnTypelibrarylistLeftDclick(self, event):
        return self.OnOkButton( event )

    def OnOkButton(self, event):
        index = self.typeLibraryList.GetNextItem(-1,state=wx.LIST_STATE_SELECTED  )
        # there could be multiple selected, should decide what to do then...
        if index != -1:
            self.generatedFilename = self.Generate( self.libraryList[index] )
            print(('generated to filename', self.generatedFilename))
        return self.EndModal(wx.ID_OK)

    def Generate( self, typeLibrary):
        """ Generate wrapper for a given type library """
        progress = Progress( self )

        try:
            makepy.GenerateFromTypeLibSpec(
                typeLibrary, None,
                bForDemand = 1,
                bBuildHidden = 1,
                progressInstance = progress,
            )
            filename =progress.filename
            progress.Destroy()
        except Exception as error:
            traceback.print_exc()
            errorMessage =wx.MessageDialog( self, str(error), "Generation Failure!", style=wx.OK)
            progress.Destroy()
            errorMessage.ShowModal()
            errorMessage.Destroy()
            return None
        return filename

    def OnDirectspecificationText(self, event):
        '''Set focus to any matching item while typing'''
        text = self.directSpecification.GetValue()
        if text:
            items = self.SearchList( text )
            if items:
                for index in range(self.typeLibraryList.GetItemCount()):
                    self.typeLibraryList.SetItemState( index, 0, wx.LIST_STATE_SELECTED )
                for (index,item) in items:
                    self.typeLibraryList.SetItemState( index, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED )
                self.typeLibraryList.EnsureVisible( items[0][0] )
        event.Skip()


    def SearchList( self, text ):
        """ Attempt to find the specified text in the list
        of DLL names, classID, and descriptions."""
        import re
        finder = re.compile( text, re.IGNORECASE )
        items = []
        wx.BeginBusyCursor()
        try:
            for attribute in ('desc', 'clsid','dll',):
                for index in range(len( self.libraryList)):
                    librarySpecification = self.libraryList[index]
                    try:
                        value = getattr( librarySpecification, attribute)
                        if value and type(value) == bytes:
                            if finder.search( value ):
                                items.append( (index, librarySpecification))
                    except Exception as error:
                        pass
##                    print error, librarySpecification, attribute, repr(getattr( librarySpecification, attribute))
        finally:
            wx.EndBusyCursor()
        return items

    def OnMakepydialogInitDialog(self, event):
        '''Initialisation of the dialog starts up a
        process of loading the type library definitions.'''
        wx.BeginBusyCursor()
        try:
            self.libraryList = libraryList = selecttlb.EnumTlbs()
            libraryList.sort()
            for index in range(len( libraryList)):
                librarySpecification = libraryList[index]
                self.typeLibraryList.InsertStringItem(
                    index,
                    librarySpecification.desc
                )
        finally:
            wx.EndBusyCursor()

    def OnBfordemandCheckbox(self, event):
        pass

class Progress(wx.ProgressDialog):
    verboseLevel = 1
    filename = ""
    def __init__(self, parent):
        wx.ProgressDialog.__init__(
            self, "MakePy Progress",
            "Generating type library wrappers",
            parent=parent, style=wx.PD_AUTO_HIDE | wx.PD_APP_MODAL,
        )
    def Close(self, event=None):
        pass
    def Starting( self, description=None ):
        pass
    def Finished(self):
        pass
    def SetDescription(self, desc, maxticks = None):
        self.Update(-1,  newmsg = desc )
    def Tick(self, desc = None):
        pass
    def VerboseProgress(self, desc, verboseLevel = 2):
        if self.verboseLevel >= verboseLevel:
            self.SetDescription(desc)

    def LogBeginGenerate(self, filename):
        self.VerboseProgress("Generating to %s" % filename, 1)
        self.filename = filename

    def LogWarning(self, desc):
        self.VerboseProgress("WARNING: " + desc, 1)

if __name__ == "__main__":
    class DemoFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, 2400, "File entry with browse", size=(500,150) )
            dialog = MakePyDialog( self )
            dialog.ShowModal( )
            dialog.Destroy()

    class DemoApp(wx.App):
        def OnInit(self):
            wx.Image_AddHandler(wx.JPEGHandler())
            wx.Image_AddHandler(wx.PNGHandler())
            wx.Image_AddHandler(wx.GIFHandler())
            frame = DemoFrame(None)
            frame.Show(True)
            self.SetTopWindow(frame)
            return True
    def test( ):
        app = DemoApp(0)
        app.MainLoop()
    print('Creating dialog')
    test( )
