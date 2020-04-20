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

    @app.route("/")
    def home():
        datalist_name = [el[0] for el in db.session.query(Food.name).distinct().all()]
        extention = ["Brötchen", "Ei", "100g_Wurst", "200g_Wurst"]
        datalist_name.extend(extention)
        rank_dict = home_rank()
        return render_template('home.html', datalist_name=datalist_name,
                               current = rank_dict["current"],
                               best_days = rank_dict["best"],
                               worst_days= rank_dict["worst"])

    @app.route("/history")
    def history():
        prev_data = []
        for el in db.session.query(Food).distinct().order_by(Food.timestamp_obj.desc()).all():
            el.timestamp_obj = el.timestamp_obj.strftime("%d/%m/%Y %a - %H:%M")
            prev_data.append(convert_sqlalchemy_todict(el))
        return render_template('history.html', prev_data=prev_data)

    @app.route("/misc")
    def misc():
        prev_data = []
        '#Query all data from Misc and sort by date (desc)'
        for el in db.session.query(Misc).order_by(Misc.timestamp_obj.desc()).all():
            el.timestamp_obj = el.timestamp_obj.strftime("%d/%m/%Y")
            prev_data.append(convert_sqlalchemy_todict(el))
        return render_template('misc.html', prev_data=prev_data)

    @app.route("/analysis")
    def analysis():
        """
        Return the analysis.html with data
        """
        df_merge = merge_food_misc()

        '#1.1.Step: Convert from datetime64 to epoch'
        df_merge["timestamp_obj"] = df_merge["timestamp_obj"].astype("int64") / 1e6

        df_merge["timestamp_obj"] = pd.to_datetime((df_merge["timestamp_obj"]*1e6))
        df_merge["timestamp_str"] = df_merge["timestamp_obj"].dt.strftime('%d/%m/%Y')

        '#2.1Step: Create a new column which is the ratio in hecto (calorie per steps)'
        df_merge["ratio_raw"] = ((df_merge["calorie"]/df_merge["amount_steps"])*100).round(2)
        df_merge["ratio"] = df_merge["ratio_raw"].round(2)
        '#2.3.Step: Calculate the current diff. Shift(-1) is there to shift row by one '
        df_merge["diff"]=df_merge["amount_weight"].diff().shift(-1).round(2)

        '#2.Step: Convert the data into list so that highchart is able to interpret the data an create the line chart'
        df_merge["timestamp_ep"] = df_merge["timestamp_obj"].astype("int64") / 1e6
        '#2.1.Step: Replace NAN in the column diff because for the current day there is no diff'
        df_merge['diff'] = df_merge['diff'].fillna(0)
        '#2.1.Step: Pre-process extrem points for ratio'
        df_merge.ratio.loc[df_merge.ratio>15]=15
        data_chart = {}
        for columns in ["amount_steps", "calorie", "amount_weight","diff","ratio"]:
            '#1.4.Step: Sort the pd.serie for highchart'
            df_sorted = df_merge[["timestamp_ep", columns]].sort_values(by=['timestamp_ep'])
            data_chart[columns] = df_sorted.to_numpy().tolist()
        list_sorted = list(df_merge.sort_values(by=['timestamp_ep'],ascending=False ).T.to_dict().values())

        return render_template('analysis.html', data_chart=data_chart,list_sorted=list_sorted)

    def home_rank():
        '''
        Calculates the figure for the table rank on the home.html.

        :return (dict): The return value consist out of top 3, worst 3 and current value
        '''
        rank_dict={}
        '#1.Step: Get all data'
        df_merge_raw = merge_food_misc()

        '#2.1Step: Create a new column which is the ratio in hecto (calorie per steps)'
        df_merge_raw["ratio_raw"] = (df_merge_raw["calorie"]/df_merge_raw["amount_steps"])*100
        df_merge_raw["ratio"] = df_merge_raw["ratio_raw"].round(2)
        '#2.3.Step: Calculate the current diff. Shift(-1) is there to shift row by one '
        df_merge_raw["diff"]=df_merge_raw["amount_weight"].diff().shift(-1).round(2)

        '#2.2.Step: Exclude all day where calorie is below 1200'
        df_merge = df_merge_raw.loc[(df_merge_raw["calorie"]>1200)]
        '#4.Step: Sort max'
        df_sorted = df_merge.sort_values(by="ratio").reset_index(drop=True)
        '#4.1.Step: Get the current day'
        today = df_merge_raw.sort_values(by="timestamp_obj", ascending=False).reset_index().iloc[0, 1]
        '#4.3.Step: Check if the value is under 1200, if so then df_merge_raw need to be used'
        current_cal  = df_merge_raw.loc[df_merge_raw["timestamp_obj"] == today].reset_index().loc[0, "calorie"]

        if current_cal<1200:
            df_current = df_merge_raw.loc[df_merge_raw["timestamp_obj"] == today].reset_index()
            df_current["index"]=99
        else:
            today = df_merge.sort_values(by="timestamp_obj", ascending=False).reset_index().iloc[0, 1]
            '#4.2.Step: Select, and reset index to get the current rank as colum'
            df_current = df_sorted.loc[(df_sorted.timestamp_obj == today)].reset_index()
        df_current["timestamp_str"] = df_current["timestamp_obj"].dt.strftime('%a - %d/%m/%Y')
        '#4.3.Step: Convert to dict'
        rank_dict["current"]= df_current.T.to_dict()
        '#5.1.Step: Get the best and worst days, exclude the current day'
        df_ex = df_sorted.loc[(df_sorted.timestamp_obj != today)].reset_index()
        df_ex["timestamp_str"] = df_ex["timestamp_obj"].dt.strftime('%a - %d/%m/%Y')
        rank_dict["best"] = df_ex.iloc[0:3, ].T.to_dict()
        '5.2.Step: .iloc[::-1] is to reverse the order'
        rank_dict["worst"] = df_ex.tail(3).iloc[::-1].reset_index().T.to_dict()

        return rank_dict


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
    @app.route("/misc", methods=["Delete"])
    def delete_misc():

        db_id = request.get_json()["data"]
        # Convert from epoch to unix
        db.session.query(Misc).filter_by(id=db_id).delete()
        db.session.commit()
        return jsonify({
            'success': True,
        }, 204)
    @app.route("/misc_data", methods=["POST"])
    def misc_data():

        el_json = request.get_json()["data"]
        # Convert from epoch to unix
        misc_mapping = []
        for el in el_json:
            if el["database_id"] == 'database_id':
                "#If row hasn't a existing record in db, a new object will be created an added to the db"
                timestamp_obj = datetime.strptime(el["date"], '%d/%m/%Y')
                timestamp_unix = time.mktime(timestamp_obj.timetuple())
                db.session.add(
                    Misc(timestamp_unix=timestamp_unix, timestamp_obj=timestamp_obj,
                         amount_steps=el["steps"], amount_weight=el["weight"])
                )
                db.session.commit()
            else:
                '#Replace the existing record'
                '# In order to make a bulk update, an array with dict (same key as Misc) need to be created'
                timestamp_obj = datetime.strptime(el["date"], '%d/%m/%Y')
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

    def merge_food_misc():
        '''
        Merge all Food and Misc records to one dataframe
        :return (pandas.DataFrame): Contains all Food ans Misc records
        '''
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
        df_merge = pd.merge(df_dict["food_grouped_reset"], df_dict["misc"], on='timestamp_obj', how='inner')
        df_merge = df_merge.dropna()
        return df_merge

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
