import pandas as pd
import datetime
import polyline
import numpy as np
import folium
import time
import re
from statistics import mean

def clean_data(stravaData):
    '''     '''
    # 1. Put date in usable format
    activities = pd.json_normalize(stravaData)
    
    # 2. Convert date column
    activities.loc[:, "start_date"] = pd.to_datetime(activities["start_date"]).dt.tz_localize(None)
    activities.loc[:, "start_date_local"] = pd.to_datetime(activities["start_date_local"]).dt.tz_localize(None)
    
    # 3. Filter the correct runs
    activities = activities[activities.type == "Run"]
    activities = activities[(activities.type == "Run") & (activities.start_date_local >= datetime.datetime(2021, 11, 8))]
    activities = activities[list(map(lambda x: "#" in x, activities.name))]
    
    # 4. Convert the units
    activities.loc[:, "distance"] /= 1000 # convert from m to km
    activities.loc[:, "average_speed"] *= 3.6 # convert from m/s to km/h
    activities.loc[:, "max_speed"] *= 3.6 # convert from m/s to km/h
    
    # 5. Decoding to plot routes
    def poly_coder(x):
        if x is None:
            return None
        else:
            return polyline.decode(x)
    activities["map.polyline"] = activities["map.summary_polyline"].apply(poly_coder)

    # 6. Determine week number
    activities["week_number"] = activities["start_date_local"].apply(lambda  x: x.isocalendar()[1])
    
    # 6. Set an index column
    activities.set_index("start_date_local", inplace=True)
    
    return activities

def centroid_f(polylines):
    x, y = [], []
    for polyline in polylines:
        for coord in polyline:
            x.append(coord[0])
            y.append(coord[1])
    return [(min(x)+max(x))/2, (min(y)+max(y))/2]

def map_creation(cleaned_data):
    # color scheme
    color = {'Ride':'red', 'Run':'blue', 'Walk':'purple'}
    resolution, width, height = 75, 6, 6.5

    m = folium.Map(location=centroid_f(cleaned_data['map.polyline']), zoom_start=4)
    for row in cleaned_data.iterrows():
        row_index = row[0]
        row_values = row[1]
        folium.PolyLine(row_values['map.polyline'], color=color[row_values['type']]).add_to(m)
        halfway_coord = row_values['map.polyline'][int(len(row_values['map.polyline'])/2)]

        halfway_coord = row_values['map.polyline'][int(len(row_values['map.polyline'])/2)]
        # popup text
        # popup text
        html = """
        <h3>{}</h3>
            <p>
                <code>
                Date : {} <br>
                Time : {}
                </code>
            </p>
        <h4>{}</h4>
            <p> 
                <code>
                    Distance&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp: {:.2f} km <br>
                    Elevation Gain&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp: {:.0f} m <br>
                    Moving Time&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp: {} <br>
                    Average Speed&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp: {:.2f} km/h (maximum: {:.2f} km/h) <br>
                </code>
            </p>
        """.format(
            row_values['name'], 
            row_index.date(), 
            row_index.time(),  
            row_values['type'], 
            row_values['distance'], 
            row_values['total_elevation_gain'], 
            time.strftime('%H:%M:%S', time.gmtime(row_values['moving_time'])), 
            row_values['average_speed'], row_values['max_speed']
        )

        # add marker to map
        iframe = folium.IFrame(html, width=(width*resolution)+20, height=(height*resolution)+20)
        popup = folium.Popup(iframe, max_width=2650)
        icon = folium.Icon(color=color[row_values['type']], icon='info-sign')
        marker = folium.Marker(location=halfway_coord, popup=popup, icon=icon)
        marker.add_to(m)
    return m    

def analyze_data(cleaned_data):
    analyze_output = dict()
    
    # Number of runs
    analyze_output["runs"] = len(cleaned_data)

    # Number of runs compared with last week
    cur_week = max(cleaned_data["week_number"])
    analyze_output["more_runs_than_last_week"] = len(cleaned_data) - len(cleaned_data[cleaned_data["week_number"] < cur_week])

    # Percentage completed 
    analyze_output["perc_completed"] = round(len(cleaned_data)/90 * 100, 4)

    # Total km
    analyze_output["Total_distance"] = sum(cleaned_data["distance"])
    analyze_output["Total_distance_last_week"] = sum(cleaned_data["distance"]) - sum(cleaned_data.distance[cleaned_data["week_number"] < cur_week])

    # Longest run 
    analyze_output["Longest_run"] = max(cleaned_data["distance"])
    analyze_output["Longest_run_days_ago"] = abs(datetime.datetime.now().date() - cleaned_data.distance.idxmax().date()).days

    # Highest week volume 
    week_dict = dict()
    week_date_dict = dict()
    week_compl_dict = dict()
    for week, week_df in cleaned_data.groupby("week_number"):
        week_dict[week] = sum(week_df["distance"])
        week_date_dict[week] = str(min(list(week_df.index)).date()) + ' - ' + str(max(list(week_df.index)).date())
        week_compl_dict[week]= round(len(week_df)/5 * 100)
    
    # Week volumes
    analyze_output["week_volumes"] = [week_dict[k] for k in list(week_dict.keys())[-5:]]
    analyze_output["highest_week_volume"] = max(list(week_dict.values()))

    # Week dates
    analyze_output["week_dates"] = [week_date_dict[k] for k in list(week_date_dict.keys())[-5:]]

    # Week percentage
    analyze_output["week_percentage"] = [week_compl_dict[k] for k in list(week_compl_dict.keys())[-5:]]

    # Total duration
    totalDuration = sum(cleaned_data["moving_time"])/3600
    totalDuration_last_week = (sum(cleaned_data["moving_time"]) - sum(cleaned_data["moving_time"][cleaned_data["week_number"] < cur_week]))/3600
    analyze_output["Total_duration"] = "{0:02.0f}H:{1:02.0f}M".format(*divmod(totalDuration * 60, 60))
    analyze_output["Total_duration_last_week"] = "{0:02.0f}H:{1:02.0f}M".format(*divmod(totalDuration_last_week * 60, 60))

    # Stats per exercise type
    def cleaned_exercise_type(value):
        value = re.sub("[^ a-zA-Z]+", "", value)
        value = value.strip()

        if "Long" in value:
            return "Long run"
        elif "Recovery" in value:
            return "Recovery"
        elif "Interval" in value:
            return "Interval"
        elif "Fartlek" in value:
            return "Fartlek"
        elif "Hill" in value:
            return "Hill"

    def type_stats(group_df):
        return [len(group_df), str(round(sum(group_df.distance), 2)) + "KM", str(round(mean(group_df.average_speed), 2)) + "KM/H"]

    cleaned_data.cleaned_name = cleaned_data.name.apply(lambda x: cleaned_exercise_type(x))

    analyze_output["Long_run_stats"] = type_stats(cleaned_data[cleaned_data.cleaned_name == "Long run"])
    analyze_output["Recovery_run_stats"] = type_stats(cleaned_data[cleaned_data.cleaned_name == "Recovery"])
    analyze_output["Interval_run_stats"] = type_stats(cleaned_data[cleaned_data.cleaned_name == "Interval"])
    analyze_output["Fartlek_run_stats"] = type_stats(cleaned_data[cleaned_data.cleaned_name == "Fartlek"])
    analyze_output["hill_run_stats"] = type_stats(cleaned_data[cleaned_data.cleaned_name == "Hill"])

    # Where do i have been running? 
    analyze_output["map"] = map_creation(cleaned_data[cleaned_data["map.polyline"].apply(lambda x: x is not None)]) 
       
    return analyze_output

