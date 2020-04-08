import setup_path 
import airsim


class HotPoint:
      def __init__(self, initX, initY, initZ,port):
          self.initX = initX
          self.initY = initY
          self.initZ = initZ
          self.port = port

      def start(self):
          print("hot Point")
          client = airsim.MultirotorClient('',self.port)
        #  client.confirmConnection()
        #   client.enableApiControl(True)
        #   client.armDisarm(True) 
          client.moveToPositionAsync(float(self.initX),float(self.initY), -1 * float(self.initZ), 5).join()

          return "complit"