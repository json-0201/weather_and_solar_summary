# website is a package now, (".__init__" is optional)
from website import create_app
app = create_app()

# only if this file is run (app.py)
if __name__ == "__main__":
    app.run(debug=True)