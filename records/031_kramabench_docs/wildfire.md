# KramaBench wildfire：说明材料及文件开头摘录

以下为原文/原字段摘录；不解释其含义。文本保持解码后的字符与换行；Excel 以原 OOXML 单元格坐标和值呈现，不重排、不推断表头、不计算公式。

## 文件：`wildfire/input/Fire_Weather_Data_2002-2014_2016.csv`

来源：`data/kramabench/data/wildfire/input/Fire_Weather_Data_2002-2014_2016.csv`；1,302,377 字节；扩展名 `.csv`。

摘录范围：first_5_physical_lines。

<!-- excerpt:wildfire.1721.1 chars:1329 -->
```text
start_year,region_ind,incident_number,avrh_mean,wind_med,erc_med,rain_sum,region,state,incident_name,cause,dominant_strategy_25_s,dominant_strategy_50_s,dominant_strategy_75_s,subdom_strategy,start_date,controlled_date,duration,prim_threatened_aggregate,comm_threatened_aggregate,outb_threatened_aggregate,injuries_to_date_last,fatalities_last,latitude,longitude,start_day_of_year,control_year,control_day_of_year,gt_100,dom_strat_ind_75,dom_strat_ind_25,dom_strat_ind_50,station_verified_in_psa,hec,cause_ind,total_fire_region,total_fire_west
2002,6,CA-ANF-3518,39,6,77,0,California,CA,williams/curve complex,U,Full Suppression,Full Suppression,Full Suppression,,9/22/2002,10/15/2002,24,33100,180,15903,4,0,34,-118,265,2002,288,1,0,0,0,45421,15417,0,99,403
2002,6,CA-AEU-16666,46,1,56,0,California,CA,sly park vmp,N,Full Suppression,Full Suppression,Full Suppression,,10/21/2002,10/21/2002,1,0,0,0,0,0,39,-121,294,2002,294,1,0,0,0,42603,81,0,99,403
2002,6,CA-LAC02172482,19,18,24,0,California,CA,cherry,U,Full Suppression,Full Suppression,Full Suppression,,8/25/2002,8/27/2002,3,0,0,0,0,0,35,-118,237,2002,239,1,0,0,0,45440,49,0,99,403
2002,6,CA-ANF-001751,60,6,26,0,California,CA,susanna,H,Full Suppression,Full Suppression,Full Suppression,,6/3/2002,6/8/2002,6,30,15,25,3,0,34,-118,154,2002,159,1,0,0,0,45421,51,1,99,403
```
<!-- /excerpt:wildfire.1721.1 -->

## 文件：`wildfire/input/NST-EST2024-POP.xlsx`

来源：`data/kramabench/data/wildfire/input/NST-EST2024-POP.xlsx`；15,507 字节；扩展名 `.xlsx`。

摘录范围：all_sheet_names。

<!-- excerpt:wildfire.1722.1 chars:65 -->
```json
[
  {
    "name": "NST-EST2024-POP",
    "state": "visible"
  }
]
```
<!-- /excerpt:wildfire.1722.1 -->

### 页：`NST-EST2024-POP`

摘录范围：excel_first_10_physical_rows。

