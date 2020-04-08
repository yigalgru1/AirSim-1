start /d "C:\terrains\Build" AirSimAssets.exe /flaskPortArg=5000  /unityDronePort=41451
more +1 "%CD%\config.cfg > "%CD%\instance\config.cfg
echo SESSION_COOKIE_PATH=41451 >> "%CD%\instance\config.cfg

 
set FLASK_APP=falskICD
flask run --host=0.0.0.0 --port=5000

pause