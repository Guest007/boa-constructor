#-----------------------------------------------------------------------------
# Name:        ModRunner.py
# Purpose:     Different process executers.
#
# Author:      Riaan Booysen
#
# Created:     2001/12/02
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2003 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

import string, traceback
from os import path
from popen2import import popen3

from wxPython.wx import *

import Preferences, Utils

import ErrorStack

class ModuleRunner:
    def __init__(self, esf, app, runningDir=''):
        self.init(esf, app)
        self.runningDir = runningDir
        self.results = {}

    def run(self, cmd):
        pass

    def init(self, esf, app):
        self.esf = esf
        if esf:
            self.esf.app = app
        else:
            self.app = app

    def recheck(self):
        if self.results:
            return apply(self.checkError, (), self.results)

    def checkError(self, err, caption, out=None, root='Error', errRaw=()):
        if self.esf:
            if err or out:
                tbs = self.esf.updateCtrls(err, out, root, self.runningDir, errRaw)
                self.esf.display(len(err))
                return tbs
            else:
                self.esf.updateCtrls([])
                return None
        else:
            self.results = {'err': err,
                            'caption': caption,
                            'out': out,
                            'root': root,
                            'errRaw': errRaw}


class CompileModuleRunner(ModuleRunner):
    """ Uses compiles a module to show syntax errors

    If the model is not saved, the source in the model is compiled directly.
    Saved models (on the filesystem) are compiled from their files. This is
    useful for generating the .pyc files """
    def run(self, filename, source, modified):
        protsplit = string.find(filename, '://')
        if protsplit != -1:
            prot, filename = filename[:protsplit], filename[protsplit+3:]
        else:
            prot = 'file'

        source = Utils.toUnixEOLMode(source)+'\n\n'
        try:
            code = compile(source, filename, 'exec')
        except SyntaxError:
            etype, value, tb = sys.exc_info()
            try:
                traceback.print_exception(etype, value, tb, 0, sys.stderr)
            finally:
                etype = value = tb = None
        except:
            # Add filename to traceback object
            etype, value, tb = sys.exc_info()
            try:
                msg, (_filename, lineno, offset, line) = value.args
                if not _filename:
                    # XXX this is broken on too long lines
                    value.args = msg, (filename, lineno, offset, line)
                    value.filename = filename
                traceback.print_exc()
            finally:
                etype = value = tb = None

        # auto generating pycs is sometimes a pain
        ##        if modified or prot != 'file':
        ##        else:
        ##            import py_compile
        ##            py_compile.compile(filename)

class ExecuteModuleRunner(ModuleRunner):
    """ Uses wxPython's wxExecute, no redirection """
    def run(self, cmd):
        wxExecute(cmd, true)

class ProcessModuleRunner(ModuleRunner):
    """ Uses wxPython's wxProcess, output and errors are redirected and displayed
        in a frame. A cancelable dialog displays while the process executes
        This currently only works for non GUI processes """
    def run(self, cmd, Parser=ErrorStack.StdErrErrorParser,
            caption='Execute module', root='Error', autoClose=false):
        import ProcessProgressDlg
        dlg = ProcessProgressDlg.ProcessProgressDlg(None, cmd, caption,
              autoClose=autoClose)
        try:
            dlg.ShowModal()
            serr = ErrorStack.buildErrorList(dlg.errors, Parser)
            return self.checkError(serr, 'Ran', dlg.output, root, dlg.errors)

        finally:
            dlg.Destroy()

class PopenModuleRunner(ModuleRunner):
    """ Uses Python's popen2, output and errors are redirected and displayed
        in a frame. """
    def run(self, cmd, inpLines=[]):
        inpLines.reverse()
        inp, outp, errp = popen3(cmd)
        out = []
        while 1:
            if inpLines:
                inp.write(inpLines.pop())
            l = outp.readline()
            if not l: break
            out.append(l)

        errLines = errp.readlines()
        serr = ErrorStack.buildErrorList(errLines)

        if serr or out:
            return self.checkError(serr, 'Ran', out, errRaw=errLines)
        else:
            return None

PreferredRunner = PopenModuleRunner

wxEVT_EXEC_FINISH = wxNewId()

def EVT_EXEC_FINISH(win, func):
    win.Connect(-1, -1, wxEVT_EXEC_FINISH, func)

class ExecFinishEvent(wxPyEvent):
    def __init__(self, runner):
        wxPyEvent.__init__(self)
        self.SetEventType(wxEVT_EXEC_FINISH)
        self.runner = runner