<!-- excerpt:wildfire.1722.2 chars:7561 -->
```jsonl
{"row": 1, "cells": [{"cell": "A1", "type": "s", "text": "table with row headers in column A and column headers in rows 3 through 4. (leading dots indicate sub-parts)", "style_index": "19"}, {"cell": "B1", "type": "n", "raw_value": null, "style_index": "19"}, {"cell": "C1", "type": "n", "raw_value": null, "style_index": "19"}, {"cell": "D1", "type": "n", "raw_value": null, "style_index": "19"}, {"cell": "E1", "type": "n", "raw_value": null, "style_index": "19"}, {"cell": "F1", "type": "n", "raw_value": null, "style_index": "19"}, {"cell": "G1", "type": "n", "raw_value": null, "style_index": "19"}]}
{"row": 2, "cells": [{"cell": "A2", "type": "s", "text": "Annual Estimates of the Resident Population for the United States, Regions, States, District of Columbia, and Puerto Rico: April 1, 2020 to July 1, 2024", "style_index": "20"}, {"cell": "B2", "type": "n", "raw_value": null, "style_index": "21"}, {"cell": "C2", "type": "n", "raw_value": null, "style_index": "21"}, {"cell": "D2", "type": "n", "raw_value": null, "style_index": "21"}, {"cell": "E2", "type": "n", "raw_value": null, "style_index": "21"}, {"cell": "F2", "type": "n", "raw_value": null, "style_index": "21"}, {"cell": "G2", "type": "n", "raw_value": null, "style_index": "21"}]}
{"row": 3, "cells": [{"cell": "A3", "type": "s", "text": "Geographic Area", "style_index": "22"}, {"cell": "B3", "type": "s", "text": "April 1, 2020 Estimates Base", "style_index": "24"}, {"cell": "C3", "type": "s", "text": "Population Estimate (as of July 1)", "style_index": "25"}, {"cell": "D3", "type": "n", "raw_value": null, "style_index": "26"}, {"cell": "E3", "type": "n", "raw_value": null, "style_index": "26"}, {"cell": "F3", "type": "n", "raw_value": null, "style_index": "26"}, {"cell": "G3", "type": "n", "raw_value": null, "style_index": "26"}, {"cell": "H3", "type": "n", "raw_value": null, "style_index": "39"}, {"cell": "I3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "J3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "K3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "L3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "M3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "N3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "O3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "P3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "Q3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "R3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "S3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "T3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "U3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "V3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "W3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "X3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "Y3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "Z3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "AA3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "AB3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "AC3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "AD3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "AE3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "AF3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "AG3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "AH3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "AI3", "type": "n", "raw_value": null, "style_index": "40"}, {"cell": "AJ3", "type": "n", "raw_value": null, "style_index": "40"}]}
{"row": 4, "cells": [{"cell": "A4", "type": "n", "raw_value": null, "style_index": "23"}, {"cell": "B4", "type": "n", "raw_value": null, "style_index": "23"}, {"cell": "C4", "type": "n", "raw_value": "2020", "style_index": "3"}, {"cell": "D4", "type": "n", "raw_value": "2021", "style_index": "3"}, {"cell": "E4", "type": "n", "raw_value": "2022", "style_index": "3"}, {"cell": "F4", "type": "n", "raw_value": "2023", "style_index": "3"}, {"cell": "G4", "type": "n", "raw_value": "2024", "style_index": "3"}]}
{"row": 5, "cells": [{"cell": "A5", "type": "s", "text": "United States", "style_index": "4"}, {"cell": "B5", "type": "n", "raw_value": "331515736", "style_index": "5"}, {"cell": "C5", "type": "n", "raw_value": "331577720", "style_index": "5"}, {"cell": "D5", "type": "n", "raw_value": "332099760", "style_index": "5"}, {"cell": "E5", "type": "n", "raw_value": "334017321", "style_index": "5"}, {"cell": "F5", "type": "n", "raw_value": "336806231", "style_index": "5"}, {"cell": "G5", "type": "n", "raw_value": "340110988", "style_index": "5"}]}
{"row": 6, "cells": [{"cell": "A6", "type": "s", "text": "Northeast", "style_index": "6"}, {"cell": "B6", "type": "n", "raw_value": "57617706", "style_index": "7"}, {"cell": "C6", "type": "n", "raw_value": "57431458", "style_index": "7"}, {"cell": "D6", "type": "n", "raw_value": "57252533", "style_index": "7"}, {"cell": "E6", "type": "n", "raw_value": "57159597", "style_index": "7"}, {"cell": "F6", "type": "n", "raw_value": "57398303", "style_index": "7"}, {"cell": "G6", "type": "n", "raw_value": "57832935", "style_index": "7"}]}
{"row": 7, "cells": [{"cell": "A7", "type": "s", "text": "Midwest", "style_index": "6"}, {"cell": "B7", "type": "n", "raw_value": "68998970", "style_index": "7"}, {"cell": "C7", "type": "n", "raw_value": "68984258", "style_index": "7"}, {"cell": "D7", "type": "n", "raw_value": "68872831", "style_index": "7"}, {"cell": "E7", "type": "n", "raw_value": "68903297", "style_index": "7"}, {"cell": "F7", "type": "n", "raw_value": "69186401", "style_index": "7"}, {"cell": "G7", "type": "n", "raw_value": "69596584", "style_index": "7"}]}
{"row": 8, "cells": [{"cell": "A8", "type": "s", "text": "South", "style_index": "6"}, {"cell": "B8", "type": "n", "raw_value": "126281537", "style_index": "7"}, {"cell": "C8", "type": "n", "raw_value": "126476549", "style_index": "7"}, {"cell": "D8", "type": "n", "raw_value": "127368010", "style_index": "7"}, {"cell": "E8", "type": "n", "raw_value": "129037849", "style_index": "7"}, {"cell": "F8", "type": "n", "raw_value": "130893358", "style_index": "7"}, {"cell": "G8", "type": "n", "raw_value": "132665693", "style_index": "7"}]}
{"row": 9, "cells": [{"cell": "A9", "type": "s", "text": "West", "style_index": "8"}, {"cell": "B9", "type": "n", "raw_value": "78617523", "style_index": "9"}, {"cell": "C9", "type": "n", "raw_value": "78685455", "style_index": "9"}, {"cell": "D9", "type": "n", "raw_value": "78606386", "style_index": "9"}, {"cell": "E9", "type": "n", "raw_value": "78916578", "style_index": "9"}, {"cell": "F9", "type": "n", "raw_value": "79328169", "style_index": "9"}, {"cell": "G9", "type": "n", "raw_value": "80015776", "style_index": "9"}]}
{"row": 10, "cells": [{"cell": "A10", "type": "s", "text": ".Alabama", "style_index": "10"}, {"cell": "B10", "type": "n", "raw_value": "5025369", "style_index": "7"}, {"cell": "C10", "type": "n", "raw_value": "5033094", "style_index": "7"}, {"cell": "D10", "type": "n", "raw_value": "5049196", "style_index": "7"}, {"cell": "E10", "type": "n", "raw_value": "5076181", "style_index": "7"}, {"cell": "F10", "type": "n", "raw_value": "5117673", "style_index": "7"}, {"cell": "G10", "type": "n", "raw_value": "5157699", "style_index": "7"}]}
```
<!-- /excerpt:wildfire.1722.2 -->

## 文件：`wildfire/input/PublicView_RAWS_-3515561676727363726.csv`

来源：`data/kramabench/data/wildfire/input/PublicView_RAWS_-3515561676727363726.csv`；1,395,019 字节；扩展名 `.csv`。

摘录范围：first_5_physical_lines。

