from flask import Flask, render_template, jsonify, request
from foodwatch.models import setup_db, Food, Misc
from flask_cors import CORS
from sqlalchemy import Date, cast, inspect
from datetime import date, datetime, timedelta
import pandas as pd
import os
import time


def create_app(dbms="sqlite3", test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if dbms == "sqlite3":
        if test_config:
            database_filename = "database_test.db"
        else:
            database_filename = "database.db"
        project_dir = os.path.dirname(os.path.abspath(__file__))
        database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))
        db = setup_db(app, database_path)
    else:
        database_path = 'postgres://diyqhmcpqznxqh:6bfd76c3b1810ef06e06867d8806f0814b45bea09a3f1aa70f0e1fb81b3c2c4c@ec2-52-207-93-32.compute-1.amazonaws.com:5432/dc2cbh2ac1dp2p'
        db = setup_db(app, database_path)

    CORS(app)

    @app.route("/hap")
    def happy():
        return render_template("test.html")

    @app.route("/")
    def home():
        datalist_name = [el[0] for el in db.session.query(Food.name).distinct().all()]
        extention = ["Brötchen", "Ei", "100g_Wurst", "200g_Wurst"]
        datalist_name.extend(extention)
        return render_template('home.html', datalist_name=datalist_name)

    @app.route("/history")
    def history():
        prev_data = []
        for el in db.session.query(Food).distinct().all():
            el.timestamp_obj = el.timestamp_obj.strftime("%d/%m/%Y %a - %H:%M")
            prev_data.append(convert_sqlalchemy_todict(el))
        return render_template('history.html', prev_data=prev_data)

    @app.route("/misc")
    def misc():
        prev_data = []
        for el in db.session.query(Misc).distinct().all():
            el.timestamp_obj = el.timestamp_obj.strftime("%d/%m/%Y")
            prev_data.append(convert_sqlalchemy_todict(el))
        return render_template('misc.html', prev_data=prev_data)

    @app.route("/analysis")
    def analysis():
        """
        Return the analysis.html with data
        """
        '#1.1.Step: Get all records for Food, Misc'
        df_dict = {}
        for model_obj in [Food, Misc]:
            query = db.session.query(model_obj).all()
            query_result = [convert_sqlalchemy_todict(x) for x in query]
            dict_key = str(model_obj.__table__.name)
            df_dict[dict_key] = pd.DataFrame(query_result)

            '#1.2.Step: Convert timestampe_obj to pandas datetime and round to day'
            df_dict[dict_key]["timestamp_obj"] = pd.to_datetime((df_dict[dict_key]["timestamp_obj"])) \
                .dt.floor('d')

        '#2.Step: Group Foods by day and  reset_index'
        df_dict["food_grouped_reset"] = df_dict["food"].groupby(by=df_dict["food"]['timestamp_obj'].dt.date)\
            .sum() \
            .reset_index()

        '#2.2.Step: Convert timestampe_obj to pandas datetime (g=group;r=reset;t=transformed '
        df_dict["food_grouped_reset"]["timestamp_obj"] = pd.to_datetime(df_dict["food_grouped_reset"]["timestamp_obj"]) \
            .dt.floor('d')

        '#3.1.Step: Merge the dataframe'
        df_merge = pd.merge(df_dict["food_grouped_reset"], df_dict["misc"], on='timestamp_obj', how='outer')
        '#3.2.Step: Convert the data into list so that highchart is able to interpret the data an create the line chart'
        '#3.3.Step: Convert from datetime64 to epoch'
        df_merge["timestamp_obj"] = df_merge["timestamp_obj"].astype("int64") / 1e6
        df_merge = df_merge.dropna()
        data = {}

        for columns in ["amount_steps", "calorie", "amount_weight"]:
            '#3.4.Step: Sort the pd.serie for highchart'
            df_sorted = df_merge[["timestamp_obj", columns]].sort_values(by=['timestamp_obj'])
            data[columns] = df_sorted.to_numpy().tolist()

        return render_template('analysis.html', data=data)

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
        if len(df) != 0:
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

    @app.route("/misc_data", methods=["POST"])
    def misc_data():

        el_json = request.get_json()["data"]
        # Convert from epoch to unix
        misc_mapping = []
        for el in el_json:
            if el["database_id"] == 'database_id':
                "#If row hasn't a existing record in db, a new object will be created an added to the db"
                timestamp_obj = datetime.strptime(el["date"], '%d/%M/%Y')
                timestamp_unix = time.mktime(timestamp_obj.timetuple())
                db.session.add(
                    Misc(timestamp_unix=timestamp_unix, timestamp_obj=timestamp_obj,
                         amount_steps=el["steps"], amount_weight=el["weight"])
                )
                db.session.commit()
            else:
                '#Replace the existing record'
                '# In order to make a bulk update, an array with dict (same key as Misc) need to be created'
                timestamp_obj = datetime.strptime(el["date"], '%d/%M/%Y')
                timestamp_unix = time.mktime(timestamp_obj.timetuple())
                modify_el = {"timestamp_obj": timestamp_obj,
                             "timestamp_unix": timestamp_unix,
                             "amount_steps": el["steps"],
                             "amount_weight": el["weight"],
                             "id": el["database_id"]
                             }
                misc_mapping.append(modify_el)

        db.session.bulk_update_mappings(Misc, misc_mapping)
        db.session.commit()

        return jsonify({
            'success': True,
        }, 204)

    @app.route("/data_today", methods=["POST"])
    def post_data_today():

        el = request.get_json()["data"]
        # Convert from epoch to unix
        el["timestamp_unix"] = round(int(el["timestamp_epoch"]) / 1000)
        del (el["timestamp_epoch"])
        '#Check for double then inject'
        if db.session.query(Food).filter_by(timestamp_unix=el["timestamp_unix"]).count() < 1:
            el["timestamp_obj"] = datetime.utcfromtimestamp(el["timestamp_unix"])
            f1 = Food(**el)
            db.session.add(f1)
            db.session.commit()

        return jsonify({
            'success': True,
        }, 204)

    @app.route("/data_today", methods=["Delete"])
    def delete_data_today():

        db_id = request.get_json()["data"]
        # Convert from epoch to unix
        db.session.query(Food).filter_by(id=db_id).delete()
        db.session.commit()
        return jsonify({
            'success': True,
        }, 204)

    def convert_sqlalchemy_todict(obj):
        """
        Converts a sqlalchemy oject to a dict
        :param obj:
        :return:
        """
        return {c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs}

    return app


# Check if app runs on local computer:
os.system('uname -a > tmp')
if open('tmp', 'r').read()[:24] == "Linux wlg1fe-HP-Pavilion":
    app = create_app(dbms="sqlite3")
else:
    app = create_app(dbms="mysql")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
