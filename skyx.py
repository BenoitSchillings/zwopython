''' Module to handle connections to TheSkyX
The classes are defined to match the classes in Script TheSkyX. This isn't
really necessary as they all just send the javascript to TheSkyX via
SkyXConnection._send().
'''
from __future__ import print_function

import logging
import time
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR, error


#-------------------------------------------------------------------------


logger = logging.getLogger(__name__)

class Singleton(object):
    ''' Singleton class so we dont have to keep specifing host and port'''
    def __init__(self, klass):
        ''' Initiator '''
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwds):
        ''' When called as a function return our singleton instance. '''
        if self.instance is None:
            self.instance = self.klass(*args, **kwds)
        return self.instance

#-------------------------------------------------------------------------

class SkyxObjectNotFoundError(Exception):
    ''' Exception for objects not found in SkyX.
    '''
    def __init__(self, value):
        ''' init'''
        super(SkyxObjectNotFoundError, self).__init__(value)
        self.value = value

    def __str__(self):
        ''' returns the error string '''
        return repr(self.value)

#-------------------------------------------------------------------------

class SkyxConnectionError(Exception):
    ''' Exception for Failures to Connect to SkyX
    '''
    def __init__(self, value):
        ''' init'''
        super(SkyxConnectionError, self).__init__(value)
        self.value = value

    def __str__(self):
        ''' returns the error string '''
        return repr(self.value)

#-------------------------------------------------------------------------


class SkyxTypeError(Exception):
    ''' Exception for Failures to Connect to SkyX
    '''
    def __init__(self, value):
        ''' init'''
        super(SkyxTypeError, self).__init__(value)
        self.value = value

    def __str__(self):
        ''' returns the error string '''
        return repr(self.value)

#-------------------------------------------------------------------------
    
@Singleton
class SkyXConnection(object):
    ''' Class to handle connections to TheSkyX
    '''
    def __init__(self, host="localhost", port=3040):
        ''' define host and port for TheSkyX.
        '''
        self.host = host
        self.port = port
        
    def reconfigure(self,host="localhost", port=3040):
        ''' If we need to chane ip we can do so this way'''
        self.host = host
        self.port = port
                
    def _send(self, command):
        ''' sends a js script to TheSkyX and returns the output.
        '''
        try:
            logger.debug(command)
            sockobj = socket(AF_INET, SOCK_STREAM)
            sockobj.connect((self.host, self.port))
            sockobj.send(bytes('/* Java Script */\n' +
                               '/* Socket Start Packet */\n' + command +
                               '\n/* Socket End Packet */\n', 'utf8'))
            output = sockobj.recv(2048)
            output = output.decode('utf-8')
            logger.debug(output)
            sockobj.shutdown(SHUT_RDWR)
            sockobj.close()

            return output.split("|")[0]
        except error as msg:
            raise SkyxConnectionError("Connection to " + self.host + ":" + \
                                      str(self.port) + " failed. :" + str(msg))


#-------------------------------------------------------------------------

    def find(self, target):
        ''' Find a target
            target can be a defined object or a decimal ra,dec
        '''
        output = self._send('sky6StarChart.Find("' + target + '")')
        if output == "undefined":
            return True
        else:
            raise SkyxObjectNotFoundError(target)
                                    
 
