from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from sqlalchemy import Date, cast, inspect
from datetime import date, datetime, timedelta
from flask import send_from_directory
import pandas as pd
import numpy as np
import foodwatch.streak as streak
import os
import time
import json
from flask_migrate import Migrate
from foodwatch.helper import try_str_float
from foodwatch.auth import requires_auth
from foodwatch.own_abort_exception import abort
from foodwatch.models import setup_db, Food, Misc, Home_misc

def create_app(dbms="sqlite3", test_config=None):
    # create and configure the app
    #================
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
        if "jwt_foodwatch" in os.environ.keys():
            database_path = os.environ["database_path"]
        else:
            try:
                with open('foodwatch/env.json', 'r') as env_file:
                    env_dict = json.load(env_file)
                    database_path = env_dict["database_path"]
            except FileNotFoundError:
                with open('env.json', 'r') as env_file:
                    env_dict = json.load(env_file)
                    database_path = env_dict["database_path"]

        db = setup_db(app, database_path)

    CORS(app)

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                                   mimetype='image/vnd.microsoft.icon')
    @app.route("/")
    def login():
        return render_template('login.html')

    @app.route("/home")
    def home():
        df = pd.read_sql_table("food", db.session.bind)
        df_groupby = df.groupby(by=df["name"]).mean()
        df_mean = df_groupby.reset_index()
        datalist_name = df_mean[["name", "calorie"]].values

        rank_dict = home_rank()
        total_calories = db.session.query(Home_misc.total_calories).first()
        HM = db.session.query(Home_misc).first()
        '#2.1.Step: Convert bulk_items string into dict'
        bulk_items = db.session.query(Home_misc.bulk_items).first()[0]
        str_bulk_items = json.loads(bulk_items)["0"]
        return render_template('home.html', datalist_name=datalist_name,
                               current = rank_dict["current"],
                               total_calories=total_calories,
                               bulk_items=str_bulk_items)

    #<path:path> is just for safe view "
    @app.route("/histor<path:path>")
    def history(path):
        prev_data = []
        for el in db.session.query(Food).distinct().order_by(Food.timestamp_obj.desc()).all():
            el.timestamp_obj = el.timestamp_obj.strftime("%d/%m/%Y %a - %H:%M")
            prev_data.append(convert_sqlalchemy_todict(el))
        return render_template('history.html', prev_data=prev_data)
    @app.route("/bulk_items/<string:slot>",methods=["GET"])
    def get_bulk_items(slot):
        """
        Get the bulk_items of a specific slot
        :param slot:
        :return:
        """
        '#1.Step: Get the bulk_items'
        bulk_items = db.session.query(Home_misc.bulk_items).first()[0]
        '#2.1.Step: Convert string into dict'
        dict_bulk_items = json.loads(bulk_items)

        '#2.2.Step: Check if slot is in keys'
        if slot in dict_bulk_items.keys():
            '#2.3.Step: Get the items of the slot'
            bulk_slot_items = dict_bulk_items[slot]
        else:
            bulk_slot_items = "No items saved to this slot"

        return jsonify({
            'success': True,
            'bulk_slot_items': bulk_slot_items,
        }, 200)


    @app.route("/bulk_items",methods=["POST"])
    @requires_auth('post:bulk_items')
    def post_bulk_items(payload):
        """
        Get the bulk_items of a specific slot
        :param slot:
        :return:
        """
        '#1.Step: Get the bulk_items and bulk_slot'
        bulk_items_front = request.get_json()["bulk_items"]
        bulk_slot = request.get_json()["bulk_slot"]
        HM = db.session.query(Home_misc).first()
        # "2.1.Step: Check if result is empty"
        # bulk_items1={"0":"""
        #                          Proteinpulver_25_g,90
        #                          Leinsamen_20g,106
        #                          Apfelkuchen_Hälfte,50
        #                          Hafer_50_g,180
        #                         """,
        #             "1":"""
        #                          Proteinpulver_25_g,90
        #                          Leinsamen_20g,106
        #                          Apfelkuchen_Hälfte,50
        #                          Hafer_50_g,180
        #                         """}
        # HM.bulk_items=json.dumps(bulk_items1)
        # db.session.commit()
        '#2.2.Step: Convert string into dict'
        dict_bulk_items = json.loads(HM.bulk_items)
        '#2.2.Step: Replace the bulk_items of the slot'
        dict_bulk_items[bulk_slot] = bulk_items_front
        '#2.3.Step: Stringly the dict and save it to the database'
        HM.bulk_items = json.dumps(dict_bulk_items)
        db.session.commit()
        return jsonify({
            'success': True,
            'msg': "bulk items successfuly saved",
        }, 200)

    @app.route("/misc")
    def misc():
        prev_data = []
        '#Query all data from Misc and sort by date (desc)'
        for el in db.session.query(Misc).order_by(Misc.timestamp_obj.desc()).all():
            el.timestamp_obj = el.timestamp_obj.strftime("%d/%m/%Y")
            prev_data.append(convert_sqlalchemy_todict(el))
        return render_template('misc.html', prev_data=prev_data)

    @app.route("/analysi<path:path>")
    def analysis(path):
        """
        Return the analysis.html with data

        """

        df_merge = merge_food_misc(db)

        '#1.1.Step: Convert from datetime64 to epoch'
        df_merge["timestamp_obj"] = df_merge["timestamp_obj"].astype("int64") / 1e6

        df_merge["timestamp_obj"] = pd.to_datetime((df_merge["timestamp_obj"]*1e6))
        df_merge["timestamp_str"] = df_merge["timestamp_obj"].dt.strftime('%d/%m/%y')

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
        df_merge_raw = merge_food_misc(db)

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
        query = db.session.query(Food).filter(Food.timestamp_obj > today)
        query_sort = query.order_by(Food.timestamp_obj.asc()).all()
        query_result = [convert_sqlalchemy_todict(x) for x in query_sort]
        '#2.Step: Get the current sum of the day'
        df = pd.DataFrame(query_result)
        '#2.1.Step: Check if DataFrame is empty'

        if len(df) != 0:
            '#2.1.Step: Convert column calorie to int'
            df['calorie'] = pd.to_numeric(df['calorie'], errors='coerce')
            total_sum = str(df['calorie'].sum())
        else:
            total_sum = 0
        total_calories_plan = db.session.query(Home_misc.total_calories).first()
        return jsonify({
            'success': True,
            'food': query_result,
            'total_sum_today': total_sum,
            'total_calories_plan':total_calories_plan[0]
        }, 200)

    @app.route("/misc", methods=["Delete"])
    @requires_auth('delete')
    def delete_misc(payload):

        db_id = request.get_json()["data"]
        # Convert from epoch to unix
        db.session.query(Misc).filter_by(id=db_id).delete()
        db.session.commit()
        return jsonify({
            'success': True,
        }, 204)

    @app.route("/all_data/<table>/<keyword>")
    def get_all_data(table,keyword):
        """
        Get all data of a specific field
        :return:
        """
        '#1.Step: Get the data as df'
        df = pd.read_sql_table(table, db.session.bind)
        '#2.Step: Sort the data for highchart'
        data_sorted = df.sort_values(by=['timestamp_unix'])
        '#3.Step: Delete the zeros'
        data_non_zero = data_sorted[data_sorted["amount_weight"] != 0]
        '#4.Step: Multipy by 1000 because highchart except epoch not unix'
        data_non_zero["timestamp_unix"] = data_non_zero["timestamp_unix"] * 1000
        data_numpy = data_non_zero[['timestamp_unix', keyword]].values
        data_list = data_numpy.tolist()

        return jsonify({
            'success': True,
            'data':data_list
        }, 204)


    @app.route("/misc_data", methods=["POST"])
    @requires_auth('post')
    def misc_data(payload):
        """
        Save all data from the tab misc to the database
        :param payload:
        :return:
        """
        el_json = request.get_json()["data"]
        # Convert from epoch to unix
        misc_mapping = []
        for el in el_json:
            if (el["database_id"] == 'database_id') and \
                try_str_float(el["weight"]) and try_str_float(el["steps"]) :
                "#If row hasn't a existing record in db, a new object will be created an added to the db"
                timestamp_obj = datetime.strptime(el["date"], '%d/%m/%Y')
                timestamp_unix = time.mktime(timestamp_obj.timetuple())
                db.session.add(
                    Misc(timestamp_unix=timestamp_unix, timestamp_obj=timestamp_obj,
                         amount_steps=el["steps"], amount_weight=el["weight"])
                )
                db.session.commit()
            elif try_str_float(el["weight"]) and try_str_float(el["steps"]):
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
            else:
                abort(400)
        db.session.bulk_update_mappings(Misc, misc_mapping)
        db.session.commit()

        return jsonify({
            'success': True,
        }, 204)

    @app.route("/data_today", methods=["POST"])
    @requires_auth('post')
    def post_data_today(payload):
        """
        Save new added food rows to the data base and also the planed total cal amount for the day
        :return:
        """

        '#1.Step: Get all the data'
        el = request.get_json()["data"]
        '#1.1.Step: Tests if name,calorie is in fetch'
        if "name" in el.keys() and "calorie" in el.keys():
            '#2.1.Step: If name is empty or calorie is NaN => return!!'
            if el["name"]==None or try_str_float(el["calorie"])==False:
                abort(400)
            '#2.2.Step: Overwrite the current total cal amount'
            if el["total_calorie_plan"]!= None:
                hm1 = db.session.query(Home_misc).first()
                hm1.total_calories = el.pop("total_calorie_plan")
            else:
                '#If empty it will not overwrite the excising value'
                el.pop("total_calorie_plan")
            '#3.Step: Save the new food row to the database'
            # Convert from epoch to unix
            el["timestamp_unix"] = round(int(el["timestamp_epoch"]) / 1000)
            del (el["timestamp_epoch"])
            el["timestamp_obj"] = datetime.utcfromtimestamp(el["timestamp_unix"])
            f1 = Food(**el)
            db.session.add(f1)
            db.session.commit()
            return jsonify({
                'success': True,
            }, 204)
        else:
            abort(400)

    @app.route("/data_today", methods=["Delete"])
    @requires_auth('delete')
    def delete_data_today(payload):

        db_id = request.get_json()["data"]
        # Convert from epoch to unix
        db.session.query(Food).filter_by(id=db_id).delete()
        db.session.commit()
        return jsonify({
            'success': True,
        }, 204)

    def merge_food_misc(db):
        '''
        Merge all Food and Misc records to one dataframe
        :args:
            db(<class 'flask_sqlalchemy.SQLAlchemy'>): db is the database which contains the data
        :return (pandas.DataFrame): Contains all Food ans Misc records
        '''

        '#1.1.Step: Get all records for Food, Misc'
        df_dict = {}

        for model_obj in [Food, Misc]:
            query = db.session.query(model_obj).all()
            if db.session.query(model_obj).count()==0:
                return "No data in db"
            query_result = [convert_sqlalchemy_todict(x) for x in query]
            dict_key = str(model_obj.__table__.name)
            df_dict[dict_key] = pd.DataFrame(query_result)

            '#1.2.Step: Convert timestampe_obj to pandas datetime and round to day'
            df_dict[dict_key]["timestamp_obj"] = pd.to_datetime((df_dict[dict_key]["timestamp_obj"])) \
                .dt.floor('d')

        '#2.Step: Group Foods by day and  reset_index and remove all rows with string NaN'
        df_dict["food_nan"] = df_dict["food"][(df_dict["food"]["calorie"]!="NaN")]
        df_dict["food_nan"]["calorie"] = df_dict["food_nan"]["calorie"].astype("int64")
        df_dict["food_grouped_reset"] = df_dict["food_nan"].groupby(by=df_dict["food_nan"]['timestamp_obj'].dt.date)\
            .sum() \
            .reset_index()

        '#2.2.Step: Convert timestampe_obj to pandas datetime (g=group;r=reset;t=transformed '
        df_dict["food_grouped_reset"]["timestamp_obj"] = pd.to_datetime(df_dict["food_grouped_reset"]["timestamp_obj"]) \
            .dt.floor('d')

        '#3.1.Step: Merge the dataframe'
        df_merge = pd.merge(df_dict["food_grouped_reset"], df_dict["misc"], on='timestamp_obj', how='inner')
        df_merge = df_merge.dropna()

        return df_merge

    @app.route("/misc_weigth", methods=["GET"])
    def get_weigth_statistic():
        """
        Get the statics information about weight from db. (Avg. Mean for 7,14,30 days)
        :return:
        """
        '#1.Step: Read data from database'

        df = pd.read_sql_table("misc", db.session.bind)
        '#2.1.Step: Convert column amount_weight to float and column date to datetime obj'
        df['amount_weight'] = df['amount_weight'].astype(float)
        df["timestamp_obj"] = pd.to_datetime(df["timestamp_obj"], format='%Y-%m/%d %h:%m:%s')
        '#3.Step: Sort by day and reset index'
        df_weight_sorted = df.sort_values(by=['timestamp_obj'], ascending=False)
        df_weight_sorted = df_weight_sorted.reset_index(drop=True)
        '#4.Step: Calculate the statistics'
        statistics_dict = {'success': True}
        for day_range in [7,14,30]:
            statistics_dict[f'weight_{day_range}_max'] = df_weight_sorted.loc[:day_range].\
                                                         describe().loc["max", "amount_weight"]
            statistics_dict[f'weight_{day_range}_min'] = df_weight_sorted.loc[:day_range].\
                                                         describe().loc["min", "amount_weight"]
            statistics_dict[f'weight_{day_range}_mean'] = round(df_weight_sorted.loc[:day_range].\
                                                          describe().loc["mean", "amount_weight"],2)
        return (statistics_dict, 200)

    @app.route("/misc_streak/<weight_str>/<weight_range_str>", methods=["GET"])
    def get_misc_streak(weight_str, weight_range_str):
        """
        Get the streak for a weight and range
        :param slot:
        :return:
        """
        '''#1.Step: Convert url parameters to float (the problem with the <float:weight> is that it
           required always a zero e.g. 85.0
        '''
        weight = float(weight_str)
        weight_range = float(weight_range_str)
        '#2.Step: Read data from database'
        df = pd.read_sql_table("misc", db.session.bind)
        '#2.1.Step: Convert column amount_weight to float and column date to datetime obj'
        df['amount_weight'] = df['amount_weight'].astype(float)
        df["timestamp_obj"] = pd.to_datetime(df["timestamp_obj"], format='%Y-%m/%d %h:%m:%s')
        '#3.Step: Sort by day and reset index'
        df_weight_sorted = df.sort_values(by=['timestamp_obj'], ascending=False)
        df_weight_sorted  = df_weight_sorted.reset_index(drop=True)
        '#4.Step: Select all rows which met the condition'
        df_weight = df.loc[(df_weight_sorted["amount_weight"] >= weight - weight_range) & (df_weight_sorted["amount_weight"] <= weight + weight_range)]
        '#5.Step: Now get the index of the df and find the longest index sequence'
        index_sequence = list(df_weight.index)
        '#5.1.Step: If index emtpy return 0'
        if len(index_sequence)== 0:
            return jsonify({
                'success': True,
                'longest_seq':0,
                'current_streak': 0,
                'streak_attempts':0,
                'avg_streak': 0,
            }, 200)
        else:
            '#5.2.Step: Get current streak'
            current_streak = streak.current_streak(index_sequence)
            '#5.3.Step: Get a sequence analysis'
            index_dict = streak.get_longest_sequence(index_sequence)
            '#5.3.1.Step: Get  streak attempts'
            streak_attempts = sum(k * v for k, v in index_dict.items())
            '#5.3.2.Step: Get the longest streak'
            longest_seq = max(index_dict.keys())
            '#5.5.Step: Get avg streak'
            itemKeyValue= max(index_dict.items(), key=lambda x: x[1])
            return jsonify({
                'success': True,
                'longest_seq':longest_seq,
                'current_streak': current_streak,
                'streak_attempts':streak_attempts,
                'avg_streak': itemKeyValue[0],
            }, 200)




    def convert_sqlalchemy_todict(obj):
        """
        Converts a sqlalchemy oject to a dict
        :param obj:
        :return:
        """
        return {c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs}

    @app.errorhandler(4011)
    def permission_check_fail(error):
        return jsonify(dict(success=False, error=4011,
                            message='Permission check fail. ' +
                                    'The person doenst has the required permission'
                            )), 4011

    @app.errorhandler(4012)
    def invalid_header(error):
        return jsonify(dict(success=False, error=4012,
                            message='invalid_header.' + " - " +
                                    'Authorization malformed.'
                            )), 4012

    @app.errorhandler(4013)
    def token_expired(error):
        return jsonify(dict(success=False, error=4013,
                            message='token_expired.' + " - " +
                                    'Token expired.'
                            )), 4013

    @app.errorhandler(4014)
    def invalid_claims(error):
        return jsonify(dict(success=False, error=4014,
                            message='invalid_claims' + " - " +
                                    'Incorrect claims. Please, check the audience and issuer.'
                            )), 4014
    app.merge_food_misc=merge_food_misc
    app.convert_sqlalchemy_todict = convert_sqlalchemy_todict

    @app.errorhandler(4015)
    def invalid_claims(error):
        return jsonify(dict(success=False, error=4015,
                            message='invalid_header' + " - " +
                                    'Unable to parse authentication token.'
                            )), 4015

    @app.errorhandler(4016)
    def invalid_claims(error):
        return jsonify(dict(success=False, error=4016,
                            message='invalid_header' + " " +
                                    'Unable to find the appropriate key.'
                            )), 4016

    @app.errorhandler(4017)
    def invalid_claims(error):
        return jsonify(dict(success=False, error=4017,
                            message='authorization is missing' + " " +
                                    'Add authorization header to the request.'
                            )), 4017

    @app.errorhandler(4018)
    def invalid_claims(error):
        return jsonify(dict(success=False, error=4018,
                            message='invalid_header' + " " +
                                    'The authorization header must be bearer'
                            )), 4018

    app.merge_food_misc=merge_food_misc
    app.convert_sqlalchemy_todict = convert_sqlalchemy_todict

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(dict(success=False, error=400,
                            message='Data was in the wrong format!'+\
                                    ' Server was not able to save data to database'
                            )), 400

    return app

'# Check if app runs on local computer:'
os.system('hostnamectl > tmp')
with open('tmp', 'r') as temp_var:
    content_tmp = temp_var.read()
    '#"fv-az99" is the name of the computer in the azure pipeline'
    if "gwillig" in content_tmp or "fv-az" in content_tmp:
        app = create_app(dbms="sqlite3")
    else:
        app = create_app(dbms="mysql")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
