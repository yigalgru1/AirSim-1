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
          print("1111111111111111")
          client.simSetCameraOrientation("0", airsim.to_quaternion(0.261799 *3, 0, 0))
          print("22222222222222222")

          return "complit"



