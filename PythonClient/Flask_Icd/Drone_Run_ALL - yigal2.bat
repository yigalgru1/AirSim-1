start /d "C:\terrains\Build" AirSimAssets.exe /flaskPortArg=5001  /unityDronePort=41452

more +1 C:\Git\AirSim-1\PythonClient\Flask_Icd\instance\config.cfg > C:\Git\AirSim-1\PythonClient\Flask_Icd\instance\config.cfg
echo SESSION_COOKIE_PATH=41452 >> C:\Git\AirSim-1\PythonClient\Flask_Icd\instance\config.cfg

start /d "C:\Git\AirSim-1\PythonClient\Flask_Icd" 
set FLASK_APP=falskICD
flask run --host=0.0.0.0 --port=5001