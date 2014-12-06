import tornado.ioloop
import tornado.web
import serial
import utils
import sys
import glob
from pymongo import MongoClient
import pymongo
from bson.json_util import dumps
import time
import json

client_sync = MongoClient('localhost', 27017)["db_home"]


class Serial():

    buffer = ""
    serial = None
    last_port = None

    def __init__(self):
        self.connect()

    def connect(self):
        if self.last_port is not None:
            self.serial = self._connect_to_port(self.last_port)
        else:
            ports = self.scan_ports()
            for port in ports:
                self.serial = self._connect_to_port(port)
                if self._detect_stream():
                    self.last_port = port
                    break

    def _connect_to_port(self, port):
            try:
                serial_connection = serial.Serial(port, 115200, timeout=0)
                return serial_connection
            except (OSError, serial.SerialException):
                return None

    def read(self):
        try:
            if self.serial and self.serial.isOpen():
                self.buffer += self.serial.readall()
                self.buffer, frames = utils.find_all_frame(self.buffer)
                for frame in frames:
                    frame["timestamp"] = int(time.time())
                    client_sync.floor_heat.insert(frame)

            else:
                self.connect()

        except (serial.SerialException, OSError):
            self.connect()

    def call(self, func, *args):
        line = "%s(%s)" % (func, ",".join(args))
        self.serial.write(line)

    def select(self):
        self.read()

    def scan_ports(self):
        """Lists serial ports

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of available serial ports
        """
        if sys.platform.startswith('win'):
            ports = ['COM' + str(i + 1) for i in range(256)]

        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this is to exclude your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')

        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')

        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

ser = Serial()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class CurrentStateHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'application/javascript')
        state = client_sync.floor_heat.find_one(sort=[("timestamp", pymongo.DESCENDING)])
        del state["_id"]
        self.write(json.dumps(state))


class HistoryHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'application/javascript')
        state = client_sync.floor_heat.find({}, {'_id': False})
        # del state["_id"]
        self.write(dumps(state))


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/get_state", CurrentStateHandler),
    (r"/get_history", HistoryHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
])


if __name__ == "__main__":
    application.listen(8888)
    loop = tornado.ioloop.IOLoop.instance()
    period_cbk = tornado.ioloop.PeriodicCallback(ser.select, 500, loop)
    period_cbk.start()
    loop.start()