import tornado.ioloop
import tornado.web
import serial
import utils
import motor
from pymongo import MongoClient
import pymongo
from bson.json_util import dumps
import time
import json

SERIAL = '/dev/tty.usbmodem1451'
# SERIAL = '/dev/tty.usbserial-A4006WH4'

client = motor.MotorClient()
client_sync = MongoClient('localhost', 27017)["db_home"]

class Serial():
    start_frame = "<SOF>"
    end_frame = "<EOF>"
    buffer = ""
    serial = None
    def __init__(self):
        self.connect()

    def connect(self):
        try:
            self.serial = serial.Serial(SERIAL, 115200, timeout=0)
        except (OSError,):
            print("cannot connect")


    def read(self):
        try:
            if self.serial and self.serial.isOpen():
                print(self.serial.read())
                self.buffer += self.serial.readall()
                self.buffer, frames = utils.find_all_frame(self.buffer)
                for frame in frames:
                    frame["timestamp"] = int(time.time())
                    print(frame)
                    client_sync.floor_heat.insert(frame)
            else:
                self.connect()
        except (serial.SerialException,):
            pass

    def call(self, func, *args):
        line = "%s(%s)" % (func, ",".join(args))
        self.serial.write(line)


ser = Serial()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

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
    (r"/call", MainHandler),
    (r"/get_state", CurrentStateHandler),
    (r"/get_history", HistoryHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
])

def periodic():
    ser.read()

if __name__ == "__main__":
    application.listen(8888)
    loop = tornado.ioloop.IOLoop.instance()
    period_cbk = tornado.ioloop.PeriodicCallback(periodic, 1000, loop)
    period_cbk.start()
    loop.start()