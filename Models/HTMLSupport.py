# -----------------------------------------------------------------------------
# Name:        HTMLSupport.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2007
# Licence:     GPL
# -----------------------------------------------------------------------------
import wx

import Plugins
import Preferences
import Utils
from Models.EditorModels import PersistentModel
from Utils import _
from Views.EditorViews import HTMLFileView
from Views.SourceViews import EditorStyledTextCtrl
from Views.StyledTextCtrls import LanguageSTCMix, stcConfigPath

from . import Controllers, EditorHelper

print('importing Models.HTMLSupport')


EditorHelper.imgHTMLFileModel = EditorHelper.imgIdxRange()


class HTMLFileModel(PersistentModel):
    modelIdentifier = 'HTML'
    defaultName = 'html'
    bitmap = 'WebDocHTML.png'
    imgIdx = EditorHelper.imgHTMLFileModel
    ext = '.html'


class BaseHTMLStyledTextCtrlMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId,
                                (0, Preferences.STCLineNumMarginWidth), 'html', stcConfigPath)


class HTMLStyledTextCtrlMix(BaseHTMLStyledTextCtrlMix):
    def __init__(self, wId):
        BaseHTMLStyledTextCtrlMix.__init__(self, wId)
        self.setStyles()


wxID_HTMLSOURCEVIEW = wx.NewId()


class HTMLSourceView(EditorStyledTextCtrl, HTMLStyledTextCtrlMix):
    viewName = 'HTML'
    viewTitle = _('HTML')

    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_HTMLSOURCEVIEW,
                                      model, (), -1)
        HTMLStyledTextCtrlMix.__init__(self, wxID_HTMLSOURCEVIEW)
        self.active = True


class HTMLFileController(Controllers.PersistentController):
    Model = HTMLFileModel
    DefaultViews = [HTMLSourceView]
    AdditionalViews = [HTMLFileView]

# -------------------------------------------------------------------------------


Plugins.registerFileType(HTMLFileController, aliasExts=('.htm',))
Plugins.registerLanguageSTCStyle(
    'HTML',
    'html',
    BaseHTMLStyledTextCtrlMix,
    'stc-styles.rc.cfg')