<!-- excerpt:wildfire.1723.1 chars:1894 -->
```text
﻿OBJECTID,Station Name,WX ID,Ob Time,NESS ID,NWS ID,Elevation,Site Description,Latitude,Longitude,State,County,Agency,Region,Unit,Sub-Unit,Status,Rain Accumulation,Wind Speed MPH,Wind Direction Degrees,"Air Temperaturee, Standard Placement",Fuel Temperature,Relative Humidity,Battery Voltage,Fuel Moisture,"Wind Direction, Peak",Wind Speed Peak MPH,Solar Radiation,Station ID,MesoWest Station ID,MesoWest Detailed Weather Link,NOAA Detailed Weather Link,x,y
12,YNP PORTABLE,18053679,4/18/2025 3:02:04 PM,32D3E21C,,3633,,37.73003,-119.61131,CA,Mariposa,NPS,PACIFIC WEST,YOSEMITE NP,,A,45.9 inches,0 mph,225 degrees ,34 deg. F,33 deg. F ,98 % ,12.8 volts,23.8 (unk),185 degrees,3 mph,9 w/m2,18053677,YNWC1,https://mesowest.utah.edu/cgi-bin/droman/meso_base_dyn.cgi?stn=YNWC1&unit=0&timetype=GMT,https://www.weather.gov/wrh/timeseries?site=YNWC1,-119.61131,37.73003
15,BOGUE CHITTO,18770458,4/18/2025 3:12:44 PM,32B108FA,227701,126,,30.66194,-89.79556,MS,Pearl River,FWS,REGION 4,BIG BRANCH NWR,SE La Refuges Comple,A,8.77 inches,3 mph,141 degrees ,77 deg. F,79 deg. F ,70 % ,13 volts,18.4 (unk),148 degrees,7 mph,233 w/m2,18770452,BCCM6,https://mesowest.utah.edu/cgi-bin/droman/meso_base_dyn.cgi?stn=BCCM6&unit=0&timetype=GMT,https://www.weather.gov/wrh/timeseries?site=BCCM6,-89.79556,30.6619400000001
43,DEVILS TOWER,17137193,4/18/2025 3:23:04 PM,FA64F588,480606,3872,Devils Tower residence area,44.58179,-104.7195,WY,Crook,NPS,MIDWEST,DEVILS TOWER NM,NORTHERN GREAT PLAIN,A,2.86 inches,2 mph,154 degrees ,38 deg. F,41 deg. F ,65 % ,14.1 volts,21.9 (unk),218 degrees,5 mph,300 w/m2,17137190,DVLW4,https://mesowest.utah.edu/cgi-bin/droman/meso_base_dyn.cgi?stn=DVLW4&unit=0&timetype=GMT,https://www.weather.gov/wrh/timeseries?site=DVLW4,-104.7195,44.5817900000001
49,MENDOCINO PASS,17209652,4/18/2025 3:04:34 PM,32715230,041018,5382,"SITE IS JUST NORTH OF MENDOCINO PASS. AREA IS IN A SMALL
```
<!-- /excerpt:wildfire.1723.1 -->

## 文件：`wildfire/input/Wildfire_Acres_by_State.csv`

来源：`data/kramabench/data/wildfire/input/Wildfire_Acres_by_State.csv`；1,346 字节；扩展名 `.csv`。

摘录范围：first_5_physical_lines。

<!-- excerpt:wildfire.1724.1 chars:133 -->
```text
State,Total Acres Burned,Population
Alabama,20978.0,5157699
Alaska,667075.0,740133
Arizona,282989.0,7582384
Arkansas,25444.0,3088354
```
<!-- /excerpt:wildfire.1724.1 -->

## 文件：`wildfire/input/Wildfire_Fires_by_State.csv`

来源：`data/kramabench/data/wildfire/input/Wildfire_Fires_by_State.csv`；516 字节；扩展名 `.csv`。

摘录范围：first_5_physical_lines。

<!-- excerpt:wildfire.1725.1 chars:69 -->
```text
State,Total Fires
Alabama,1525
Alaska,377
Arizona,2191
Arkansas,1219
```
<!-- /excerpt:wildfire.1725.1 -->

## 文件：`wildfire/input/annual_aqi_by_county_2024.csv`

来源：`data/kramabench/data/wildfire/input/annual_aqi_by_county_2024.csv`；66,833 字节；扩展名 `.csv`。

摘录范围：first_5_physical_lines。

<!-- excerpt:wildfire.1726.1 chars:522 -->
```text
"State","County","Year","Days with AQI","Good Days","Moderate Days","Unhealthy for Sensitive Groups Days","Unhealthy Days","Very Unhealthy Days","Hazardous Days","Max AQI","90th Percentile AQI","Median AQI","Days CO","Days NO2","Days Ozone","Days PM2.5","Days PM10"
"Alabama","Baldwin",2024,210,181,29,0,0,0,0,84,53,39,0,0,98,112,0
"Alabama","Clay",2024,212,176,36,0,0,0,0,75,53,29,0,0,0,212,0
"Alabama","DeKalb",2024,244,182,62,0,0,0,0,87,58,44,0,0,170,74,0
"Alabama","Elmore",2024,144,142,2,0,0,0,0,58,47,37,0,0,144,0,0
```
<!-- /excerpt:wildfire.1726.1 -->

## 文件：`wildfire/input/cleaned_helicopter_requests_by_region.csv`

来源：`data/kramabench/data/wildfire/input/cleaned_helicopter_requests_by_region.csv`；303 字节；扩展名 `.csv`。

摘录范围：first_5_physical_lines。

<!-- excerpt:wildfire.1727.1 chars:127 -->
```text
Region,Total Helicopter Requests
Alaska Area,19
Eastern Area,9
Great Basin Area,232
National Interagency Coordination Center,0
```
<!-- /excerpt:wildfire.1727.1 -->

## 文件：`wildfire/input/democratic_vs_republican_votes_by_usa_state_2020.csv`

来源：`data/kramabench/data/wildfire/input/democratic_vs_republican_votes_by_usa_state_2020.csv`；2,880 字节；扩展名 `.csv`。

摘录范围：first_5_physical_lines。

<!-- excerpt:wildfire.1728.1 chars:261 -->
```text
state,DEM,REP,usa_state,usa_state_code,percent_democrat
Alabama,843473,1434159,Alabama,AL,37.03289205631111
Alaska,45758,80999,Alaska,AK,36.09899256056865
Arizona,1643664,1626679,Arizona,AZ,50.25968224128172
Arkansas,420985,761251,Arkansas,AR,35.60921846399535
```
<!-- /excerpt:wildfire.1728.1 -->

