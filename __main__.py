import webbrowser

from app import app
from visualisation import layout
import callbacks


if __name__ == '__main__':
	app.layout = layout
	webbrowser.open('http://127.0.0.1:8050/')
	app.run_server(debug=True)
