from flask import Flask,render_template, jsonify,request
from models import setup_db,Food
import os
from flask_cors import CORS
from sqlalchemy import Date, cast, inspect
from datetime import date,datetime, timedelta
import pandas as pd


def create_app(dbms="sql", test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if dbms == "sql":
        if test_config:
            database_filename = "database_test.db"
        else:
            database_filename = "database.db"
        project_dir = os.path.dirname(os.path.abspath(__file__))
        database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))
        db = setup_db(app, database_path)
    else:
        database_name = "watchfood"
        database_path = 'postgresql://root:admin@localhost:3306/' + database_name
        db = setup_db(app, database_path)
    CORS(app)

    @app.route("/")
    def home():
        datalist_name = [el[0] for el in db.session.query(Food.name).distinct().all()]
        extention=["Brötchen", "Ei", "100g_Wurst", "200g_Wurst"]
        datalist_name.extend(extention)
        return render_template('home.html',datalist_name=datalist_name)

    @app.route("/history")
    def history():
        return render_template('history.html')

    @app.route("/analysis")
    def analysis():
        return render_template('analysis.html')

    @app.route("/data_today", methods=["GET"])
    def get_data_today():
        '#1.Step: Get all records for the current day'
        today = date.today()
        yesterday = today - timedelta(days=1)
        query = db.session.query(Food).filter(Food.timestamp_obj > today).all()
        query_result = [convert_sqlalchemy_todict(x) for x in query]
        '#2.Step: Get the current sum of the day'
        df = pd.DataFrame(query_result)
        '#2.1.Step: Check if DataFrame is empty'
        if len(df)!=0:
            '#2.1.Step: Convert column calorie to int'
            df['calorie'] = pd.to_numeric(df['calorie'], errors='coerce')
            total_sum = str(df['calorie'].sum())
        else:
            total_sum = 0
        return jsonify({
            'success': True,
            'food': query_result,
            'total_sum_today': total_sum
        }, 200)


    @app.route("/data_today", methods=["POST"])
    def post_data_today():

        el = request.get_json()["data"]
        #Convert from epoch to unix
        el["timestamp_unix"] = round(int(el["timestamp_epoch"])/1000)
        del(el["timestamp_epoch"])
        '#Check for double then inject'
        if db.session.query(Food).filter_by(timestamp_unix=el["timestamp_unix"]).count()<1:
            el["timestamp_obj"] = datetime.utcfromtimestamp(el["timestamp_unix"])
            f1=Food(**el)
            db.session.add(f1)
            db.session.commit()

        return jsonify({
            'success': True,
        }, 244)


    def convert_sqlalchemy_todict(obj):
        """
        Converts a sqlalchemy oject to a dict
        :param obj:
        :return:
        """
        return {c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs}





    return app

app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)