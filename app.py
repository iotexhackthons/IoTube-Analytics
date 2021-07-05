# Import app
from Dashboard.base import app
from Dashboard.server import server

# Run app on server
if __name__ == '__main__':
    app.run_server()