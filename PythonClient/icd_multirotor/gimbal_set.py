import setup_path 
import airsim
import time
import pprint
import os

class Gimbal:
      def __init__(self, initYaw, initPitch, initRoll,port):
          self.initYaw = initYaw
          self.initPitch = initPitch
          self.initRoll = initRoll
          self.port = port

      def start(self):
          client = airsim.VehicleClient('',self.port)
          client.confirmConnection()
          client.simSetCameraOrientation("0", airsim.to_quaternion(self.initPitch ,self.initRoll, self.initYaw))

          return "complit"