## 文件：`wildfire/input/load_data.py`

来源：`data/kramabench/data/wildfire/input/load_data.py`；450 字节；扩展名 `.py`。

摘录范围：full_text。

<!-- excerpt:wildfire.1729.1 chars:450 -->
```text
import kagglehub

# WeatherEvents_Jan2016-Dec2022.csv needs to be downloaded from Kaggle
# Due to the size of the dataset, it is not included in the repository.

# Download latest version
path = kagglehub.dataset_download("sobhanmoosavi/us-weather-events")
print("Path to us weather events dataset files:", path)
path_2 = kagglehub.dataset_download("robikscube/zillow-home-value-index")
print("Path to zillow home index value dataset files:", path_2)
```
<!-- /excerpt:wildfire.1729.1 -->

## 文件：`wildfire/input/nifc_geographic_areas.gpkg`

来源：`data/kramabench/data/wildfire/input/nifc_geographic_areas.gpkg`；10,248,192 字节；扩展名 `.gpkg`。

摘录范围：gpkg_layer_names_and_field_names_readonly。

<!-- excerpt:wildfire.1730.1 chars:998 -->
```json
[
  {
    "layer_name": "National_GACC_Final_20250113",
    "data_type": "features",
    "fields": [
      {
        "name": "OBJECTID",
        "type": "INTEGER"
      },
      {
        "name": "SHAPE",
        "type": "MULTIPOLYGON"
      },
      {
        "name": "GeometryID",
        "type": "TEXT(50)"
      },
      {
        "name": "GACCName",
        "type": "TEXT(75)"
      },
      {
        "name": "GACCUnitID",
        "type": "TEXT(8)"
      },
      {
        "name": "GACCAbbreviation",
        "type": "TEXT(4)"
      },
      {
        "name": "GACCLocation",
        "type": "TEXT(50)"
      },
      {
        "name": "ContactPhone",
        "type": "TEXT(12)"
      },
      {
        "name": "Comments",
        "type": "TEXT(255)"
      },
      {
        "name": "DateCurrent",
        "type": "DATETIME"
      },
      {
        "name": "MapMethod",
        "type": "TEXT(25)"
      },
      {
        "name": "GlobalID",
        "type": "TEXT(38)"
      }
    ]
  }
]
```
<!-- /excerpt:wildfire.1730.1 -->

## 文件：`wildfire/input/nifc_human_caused_acres.csv`

来源：`data/kramabench/data/wildfire/input/nifc_human_caused_acres.csv`；2,508 字节；扩展名 `.csv`。

摘录范围：first_5_physical_lines。

<!-- excerpt:wildfire.1731.1 chars:554 -->
```text
Year	Alaska	Northwest	Northern California	Southern California	Northern Rockies	Great Basin	Western Great Basin	Southwest	Rocky Mountains	Eastern Area	Southern Area	Total
2024	3,512	719,771	539,170	451,843	256,481	163,215	N/A	99,642	289,709	206,169	1,937,041	4,666,553
2023	737	233,619	17,209	138,115	45,705	63,626	N/A	101,612	225,324	113,065	594,233	1,533,245
2022	11,843	163,580	190,768	84,673	56,045	270,330	N/A	918,803	252,596	60,986	1,360,545	3,370,169
2021	9,894	365,742	1,024,538	82,405	243,603	72,416	N/A	351,928	263,758	122,382	487,093	3,023,759
```
<!-- /excerpt:wildfire.1731.1 -->

## 文件：`wildfire/input/nifc_human_caused_wildfires.csv`

来源：`data/kramabench/data/wildfire/input/nifc_human_caused_wildfires.csv`；1,956 字节；扩展名 `.csv`。

摘录范围：first_5_physical_lines。

<!-- excerpt:wildfire.1732.1 chars:471 -->
```text
Year	Alaska	Northwest	Northern California	Southern California	Northern Rockies	Great Basin	Western Great Basin	Southwest	Rocky Mountains	Eastern Area	Southern Area	Total
2024	197	2,911	2,992	5,107	2,653	1,998	N/A	1,874	2,316	13,961	23,980	57,962
2023	170	2,805	2,779	4,115	1,892	974	N/A	1,881	1,174	10,240	24,627	50,697
2022	313	2,295	3,244	4,345	1,649	1,171	N/A	1,379	1,584	8,485	36,964	61,429
2021	262	3,075	3,621	5,083	2,981	1,362	N/A	1,657	2,146	10,725	21,729	52,641
```
<!-- /excerpt:wildfire.1732.1 -->

## 文件：`wildfire/input/nifc_lightning_caused_acres.csv`

来源：`data/kramabench/data/wildfire/input/nifc_lightning_caused_acres.csv`；2,481 字节；扩展名 `.csv`。

摘录范围：first_5_physical_lines。

<!-- excerpt:wildfire.1733.1 chars:549 -->
```text
Year	Alaska	Northwest	Northern California	Southern California	Northern Rockies	Great Basin	Western Great Basin*	Southwest	Rocky Mountains	Eastern Area	Southern Area	Total
2024	663,564	1,354,814	10,919	79,372	339,858	1,024,949	N/A	260,766	465,802	498	57,789	4,258,331
2023	313,538	119,748	172,438	17,019	91,949	34,030	N/A	298,788	24,039	351	88,765	1,160,665
2022	3,099,133	467,980	56,221	2,676	167,700	166,266	N/A	65,153	20,906	3,355	157,570	4,206,960
2021	243,463	1,137,284	920,967	237,972	826,057	300,748	N/A	288,935	72,428	30,287	45,743	4,101,884
```
<!-- /excerpt:wildfire.1733.1 -->

## 文件：`wildfire/input/nifc_lightning_caused_wildfires.csv`

