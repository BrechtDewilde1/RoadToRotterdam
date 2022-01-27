import Src.GetData
import Src.AnalyzeData
import json
import re
from statistics import mean

stravaData = Src.GetData.getData(75133, "b32174d53ebd5bce6f78a2c398efa45654f4e556") #Client_id and Client_secret
cleaned_data =  Src.AnalyzeData.clean_data(stravaData)
outcome_analysis = Src.AnalyzeData.analyze_data(cleaned_data)
outcome_analysis["map"].save("map.html")

## Store the json file
outcome_analysis_without_map = {k:outcome_analysis[k] for k in list(outcome_analysis.keys())[:-1]}
with open("data.json", "w") as fp:
    json.dump(outcome_analysis_without_map, fp)
