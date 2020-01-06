from flask import Flask,render_template




def create():
    app = Flask(__name__)

    @app.route("/")
    def home():
        return render_template('home.html')

    @app.route("/history")
    def history():
        return render_template('history.html')

    @app.route("/analysis")
    def analysis():
        return render_template('analysis.html')

    return app




app = create()


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)