来源：`data/kramabench/data/wildfire/input/nifc_lightning_caused_wildfires.csv`；1,667 字节；扩展名 `.csv`。

摘录范围：first_5_physical_lines。

<!-- excerpt:wildfire.1734.1 chars:416 -->
```text
Year	Alaska	Northwest	Northern California	Southern California	Northern Rockies	Great Basin*	Western Great Basin*	Southwest	Rocky Mountains	Eastern Area	Southern Area	Total
2024	180	1,134	148	156	1,017	1,281	N/A	1,064	1,066	80	809	6,935
2023	179	882	470	174	576	777	N/A	936	734	77	1,081	5,883
2022	282	1,225	185	115	1,061	949	N/A	754	808	107	1,981	7,467
2021	122	1,000	341	241	1,071	1,087	N/A	747	1,170	130	435	6,344
```
<!-- /excerpt:wildfire.1734.1 -->

## 文件：`wildfire/input/nifc_suppression_costs.csv`

来源：`data/kramabench/data/wildfire/input/nifc_suppression_costs.csv`；2,504 字节；扩展名 `.csv`。

摘录范围：first_5_physical_lines。

<!-- excerpt:wildfire.1735.1 chars:292 -->
```text
Year	Fires	Acres	Forest Service	DOI Agencies	Total
1985	82,591	2,896,147	$161,505,000	$78,438,000	$239,943,000
1986	85,907	2,719,162	$111,625,000	$91,153,000	$202,778,000
1987	71,300	2,447,296	$253,657,000	$81,452,000	$335,109,000
1988	72,750	5,009,290	$429,609,000	$149,317,000	$578,926,000
```
<!-- /excerpt:wildfire.1735.1 -->

## 文件：`wildfire/input/nifc_wildfires.csv`

来源：`data/kramabench/data/wildfire/input/nifc_wildfires.csv`；944 字节；扩展名 `.csv`。

摘录范围：first_5_physical_lines。

<!-- excerpt:wildfire.1736.1 chars:105 -->
```text
Year	Fires	Acres
2024	64,897	8,924,884
2023	56,580	2,693,910
2022	68,988	7,577,183
2021	58,985	7,125,643
```
<!-- /excerpt:wildfire.1736.1 -->

## 文件：`wildfire/input/noaa_wildfires.csv`

来源：`data/kramabench/data/wildfire/input/noaa_wildfires.csv`；1,302,377 字节；扩展名 `.csv`。

摘录范围：first_5_physical_lines。

<!-- excerpt:wildfire.1737.1 chars:1329 -->
```text
start_year,region_ind,incident_number,avrh_mean,wind_med,erc_med,rain_sum,region,state,incident_name,cause,dominant_strategy_25_s,dominant_strategy_50_s,dominant_strategy_75_s,subdom_strategy,start_date,controlled_date,duration,prim_threatened_aggregate,comm_threatened_aggregate,outb_threatened_aggregate,injuries_to_date_last,fatalities_last,latitude,longitude,start_day_of_year,control_year,control_day_of_year,gt_100,dom_strat_ind_75,dom_strat_ind_25,dom_strat_ind_50,station_verified_in_psa,hec,cause_ind,total_fire_region,total_fire_west
2002,6,CA-ANF-3518,39,6,77,0,California,CA,williams/curve complex,U,Full Suppression,Full Suppression,Full Suppression,,9/22/2002,10/15/2002,24,33100,180,15903,4,0,34,-118,265,2002,288,1,0,0,0,45421,15417,0,99,403
2002,6,CA-AEU-16666,46,1,56,0,California,CA,sly park vmp,N,Full Suppression,Full Suppression,Full Suppression,,10/21/2002,10/21/2002,1,0,0,0,0,0,39,-121,294,2002,294,1,0,0,0,42603,81,0,99,403
2002,6,CA-LAC02172482,19,18,24,0,California,CA,cherry,U,Full Suppression,Full Suppression,Full Suppression,,8/25/2002,8/27/2002,3,0,0,0,0,0,35,-118,237,2002,239,1,0,0,0,45440,49,0,99,403
2002,6,CA-ANF-001751,60,6,26,0,California,CA,susanna,H,Full Suppression,Full Suppression,Full Suppression,,6/3/2002,6/8/2002,6,30,15,25,3,0,34,-118,154,2002,159,1,0,0,0,45421,51,1,99,403
```
<!-- /excerpt:wildfire.1737.1 -->

## 文件：`wildfire/input/noaa_wildfires_monthly_stats.csv`

来源：`data/kramabench/data/wildfire/input/noaa_wildfires_monthly_stats.csv`；7,717 字节；扩展名 `.csv`。

摘录范围：first_5_physical_lines。

<!-- excerpt:wildfire.1738.1 chars:130 -->
```text
Title:U.S. Wildfires December
Missing:-999

Date,"Acres Burned","Number of Fires","Acres Burned per Fire"
200001,40757,2796,14.58
```
<!-- /excerpt:wildfire.1738.1 -->

## 文件：`wildfire/input/noaa_wildfires_variabledescrip.csv`

来源：`data/kramabench/data/wildfire/input/noaa_wildfires_variabledescrip.csv`；5,157 字节；扩展名 `.csv`。

摘录范围：full_text。

