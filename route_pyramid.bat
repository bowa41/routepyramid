REM Activate your virtual environment
call C:\Users\Jordan\PycharmProjects\routepyramid\.venv\Scripts\activate.bat

REM Start your Flask app with Waitress in a new window
start cmd /k "python C:\Users\Jordan\PycharmProjects\routepyramid\main.py"

REM Start Ngrok in another window
start cmd /k "ngrok http 5000 --url https://vaguely-central-flounder.ngrok-free.app"


echo Both Flask app and Ngrok have been started.
pausengrok 