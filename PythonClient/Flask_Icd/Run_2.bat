start /d "C:\terrains\Build" AirSimAssets.exe /flaskPortArg=5001  /unityDronePort=41452
more +1 "%CD%\config.cfg > "%CD%\instance\config.cfg
echo SESSION_COOKIE_PATH=41452 >> "%CD%\instance\config.cfg

 
set FLASK_APP=falskICD
flask run --host=0.0.0.0 --port=5001