<!-- excerpt:wildfire.1739.1 chars:5157 -->
```text
Variable Name ,"Young et al. 2020, Table 1",Alternative description
start_year,Discovery Year,"Year wildfire incident is discovered, described as YYYY"
region_ind,,Numeric value representing the region
incident_number,,ICS-209 identifier (wildfire incident identifying number)
avrh_mean,Average Relative Humidity,"Average (mean) Relative Humidity, a percentage defined as ""Daily average water vapor in the air relative to saturation"""
wind_med,Wind,Daily average (median) wind speed within the wildfire incident area in miles per hour
erc_med,Energy release component ,"Average (median) Energy Release Component (ERC) defined as ""BTUs / square foot released from a fire’s flaming front"""
rain_sum,Precipitation,"Summary of daily precipitation, described as either total precipitation over the length of an individual wildfire incident or the total for all fires within a ""fire cluster"" for a fire year"
region,Region,"Geographic region where the wildfire incident was discovered; dataset contains six regions total (California, Great Basin, Northwest, Inland Empire, Rocky Mountains, Southwest)"
state,State,Standard two-letter representation of the U.S.A. state where a wildfire incident was discovered
incident_name,Incident name,Unique alphabetic identifier for a wildfire incident
cause,Cause ,"Declared cause of wildfire incident ignition; attribute contains several different causes which are grouped into ""human"" and ""non-human"" or ""natural"" (U=unknown, N=natural, H=human, L=lightning, O=other)"
dominant_strategy_25_s,,"Wildfire with at least 25% suppression strategies = full suppression, otherwise = other"
dominant_strategy_50_s,,"Wildfire with at least 50% suppression strategies = full suppression, otherwise = other"
dominant_strategy_75_s,,"Wildfire with at least 75% suppression strategies = full suppression, otherwise = other"
subdom_strategy,,"Dominant strategy listed in ICS-209 data (Combo, Confine, Full Suppression, Monitor, nonFS-Combo, Point Zone Protection)"
start_date,Discovery Date,"Calendar date wildfire incident is discovered, described as MM/DD/YYYY C.E."
controlled_date,Control Date,"Calendar date wildfire incident is declared ""controlled"" by incident command, described as MM/DD/YYYY C.E."
duration,Duration,"Length of time, in days, from when wildfire incident is discovered (""start_date"") to when it is declared ""out"" by incident command"
prim_threatened_aggregate,"Houses at risk, contributed to",Number of houses (primary residences) at risk because of or contributed to by a wildfire incident
comm_threatened_aggregate,"Commercial Building at risk, contributed to",Number of commercial buildings at risk because of or contributed to by a wildfire incident
outb_threatened_aggregate,"Other buildings at risk, contributed to",Number of houses (primary residences) at risk because of or contributed to by a wildfire incident
injuries_to_date_last,"Injuries, contributed to",Total number of human injuries from discovery date to time of publication which are caused by or contributed to by a wildfire incident
fatalities_last,"Fatalities, contributed to",Total number of human fatalities from discovery date to time of publication which are caused or contributed to by a wildfire incident
latitude,Latitude,Latitude (decimal degrees)
longitude,Longitude,Longitude (decimal degrees)
start_day_of_year,Start day of the year,"Day of the year a wildfire incident is discovered, described by a continuous day count where 1 January is ""1"" and 31 December is ""365"" (""366"" on leap years)"
control_year,Control Year,"Year wildfire incident is declared ""controlled"", described as YYYY"
control_day_of_year,Control day of the year,"Day of the year a wildfire incident is declared ""controlled"", described by a continuous day count where 1 January is ""1"" and 31 December is ""365"" (""366"" on leap years)"
gt_100,,Indicator for fire size greater than 100 acres (1 = > 100 acres)
dom_strat_ind_75,,"Indicator for wildfire with at least 75% suppression strategies (1 = wildfire with at least 75% suppression response strategy, 0 = wildfire with < 75%)"
dom_strat_ind_25,,"Indicator for wildfire with at least 25% suppression strategies (1 = wildfire with at least 25% suppression response strategy, 0 = wildfire with < 25%)"
dom_strat_ind_50,,"Indicator for wildfire with at least 50% suppression strategies (1 = wildfire with at least 50% suppression response strategy, 0 = wildfire with < 50%)"
station_verified_in_psa,,Remote Automatic Weather Station (RAWS) ID number for weather data
hec,Fire Size,Wildfire incident size in hectares
cause_ind,Cause ,"Indicator of wildfire incident cause of ignition (0 = non-human ignited such as Natural, Unknown, Lightning; 1 = human ignited)"
total_fire_region,Number of Fires - Region ,"Total number of wildifire incidents in a given region (see ""region"" attribute) in a given fire year (see ""start_year"" in attributes)"
total_fire_west,Number of Fires - West,"Total number of wildifire incidents in the western U.S. (containing all six regions and 11 states) in a given fire year (see ""start_year"" in attributes)"
```
<!-- /excerpt:wildfire.1739.1 -->

## 文件：`wildfire/input/state_abbreviation_to_state.json`

来源：`data/kramabench/data/wildfire/input/state_abbreviation_to_state.json`；1,317 字节；扩展名 `.json`。

摘录范围：full_text。

<!-- excerpt:wildfire.1740.1 chars:1317 -->
```text
{
    "AK": "Alaska",
    "AL": "Alabama",
    "AR": "Arkansas",
    "AS": "American Samoa",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "District of Columbia",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "GU": "Guam",
    "HI": "Hawaii",
    "IA": "Iowa",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "ME": "Maine",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "MP": "Northern Mariana Islands",
    "MS": "Mississippi",
    "MT": "Montana",
    "NA": "National",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "VI": "Virgin Islands",
    "VT": "Vermont",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming"
}
```
<!-- /excerpt:wildfire.1740.1 -->

## 文件：`wildfire/input/usa.gpkg`

来源：`data/kramabench/data/wildfire/input/usa.gpkg`；17,379,328 字节；扩展名 `.gpkg`。

摘录范围：gpkg_layer_names_and_field_names_readonly。

