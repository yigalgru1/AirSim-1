import setup_path 
import airsim


class Fov:
    
    def __init__(self, port):
        self.port = port
      
    
    def start(self):
        client = airsim.MultirotorClient('',self.port)
        client.confirmConnection()
        print("fov requst") 
        dddds = client.getMultirotorState()
        dddd = client.getMultirotorFovCoordinateState()
        print(dddd)
        return True
