from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route("/")
def home():
    return send_from_directory(".", "dashb.html")

@app.route("/os1")
def os1():
    return send_from_directory(".", "os1.html")

@app.route("/os2")
def os2():
    return send_from_directory(".", "os2.html")

@app.route("/dashb")
def dashb():
    return send_from_directory(".", "dashb.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
