from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    Hello, Everyone! My first project is running.
    <br>
    Hello, Everyone! My application is now updated through Jenkins CI/CD!
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
