# -----------------------------------------------------------------------------
# Name:        XMLSupport.py
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
from Views.SourceViews import EditorStyledTextCtrl
from Views.StyledTextCtrls import LanguageSTCMix, stcConfigPath

from . import Controllers, EditorHelper

print('importing Models.XMLSupport')


EditorHelper.imgXMLFileModel = EditorHelper.imgIdxRange()


class XMLFileModel(PersistentModel):
    modelIdentifier = 'XML'
    defaultName = 'xml'
    bitmap = 'WebDocXML.png'
    imgIdx = EditorHelper.imgXMLFileModel
    ext = '.xml'


class XMLStyledTextCtrlMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId,
                                (0, Preferences.STCLineNumMarginWidth), 'xml', stcConfigPath)
        self.setStyles()


wxID_XMLSOURCEVIEW = wx.NewId()


class XMLSourceView(EditorStyledTextCtrl, XMLStyledTextCtrlMix):
    viewName = 'XML'
    viewTitle = _('XML')

    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_XMLSOURCEVIEW,
                                      model, (), -1)
        XMLStyledTextCtrlMix.__init__(self, wxID_XMLSOURCEVIEW)
        self.active = True


class XMLFileController(Controllers.PersistentController):
    Model = XMLFileModel
    DefaultViews = [XMLSourceView]
    try:
        from Views.XMLView import XMLTreeView
        AdditionalViews = [XMLTreeView]
    except ImportError:
        AdditionalViews = []

# -------------------------------------------------------------------------------


Plugins.registerFileType(XMLFileController, aliasExts=('.dtd', '.xrc'))
Plugins.registerLanguageSTCStyle(
    'XML',
    'xml',
    XMLStyledTextCtrlMix,
    'stc-styles.rc.cfg')