<!-- excerpt:wildfire.1741.1 chars:1944 -->
```json
[
  {
    "layer_name": "usa_adm2",
    "data_type": "features",
    "fields": [
      {
        "name": "fid",
        "type": "INTEGER"
      },
      {
        "name": "geom",
        "type": "MULTIPOLYGON"
      },
      {
        "name": "adm2_id",
        "type": "TEXT"
      },
      {
        "name": "adm2_src",
        "type": "TEXT"
      },
      {
        "name": "adm2_name",
        "type": "TEXT"
      },
      {
        "name": "adm2_name1",
        "type": "TEXT"
      },
      {
        "name": "adm2_name2",
        "type": "TEXT"
      },
      {
        "name": "adm1_id",
        "type": "TEXT"
      },
      {
        "name": "adm1_src",
        "type": "TEXT"
      },
      {
        "name": "adm1_name",
        "type": "TEXT"
      },
      {
        "name": "adm1_name1",
        "type": "TEXT"
      },
      {
        "name": "adm1_name2",
        "type": "TEXT"
      },
      {
        "name": "adm0_id",
        "type": "TEXT"
      },
      {
        "name": "adm0_src",
        "type": "TEXT"
      },
      {
        "name": "adm0_name",
        "type": "TEXT"
      },
      {
        "name": "adm0_name1",
        "type": "TEXT"
      },
      {
        "name": "adm0_name2",
        "type": "TEXT"
      },
      {
        "name": "src_lvl",
        "type": "INTEGER"
      },
      {
        "name": "src_lang",
        "type": "TEXT"
      },
      {
        "name": "src_lang1",
        "type": "TEXT"
      },
      {
        "name": "src_lang2",
        "type": "TEXT"
      },
      {
        "name": "src_date",
        "type": "DATE"
      },
      {
        "name": "src_update",
        "type": "DATE"
      },
      {
        "name": "src_name",
        "type": "TEXT"
      },
      {
        "name": "src_lic",
        "type": "TEXT"
      },
      {
        "name": "src_url",
        "type": "TEXT"
      },
      {
        "name": "src_grp",
        "type": "TEXT"
      }
    ]
  }
]
```
<!-- /excerpt:wildfire.1741.1 -->

## 文件：`wildfire/input/wildfire_total_fires_p45_54.csv`

来源：`data/kramabench/data/wildfire/input/wildfire_total_fires_p45_54.csv`；706 字节；扩展名 `.csv`。

摘录范围：first_5_physical_lines。

<!-- excerpt:wildfire.1742.1 chars:69 -->
```text
State,Total Fires
Alabama,1525
Alaska,377
Arizona,2191
Arkansas,1219
```
<!-- /excerpt:wildfire.1742.1 -->

## 本地仓库说明文档：`/home/katherine/dac/benchmarks/KramaBench/README.md`

摘录范围：full_text；仓库内路径 `README.md`。

原文片段 1，定位：{}。

<!-- excerpt:wildfire.repo.1780 chars:8815 -->
````text
# KramaBench
*KramaBench* is an open-source benchmark for **end-to-end data-science agents**.
Unlike question-answer–only corpora, each task in KramaBench asks a system to build a *complete* data pipeline: load raw files, clean them, transform them, and compute a final answer.
Because ground-truth code is provided, KramaBench can evaluate both the **quality of the final answer** *and* the **correctness of intermediate steps**.

![Benchmark Overview](benchmark-overview.png)

### Systems leaderboard
Overall evaluation results by domain for KramaBench:

| Variant                       | Model            | Archaeology | Astronomy | Biomedical | Environment | Legal | Wildfire | **Overall** |
| ----------------------------- | ---------------- | ----------: | --------: | ---------: | ----------: | ------: | -------: | ----------: |
| **Naive**                     | GPT-o3           | 25% | 1.73% | 3.50% | 1.35% | 3.35 % | 24.87 % | **9.64 %** |
|                               | GPT-4o           | 0.00% | 1.41% | 1.98% | 0.45% | 1.46 % | 1.45 % | **1.62 %** |
|                              | Claude-3.5       | 16.67% | 1.62% | 2.87% | 1.17% | 7.33 % | 13.63 % | **7.45 %** |
|                              | Llama-3 Instruct | 0.00% | 1.43% | 1.70% | 0.98% | 1.37 % | 1.44 % | **1.19 %** |
|                              | DeepSeek-R1      | 0.00% | 1.50% | 2.49% | 2.60% | 1.61 % | 6.46 % | **3.14 %** |
|                              | Qwen-2 Coder     | 0.00% | 1.37% | 2.02% | 1.07% | 1.44 % | 13.68 % | **3.72 %** |
| **DS-GURU (simple)**          | GPT-o3           | 25% | 3.00% | 8.63% | 7.66% | 19.15 % | 45.95 % | **20.80 %** |
|                              | GPT-4o           | 8.33% | 1.40% | 9.38% | 2.60% | 2.74 % | 19.39 % | **7.61 %** |
|                              | Claude-3.5       | 0.00% | 4.15% | 2.15% | 6.21% | 6.68 % | 34.99 % | **10.85 %** |
|                              | Llama-3 Instruct | 0.00% | 1.42% | 10.38% | 0.98% | 5.48 % | 9.81 % | **4.81 %** |
|                              | DeepSeek-R1      | 0.00% | 1.57% | 3.39% | 2.60% | 8.30 % | 14.81 % | **6.35 %** |
|                              | Qwen-2 Coder     | 0.00% | 1.36% | 2.22% | 12.59% | 1.15 % | 16.48 % | **6.43 %** |
| **DS-GURU (self-correcting)** | GPT-o3           | 25% | 3.53% | 8.95% | 19.60% | 13.89 % | 50.73 % | **22.08 %** |
|                              | GPT-4o           | 16.67% | 2.76% | 8.97% | 2.60% | 2.80 % | 17.18 % | **8.28 %** |
|                              | Claude-3.5       | 16.67% | 1.52% | 1.96% | 11.21% | 7.01 % | 39.16 % | **14.35 %** |
|                              | Llama-3 Instruct | 0.00% | 1.35% | 6.98% | 0.93% | 2.15 % | 14.49 % | **4.48 %** |
|                              | DeepSeek-R1      | 8.33% | 2.64% | 2.87% | 19.08% | 8.39 % | 30.29 % | **6.34 %** |
|                              | Qwen-2 Coder     | 8.33% | 2.40% | 4.35% | 12.64% | 9.06 % | 16.48 % | **9.98 %** |


