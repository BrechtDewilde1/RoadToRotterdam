# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import flask
from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
import json
import Src.GetData
import Src.AnalyzeData

@blueprint.route('/index')
#@login_required
def index():
    # Refresh data
    stravaData = Src.GetData.getData(75133, "b32174d53ebd5bce6f78a2c398efa45654f4e556") #Client_id and Client_secret
    cleaned_data =  Src.AnalyzeData.clean_data(stravaData)
    data  = Src.AnalyzeData.analyze_data(cleaned_data)
    data["map"].save("apps/templates/home/map.html")

    return render_template('home/index.html', segment='index', 
                            runs = data["runs"],
                            more_runs_than_last_week = data["more_runs_than_last_week"], 
                            Total_distance = str(round(data["Total_distance"], 2)) + "KM",
                            Total_distance_last_week = str(round(data["Total_distance_last_week"], 2)) + "KM",
                            Longest_run = str(data["Longest_run"]) + "KM", 
                            Total_duration_last_week = data["Total_duration_last_week"],
                            Total_duration = data["Total_duration"], 
                            Longest_run_days_ago = data["Longest_run_days_ago"],
                            progress = round(data["perc_completed"], 2), 
                            week_1_date = data["week_dates"][-1], 
                            week_1_km = str(round(data["week_volumes"][-1], 2))+"KM",
                            week_1_completed = data["week_percentage"][-1], 
                            week_2_date = data["week_dates"][-2], 
                            week_2_km = str(round(data["week_volumes"][-2], 2)) + "KM",
                            week_2_completed = data["week_percentage"][-2], 
                            week_3_date =  data["week_dates"][-3], 
                            week_3_km = str(round(data["week_volumes"][-3], 2)) + "KM",
                            week_3_completed = data["week_percentage"][-3], 
                            week_4_date = data["week_dates"][-4], 
                            week_4_km = str(round(data["week_volumes"][-4], 2))+ "KM",
                            week_4_completed = 100,
                            week_5_date = data["week_dates"][-5], 
                            week_5_km = str(round(data["week_volumes"][-5], 2))+ "KM",
                            week_5_completed = 100,
                            long_run_numbers = data["Long_run_stats"][0],
                            long_run_Volume = data["Long_run_stats"][1],
                            long_run_ap = data["Long_run_stats"][2],
                            recovery_run_numbers = data["Recovery_run_stats"][0],
                            recovery_run_Volume = data["Recovery_run_stats"][1],
                            recovery_run_ap = data["Recovery_run_stats"][2],
                            interval_run_numbers = data["Interval_run_stats"][0],
                            interval_run_Volume = data["Interval_run_stats"][1],
                            interval_run_ap = data["Interval_run_stats"][2],
                            fartlek_run_numbers = data["Fartlek_run_stats"][0],
                            fartlek_run_Volume = data["Fartlek_run_stats"][1],
                            fartlek_run_ap = data["Fartlek_run_stats"][2],
                            hill_run_numbers = data["hill_run_stats"][0],
                            hill_run_Volume = data["hill_run_stats"][1],
                            hill_run_ap = data["hill_run_stats"][2])

@blueprint.route('/<template>')
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
