from flask import Flask, render_template, request
from main import *

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/busInfo")
def busInfo():
    postcode = request.args.get('postcode')

    BusTimes = main(postcode)
    postcode = postcode.upper()

    return render_template('info.html', postcode=postcode, listBusTimes=BusTimes)


if __name__ == "__main__":
    app.run()