## Breakdown of tasks per domain

| Domain      |  #Tasks | #Sub-tasks | % “Hard” | File count |   Raw size |
| ----------- | ------: | ---------: | ---------: | ---------: | ---------: |
| Archaeology |      12 |         71 |       50 % |          5 |     7.5 MB |
| Astronomy   |      12 |         68 |       50 % |      1 556 |     486 MB |
| Biomedical  |       9 |         38 |       67 % |          7 |     175 MB |
| Environment |      20 |        148 |       70 % |         37 |      31 MB |
| Legal       |      30 |        188 |       53 % |        136 |     1.3 MB |
| Wildfire    |      21 |        120 |       71 % |         23 |       1 GB |
| **Total**   | **104** |    **633** |   **61 %** |      1 764 | **1.7 GB** |

Hard tasks are tasks whose end-to-end solution requires advanced wrangling and transformation steps.

### What does a task look like?

1. **Natural-language prompt** (e.g. *“What is the average Potassium in ppm from the first and last time the study recorded people in the Maltese area?”*).
2. **Reference pipeline** broken into • *key functionalities* and • *natural-language sub-tasks* that test those functionalities individually.

---

### Structure of the repository

The main benchmark repository contains the following folders:
- `benchmark`: This folder contains the code to run the benchmark.
- `data`: This folder contains the input data to be used in solving the benchmark.
- `quickstart`: This folder contains the code for a quickstart example.
- `results`: This folder contains the output data from the different systems under test, produced while running benchmark.
- `scripts`: This folder contains helper scripts.
- `systems`: This folder contains the code to execute the different systems under test.
- `utils`: This folder contains utility code and helper scripts.
- `workload`: This folder contains the questions of the benchmark in JSON format.

## Installation

### Prerequisites
- Python 3.10 or higher
- pip or conda for package management

### Basic Installation (to run the evaluation harness)

```bash
git clone https://github.com/<you>/KramaBench.git
cd KramaBench
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install .
```

### Optional Dependencies

KramaBench uses a modular dependency system. Install only what you need:

**For running the single- and multi-agent systems baselines**:
```bash
pip install ".[baselines]"
```
Includes: litellm, anthropic, ollama, together, PyPDF2

**For development and testing**:
```bash
pip install ".[dev]"
```
Includes: pytest, ruff

**Install everything**:
```bash
pip install ".[all]"
```

## Quick-start — run the benchmark

The **evaluation harness** is a single script:

```bash
python evaluate.py \
  --sut YourSUT            \  # label for this run
  --workload legal          \  # domain to test
  --verbose
```

Key CLI flags (see `--help`):

| Flag                  | Default                       | Purpose                                                    |
| --------------------- | ----------------------------- | ---------------------------------------------------------- |
| `--sut`               | `YourSUT` | Arbitrary name for your System Under Test (SUT).           |
| `--workload`          | `legal`                       | Must match the domain contained in the workload file.      |
| `--use_system_cache`  | *(false)*                     | Re-use previous system outputs if they exist.              |
| `--skip_subtasks`     | *(false)*                     | Evaluate only the final answer (faster, but less insight). |

`evaluate.py` produces:

```
results/<SUT>/<workload>_measures_<timestamp>.csv   # fine-grained metrics
results/aggregated_results.csv                      # one-row-per-domain summary
```

---

## Dataset availability
The dataset can be also found on HuggingFace at [this link](https://huggingface.co/datasets/eugenie-y/KramaBench)
To use it in your scripts run 
```
from datasets import load_dataset

kramabench = load_dataset("eugenie-y/kramabench")
```


## Writing your own System Under Test (SUT)

1. **Implement a Python class** that, given
   `dataset_directory` and the JSON prompt, returns either:

   * the final answer, **or**
   * executable Python that produces the answer (recommended; lets the harness inspect intermediate values).
2. Place any temporary files under the path passed to you (`system_output_directory`).
3. Make your class importable by `benchmark/Benchmark`; then run `evaluate.py --sut YourClassName`.

---

## Scoring & metrics

For every task the harness logs:

* **Exact-match metrics**: BLEU & ROUGE for strings mean-relative-absolute-error for numerics.
* **LLM code-eval**: unit tests auto-generated from sub-task ground truth.
* **Bootstrapped rubric** that rewards partial credit when the model paraphrases the correct idea.

Aggregation logic lives in `aggregate_results()` inside `evaluate.py`.

---

## Baseline : DS-GURU

DS-GURU is a minimalist agent that:

1. **Samples rows** from every file in the domain lake.
2. Prompts an LLM with the task, the sample, and strict instructions on cleaning/typing.
3. **Executes** the generated Python, sending back errors/output to the LLM for one retry loop.&#x20;

---

## Citing KramaBench

If you use KramaBench in academic work, please cite the preprint:

```
@misc{lai2025KramaBench,
  title  = {KramaBench: Evaluating End-to-End Data-Science Agents},
  author = {Eugenie Lai and Gerardo Vitagliano and Ziyu Zhang and *et al.*},
  year   = {2025},
}
```

---

### Task structure

The structure of any task inside the `{domain}.json` file is the following:

```json
[
    {   "id": "{dataset-id}-{difficulty}-1",
        "query": "...",
        "answer": "...",
        "answer_type": "...",
        "data_sources": ["...", "..."],
        "subtasks":[{
            "..."
        }]
    }
]
``` 
````
<!-- /excerpt:wildfire.repo.1780 -->

