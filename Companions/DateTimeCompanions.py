import wx
from wx.adv import DatePickerCtrl, CalendarCtrl
from wx.lib import calendar

import Plugins
from PropEdit import PropertyEditors

from . import BaseCompanions, EventCollections


class CalendarConstr:
    def constructor(self):
        return {'Date': 'date', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Name': 'name'}


EventCollections.EventCategories['CalendarEvent'] = ('wx.lib.calendar.EVT_CALENDAR',
                                                     'wx.lib.calendar.EVT_CALENDAR_SEL_CHANGED',
                                                     'wx.lib.calendar.EVT_CALENDAR_DAY, EVT_CALENDAR_MONTH',
                                                     'wx.lib.calendar.EVT_CALENDAR_YEAR', 'wx.lib.calendar.EVT_CALENDAR_WEEKDAY_CLICKED')
EventCollections.commandCategories.append('CalendarEvent')


class CalendarDTC(CalendarConstr, BaseCompanions.WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        BaseCompanions.WindowDTC.__init__(
            self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.lib.calendar.CAL_SUNDAY_FIRST', 'wx.lib.calendar.CAL_MONDAY_FIRST',
                             'wx.lib.calendar.CAL_SHOW_HOLIDAYS', 'wx.lib.calendar.CAL_NO_YEAR_CHANGE',
                             'wx.lib.calendar.CAL_NO_MONTH_CHANGE'] + self.windowStyles

        self.compositeCtrl = True

    def designTimeSource(self, position='wx.DefaultPosition',
                         size='wx.DefaultSize'):
        return {'date': 'wx.DateTime.Now()',
                'pos': position,
                'size': size,
                'style': 'wx.calendar.CAL_SHOW_HOLIDAYS',
                'name': repr(self.name)}

    def events(self):
        return BaseCompanions.WindowDTC.events(self) + ['CalendarEvent']

    def writeImports(self):
        return 'import wx.lib.calendar'


class DateTimePropEditor(PropertyEditors.BITPropEditor):
    def getDisplayValue(self):
        if self.value.IsValid():
            return '<%s>' % self.value.Format()
        else:
            return '<Invalid date>'

    def valueAsExpr(self):
        if self.value.IsValid():
            v = self.value
            return 'wx.DateTimeFromDMY(%d, %d, %d, %d, %d, %d)' % (
                v.GetDay(), v.GetMonth(), v.GetYear(),
                v.GetHour(), v.GetMinute(), v.GetSecond())
        else:
            return '<Invalid date>'

    def valueToIECValue(self):
        return self.valueAsExpr()

    def inspectorEdit(self):
        if self.value.IsValid():
            PropertyEditors.BITPropEditor.inspectorEdit(self)


EventCollections.EventCategories['DatePickerCtrlEvent'] = (
    'wx.EVT_DATE_CHANGED',)
EventCollections.commandCategories.append('DatePickerCtrlEvent')


class DatePickerCtrlDTC(BaseCompanions.WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        BaseCompanions.WindowDTC.__init__(
            self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.DP_SPIN', 'wx.DP_DROPDOWN', 'wx.DP_DEFAULT',
                             'wx.DP_ALLOWNONE', 'wx.DP_SHOWCENTURY'
                             ] + self.windowStyles

    def constructor(self):
        return {'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Name': 'name'}

    def designTimeSource(self, position='wx.DefaultPosition',
                         size='wx.DefaultSize'):
        return {'pos': position,
                'size': size,
                'style': 'wx.DP_SHOWCENTURY',
                'name': repr(self.name)}

    def events(self):
        return BaseCompanions.WindowDTC.events(self) + ['DatePickerCtrlEvent']

# -------------------------------------------------------------------------------


Plugins.registerComponent('BasicControls', CalendarCtrl,
                          'wx.calendar.CalendarCtrl', CalendarDTC)
try:
    Plugins.registerComponent('BasicControls',
                              DatePickerCtrl, 'wx.DatePickerCtrl', DatePickerCtrlDTC)
except AttributeError:
    pass


PropertyEditors.registeredTypes.extend([
    ('Class', wx.DateTime, [DateTimePropEditor]),
])