#-------------------------------------------------------------------------

 
class sky6RASCOMTele(object):
    ''' Class to implement the ccdsoftCamera script class
    '''
    def __init__(self, host="localhost", port=3040):
        ''' Define connection
        '''
        self.conn = SkyXConnection(host, port)
        
    def Connect(self):
        ''' Connect to the telescope
        '''
        command = """
                  var Out;
                  sky6RASCOMTele.Connect();
                  Out = sky6RASCOMTele.IsConnected"""

        output = self.conn._send(command).splitlines()

        if int(output[0]) != 1:
            raise SkyxTypeError("Telescope not connected. "+\
                                "sky6RASCOMTele.IsConnected=" + output[0])
        return True
        
    def Disconnect(self):
        ''' Disconnect the telescope
            Whatever this actually does...
        '''
        command = """
                  var Out;
                  sky6RASCOMTele.Disconnect();
                  Out = sky6RASCOMTele.IsConnected"""
        output = self.conn._send(command, 'utf8').splitlines()
        if int(output[0]) != 0:
            raise SkyxTypeError("Telescope still connected. " +\
                                "sky6RASCOMTele.IsConnected=" + output[0])
        return True

    def GetRaDec(self):
        ''' Get the current RA and Dec
        '''
        command = """
                  var Out;
                  sky6RASCOMTele.GetRaDec();
                  Out = String(sky6RASCOMTele.dRa) + " " + String(sky6RASCOMTele.dDec);
                  """
        output = self.conn._send(command).splitlines()[0].split()      
        return output
    
    def Sync(self, pos):
        ''' Sync to a given pos [ra, dec]
            ra, dec should be Jnow coordinates
        '''
        command = """
                var Out = "";
                sky6RASCOMTele.Sync(""" + str(pos[0]) + "," + str(pos[1]) + """, "pyskyx");
                """
        output = self.conn._send(command).splitlines()
        print(output)
        time.sleep(1)
        print(self.GetRaDec())

    def goto(self, ra, dec):
        command = """
                sky6RASCOMTele.SlewToRaDec(""" + str(ra) + "," + str(dec) + """, "cxx");
                """
        print(command)
        output = self.conn._send(command).splitlines()
        print(output)
        time.sleep(0.4)
    
    def rate(self, d_ra, d_dec):
        command = """
                sky6RASCOMTele.SetTracking(1, 0, """ + str(d_ra) + "," + str(d_dec) + """);
                """
        print(command)
        output = self.conn._send(command).splitlines()
        print(output)
        time.sleep(0.1)

   
    def stop(self):
        # Stop tracking
        command = """
                var Out = "";
                sky6RASCOMTele.SetTracking(0, 1, 15, 0);
                """
        output = self.conn._send(command).splitlines()
        print(output)
        time.sleep(1)
        
    def bump(self, dx, dy):
        dx = dx * 1000
        dy = dy * 1000
        dx = max(dx, -999)
        dx = min(dx, 999)
        dy = max(dy, -999)
        dy = min(dy, 999)
        quote = '"'
        
        cmd = ""
        
        if (dy > 4):
            cmd = quote + ":Ms" + str(int(dy)) + "#" + quote
            
        if (dy < -4):
            cmd = quote + ":Mn" + str(int(-dy)) + "#" + quote
        
        if (not(cmd == "")):
            command = """
                var Out = "";
                sky6RASCOMTele.DoCommand(3, """
            command = command + cmd + ")\n"
            print(command)
            output = self.conn._send(command).splitlines()
            print(output)

        cmd1 = ""      
        if (dx > 4):
            cmd1 = quote + ":Me" + str(int(dx)) + "#" + quote
        if (dx < -4):
            cmd1 = quote + ":Mw" + str(int(-dx)) + "#" + quote
        
        if (not(cmd1 == "")):
            command = """
                var Out = "";
                sky6RASCOMTele.DoCommand(3, """
            command = command + cmd1 + ")\n"
            print(command)
            output = self.conn._send(command).splitlines()
            print(output)
       
    def jog(self, dx, dy):
        dx = max(dx, -9.9)
        dx = min(dx, 9.9)
        dy = max(dy, -9.9)
        dy = min(dy, 9.9)
        
        quote = '"'
        
        if (dy > 0):
            cmd = "Jog(" + str(dy) + ',"N"' + ")"
            
        if (dy < 0):
            cmd = "Jog(" + str(dy) + ',"S"' + ")"
        
        if (not(cmd is None)):
            command = """
                var Out = "";
                sky6RASCOMTele."""
            command = command + cmd + "\n"

            print(command)
            output = self.conn._send(command).splitlines()
            print(output)

        if (dx > 0):
            cmd = "Jog(" + str(dx) + ',"E"' + ")"
            
        if (dx < 0):
            cmd = "Jog(" + str(dx) + ',"W"' + ")"
        
        if (not(cmd is None)):
            command = """
                var Out = "";
                sky6RASCOMTele."""
            command = command + cmd + "\n"
            print(command)
            output = self.conn._send(command).splitlines()
            print(output)




