from api import create_app

app = create_app()

if __name__ == '__main__': # Only if we run this file, not if it's imported
    app.run(debug=True) # If I make a change, it will rerun.