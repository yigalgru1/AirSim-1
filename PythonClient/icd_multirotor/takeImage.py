import setup_path
import airsim
import time
import tempfile
import os
import base64


print("take image")
client = airsim.MultirotorClient('')
client.confirmConnection()
idx = 0
tmp_dir = os.path.join(tempfile.gettempdir(), "airsim_drone")

while True:
    rawImage = client.simGetImage("0", airsim.ImageType.Scene)
    print("take image")
    idx = idx+1
    print(idx)
    filename = os.path.join(tmp_dir, str(idx))
    new_image_string = base64.b64encode(rawImage).decode("utf-8")
    time.sleep(0.1)



