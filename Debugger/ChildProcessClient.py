import os, string, sys, time, socket
from ExternalLib import xmlrpclib
from wxPython import wx


KEEP_STREAMS_OPEN = 1
USE_TCPWATCH = 0


class TransportWithAuth (xmlrpclib.Transport):
    """Adds a proprietary but simple authentication header to the
    RPC mechanism.  NOTE: this requires xmlrpclib version 1.0.0."""

    def __init__(self, auth):
        self._auth = auth

    def send_user_agent(self, connection):
        xmlrpclib.Transport.send_user_agent(self, connection)
        connection.putheader("X-Auth", self._auth)


def spawnChild(monitor, process):
    """Returns an xmlrpclib.Server, a connection to an xml-rpc server,
    and the input and error streams.
    """
    # Start ChildProcessServerStart.py in a new process.
    script_fn = os.path.join(os.path.dirname(__file__),
                             'ChildProcessServerStart.py')
    os.environ['PYTHONPATH'] = string.join(sys.path, os.pathsep)
    cmd = '%s "%s"' % (sys.executable, script_fn)
    try:
        pid = wx.wxExecute(cmd, 0, process)
        line = ''
        if monitor.isAlive():
            istream = process.GetInputStream()
            estream = process.GetErrorStream()

            err = ''
            # read in the port and auth hash
            while monitor.isAlive() and string.find(line, '\n') < 0:
                # don't take more time than the process we wait for ;)
                time.sleep(0.00001)
                if not istream.eof():
                    line = line + istream.read(1)
                # test for tracebacks on stderr
                if not estream.eof():
                    err = estream.read()
                    errlines = string.split(err, '\n')
                    while not string.strip(errlines[-1]): del errlines[-1]
                    exctype, excvalue = string.split(errlines[-1], ':')
                    while errlines and errlines[-1][:7] != '  File ':
                        del errlines[-1]
                    if errlines:
                        errfile = ' (%s)' % string.strip(errlines[-1])
                    else:
                        errfile = ''
                    raise __builtins__[string.strip(exctype)], (
                        string.strip(excvalue)+errfile)

        if not KEEP_STREAMS_OPEN:
            process.CloseOutput()

        if monitor.isAlive():
            line = string.strip(line)
            if not line:
                raise RuntimeError, (
                    'The debug server address could not be read')
            port, auth = string.split(string.strip(line))

            if USE_TCPWATCH:
                # Start TCPWatch as a connection forwarder.
                from thread import start_new_thread
                def run_tcpwatch(port):
                    os.system("tcpwatch -L9100:%d" % int(port))
                start_new_thread(run_tcpwatch, (port,))
                time.sleep(1)
                port = 9100

            trans = TransportWithAuth(auth)
            server = xmlrpclib.Server(
                'http://127.0.0.1:%d' % int(port), trans)
            return server, istream, estream, pid
        else:
            raise RuntimeError, 'The debug server failed to start'
    except:
        if monitor.isAlive():
            process.CloseOutput()
        monitor.kill()
        raise


###################################################################


from DebugClient import DebugClient, MultiThreadedDebugClient, \
     DebuggerTask, wxEVT_DEBUGGER_EXC, wxEVT_DEBUGGER_START, \
     wxEVT_DEBUGGER_STOPPED, EVT_DEBUGGER_START


class ChildProcessClient(MultiThreadedDebugClient):

    server = None       # An xmlrpclib.Server instance
    processId = 0
    process = None      # A wxProcess
    input_stream = None
    error_stream = None

    def __init__(self, win):
        DebugClient.__init__(self, win)
        EVT_DEBUGGER_START(win, self.win_id, self.OnDebuggerStart)

    def invokeOnServer(self, m_name, m_args=(), r_name=None, r_args=()):
        task = DebuggerTask(self, m_name, m_args, r_name, r_args)
        if self.server is None:
            # Start the process, making sure the spawn occurs
            # in the main thread *only*.
            evt = self.createEvent(wxEVT_DEBUGGER_START)
            evt.SetTask(task)
            self.postEvent(evt)
        else:
            self.taskHandler.addTask(task)

    def invoke(self, m_name, m_args):
        m = getattr(self.server, m_name)
        result = apply(m, m_args)
        return result

    def isAlive(self):
        return (self.process is not None)

    def kill(self):
        server = self.server
        if server is not None:
            self.server = None
            try:
                server.exit_debugger()
            except socket.error, err:
                pass # server is already shut down
            server = None
        self.input_stream = None
        self.error_stream = None
        process = self.process
        self.process = None
        if process is not None:
            # process.Detach()
            if KEEP_STREAMS_OPEN:
                process.CloseOutput()

    def __del__(self):
        pass#self.kill()

    def pollStreams(self):
        stdin_text = ''
        stderr_text = ''
        stream = self.input_stream
        if stream is not None and not stream.eof():
            stdin_text = stream.read()
        stream = self.error_stream
        if stream is not None and not stream.eof():
            stderr_text = stream.read()
        return (stdin_text, stderr_text)

    def getProcessId(self):
        """Returns the process ID if this client is connected to another
        process."""
        return self.processId

    def OnDebuggerStart(self, evt):
        try:
            wx.wxBeginBusyCursor()
            try:
                if self.server is None:
                    # Start the subprocess.
                    process = wx.wxProcess(self.event_handler, self.win_id)
                    process.Redirect()
                    self.process = process
                    wx.EVT_END_PROCESS(self.event_handler, self.win_id,
                                       self.OnProcessEnded)
                    self.server, self.input_stream, self.error_stream, \
                          self.processId = spawnChild(self, process)
                self.taskHandler.addTask(evt.GetTask())
            except:
                t, v, tb = sys.exc_info()#[:2]
                evt = self.createEvent(wxEVT_DEBUGGER_EXC)
                evt.SetExc(t, v)
                self.postEvent(evt)
        finally:
            wx.wxEndBusyCursor()

    def OnProcessEnded(self, evt):
        self.pollStreams()
        self.kill()
        evt = self.createEvent(wxEVT_DEBUGGER_STOPPED)
        self.postEvent(evt)


if __name__ == '__main__':
    a = wx.wxPySimpleApp()
    f = wx.wxFrame(None, -1, '')
    f.Show()
    cpc = ChildProcessClient(f)
    cpc.OnDebuggerStart(None)
    a.MainLoop()
