#!/usr/bin/env python

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from base64 import b64decode
from rpc_commands import *
import ConfigParser
import argparse
import xmlrpclib



# Server definition

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

    def authenticate(self, headers):
        auth = headers.get('Authorization') 
        try:
            (basic, _, encoded) = headers.get('Authorization').partition(' ')
        except:
            return 1        
        else:
            # Client authentication
            (basic, _, encoded) = headers.get('Authorization').partition(' ')
            assert basic == 'Basic', 'Only basic authentication supported'
            #    Encoded portion of the header is a string
            #    Need to convert to bytestring
            encodedByteString = encoded.encode()
            #    Decode Base64 byte String to a decoded Byte String
            decodedBytes = b64decode(encodedByteString)
            #    Convert from byte string to a regular String
            decodedString = decodedBytes.decode()
            #    Get the username and password from the string
            (username, _, password) = decodedString.partition(':')
            #    Check that username and password match internal global dictionary
            config = ConfigParser.ConfigParser()
            config.read(expanduser("~") + "/" + ".silme/silme.conf")
            rpc_user = config.get('server', 'username')
            rpc_pass = config.get('server', 'password')
            
            if username == rpc_user and password == rpc_pass:                
                return 1
            else:
                return 0


    def parse_request(self):        
        if SimpleXMLRPCRequestHandler.parse_request(self):
            # next we authenticate
            if self.authenticate(self.headers):
                return True
            else:
                # if authentication fails, tell the client
                self.send_error(401, 'Authentication failed')
        return False
        

class MyServer(SimpleXMLRPCServer):
    def __init__(self, bind_address, bind_port):
        # Create server
        self.server = SimpleXMLRPCServer((bind_address, bind_port), requestHandler=RequestHandler)
        self.server.register_introspection_functions()
        self.server.register_function(pow)
        self.server.register_function(lambda: os.getpid(), 'getpid')
        self.server.register_introspection_functions()
        self.server.register_function(self.server_close, 'stop')
        #blockchain 
        self.server.register_function(GetBestHeight, 'getbestheight')
        self.server.register_function(GetBestHash, 'getbesthash')
        self.server.register_function(GetDifficulty, 'getdifficulty')
        self.server.register_function(NetHashRate, 'nethashrate')
        self.server.register_function(GetInfo, 'getinfo')
        #wallet
        self.server.register_function(GetMyAddresses, 'getmyaddresses')
        self.server.register_function(GetNewAddress, 'getnewaddress')
        self.server.register_function(GetBalance, 'getbalance')
        #mining 
        self.server.register_function(MemCount, 'mempoolcount')
        self.server.register_function(GetTarget, 'gettarget')
        #
        self.server.register_function(Version, 'version')
        return
    
    def serve_forever(self):
        self.server.serve_forever()
        
    def server_close(self):
        self.server.server_close()
        return 1


def run_rpc_command(params, rpc_port):
    cmd = params[0]
    rpc_user = config.get('server', 'username')
    rpc_pass = config.get('server', 'password')
    server = xmlrpclib.ServerProxy('http://%s:%s@localhost:%s' %(rpc_user, rpc_pass, rpc_port))
    func = getattr(server, cmd)
    r = func(*params[1:])
    print json.dumps(r, indent=4, sort_keys=True)
        

if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read(expanduser("~") + "/" + ".silme/silme.conf")

    rpc_host = config.get('server', 'host')
    rpc_port = config.get('server', 'rpc_port')

    parser = argparse.ArgumentParser()
    parser.add_argument('command', nargs='*', default=[], help='send a command to the server')
    args = parser.parse_args()

    if len(args.command) >= 1:
        try:
            run_rpc_command(args.command, rpc_port)
        except socket.error:
            print "server not running"
            sys.exit(1)
        sys.exit(0)

    try:
        run_rpc_command(['getpid'], rpc_port)
        is_running = True
    except socket.error:
        is_running = False

    if is_running:
        print "server already running"
        sys.exit(1)

    server = MyServer(rpc_host, int(rpc_port))
    server.serve_forever()
