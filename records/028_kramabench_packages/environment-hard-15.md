# environment-hard-15

## 1. 题目信息

- 题号：`environment-hard-15`
- 领域：环境（`environment`）
- 难度：`hard`
- 答案类型：`string_exact`

- 官方评分状态：以下为旧基线适配器记录的原始 `score`，不是完整官方评测入口的新结果。

<!-- original:score chars:98 -->
```json
{
    "status": "scored",
    "source": "official_deterministic_definitions",
    "success": 0
  }
```
<!-- /original:score -->

来源：`records/027_kramabench_source/runs/20261018_hard_all_01/environment-hard-15_01/meta.json`；归档成员 `20261018_hard_all_01/environment-hard-15_01/messages.jsonl`、`steps.jsonl`；`data/kramabench/workload/environment.json` 中 `id=environment-hard-15`。

## 2. agent 收到的题面原文

来源字段：`meta.prompt_values.query`。

<!-- original:query chars:236 -->
```text
Which fresh water beach is the most polluted since 2020 (inclusive)? Most polluted is defined as highest average exceedance rate since 2020, and only consider the beaches that are measured in all the years from 2020 to 2023 (inclusive).
```
<!-- /original:query -->

## 3. 最终答案与标准答案

### agent 最终答案原文

<!-- original:final_answer chars:77 -->
```text
Damon Pond Beach (DCR) — average annual exceedance rate of 58.1% (2020–2023).
```
<!-- /original:final_answer -->

### 标准答案原文

<!-- original:gold_answer chars:22 -->
```text
Damon Pond Beach (DCR)
```
<!-- /original:gold_answer -->

## 4. 子任务

以下内容 agent 看不到，只供标注使用

### 子任务 1：environment-hard-15-1

问题原文：

<!-- original:subtask.1.query chars:95 -->
```text
Which beach names are included in the dataset?
**Expected answer:** ['Beach A', 'Beach B', ...]
```
<!-- /original:subtask.1.query -->

标准答案原文：

<!-- original:subtask.1.answer chars:18968 -->
```json
[
                    "Damon Pond Beach (DCR)",
                    "Beamans Pond - Day Use (DCR)",
                    "Beamans Pond - Campground (DCR)",
                    "Robinson Pond Beach (DCR)",
                    "Pearl Hill Pond Beach (DCR)",
                    "Waushakum Beach",
                    "Learned Pond Beach",
                    "Lake Quinsigamond-Regatta Point Beach (DCR)",
                    "Community Center Beach",
                    "Bass Pond ",
                    "Merrimac River - Bath House",
                    "Dunn Pond (DCR)",
                    "Peckham Pond ",
                    "Shannon Beach ",
                    "Camp Wilder ",
                    "Lake Wyola (DCR)",
                    "Hopkinton Reservoir-Main Beach (DCR)",
                    "Eagle Lake",
                    "Sherwood Forest - North Beach",
                    "Puffers Pond (AKA Factory Hollow Pond) ",
                    "Pearce Lake ",
                    "Cold River Pool (DCR)",
                    "Houghton's Pond ",
                    "Frye Pond Beach (DCR)",
                    "Mendon Town Beach",
                    "Lake Gardner",
                    "Hampton Ponds - Kingsley Beach (DCR)",
                    "Hopkinton Reservoir-Upper Beach (DCR)",
                    "Sherwood Forest - Grassy Beach",
                    "Ashland Reservoir-Main Beach (DCR)",
                    "Sutton Falls Camp",
                    "Lulu Pond Beach (DCR)",
                    "Seth's Pond ",
                    "Coes Pond Beach (Mill St.)",
                    "Hampton Ponds - Lamberts Beach (DCR)",
                    "Miacomet Pond",
                    "Paddle Club ",
                    "Pleasure Point",
                    "Lake Lashaway",
                    "Crow Hill Pond Beach (DCR)",
                    "Mauserts Pond (DCR)",
                    "Shore Park",
                    "Whitehall Pond Beach (DCR)",
                    "Fair Acres Country Day School",
                    "Medford Boat Club ",
                    "Furnace Colony",
                    "Silver Hill Assoc",
                    "Greenfield Municipal Bathing Beach",
                    "Picture Lake (Flax Pond)",
                    "Glen Devin Condominiums",
                    "Berry Pond Beach (DCR)",
                    "Chicopee Beach (DCR)",
                    "Stoddard Park",
                    "Watsons Pond (DCR)",
                    "Laurel Lake (DCR)",
                    "Upper Highland Lake - Day use area beach (DCR)",
                    "Benedict Pond Beach (DCR)",
                    "Morses Beach",
                    "Conway Swimming Pool",
                    "Camp Marshall Beach",
                    "Santuit Pond ",
                    "Upton Town Beach",
                    "St. Laurent Camp",
                    "Walden Pond - Main (DCR)",
                    "Lake Quinsigamond-Lake Park Beach (DCR)",
                    "Smith Pond",
                    "Arrive Lunenburg (Lake Whalom)",
                    "Whispering Pines Condo Association (Muddy Pond)",
                    "York Lake Beach (DCR)",
                    "Freetown Town Beach",
                    "Luther Hill Park",
                    "Homestead Residents Association (Crocker Pond)",
                    "Farm Pond",
                    "Saxonville Beach",
                    "Camp Gannet (Everwood/upper)",
                    "Camp Danbee",
                    "Hickory Hills (Brookview)",
                    "Indian Lake Public Beach (Sherburne Ave)",
                    "Crystal Lake",
                    "Hickory Hills (Hemlock Drive)",
                    "Ames Pond",
                    "Sherwood Forest - Boat Beach",
                    "Massaconet Shores",
                    "Hinkley ",
                    "Wells State Park - Walker Pond Beach (DCR)",
                    "Sesachacha Pond",
                    "Damon Pond Association Beach",
                    "Memorial Beach (Dug Pond) ",
                    "Becket Woods Road District - Beach",
                    "Forest Lake: Swimming Beach",
                    "Camp Russell",
                    "Lunenburg Town Beach",
                    "Ashfield Park Beach",
                    "Silver Pond Beach",
                    "Indian Lake Assoc - Niskayuna Beach",
                    "Cedar Lake Recreation Area",
                    "Sherwood Forest - Will Scarlett",
                    "Lakeland Beach",
                    "White Pines Condos (Stockbridge Bowl)",
                    "Wallum Lake (DCR)",
                    "Ice House Pond",
                    "Wayland Town Beach ",
                    "Tyngsborough Town Beach",
                    "Sand Shores Association",
                    "Briarwood Mashpee Association",
                    "Little Sandy",
                    "Long Pond (Depot St.)",
                    "Long Cove (Fresh)",
                    "Camp Yomechas",
                    "Indian Ranch",
                    "Lake Chauncy Beach",
                    "Wrights Pond ",
                    "Tom Denney Nature Camp",
                    "John's Pond",
                    "Edwards Town Beach",
                    "Lake Dennison State Park (DCR) ",
                    "John's Pond North Cove Association",
                    "Halifax Beach Association",
                    "Silver Lake",
                    "Lake Wyola Association: West Beach",
                    "Camp Good News",
                    "Lake Pearl Restaurant",
                    "White Island Association",
                    "Lenox Town Beach (Laurel Lake)",
                    "Gull Pond Landing",
                    "Mascuppic",
                    "Collette Drive Beach",
                    "Sharon Town Beach ",
                    "Everwood Day Camp (Everwood/lower)",
                    "Santuit Pond Estates Association",
                    "Freeman Lake ",
                    "Indian Memorial",
                    "Stockbridge Town Beach (Stockbridge Bowl)",
                    "Snake Pond",
                    "Cochituate State Park Beach (DCR)",
                    "Nutting Lake - Micozzi Beach ",
                    "Walden Pond - Red Cross (DCR) ",
                    "Sampson's Pond",
                    "John's Pond Estates Association (Fred's)",
                    "Walker Pond - Main Beach",
                    "Morton Park ",
                    "Shangri-La",
                    "White Pond Cottages",
                    "Pinecrest Beach Improvement Association (Jenkins Pond)",
                    "Fresh Pond ",
                    "Camp Avoda",
                    "Dunroamin Park and Cottages",
                    "Mirror Lake",
                    "Camp Sequena ",
                    "Lochstead Association",
                    "Queen Sewell Pond",
                    "Oldham Pond",
                    "Twin Lakes Condominiums",
                    "Water-by Estates Homeowners Association",
                    "Sun Retreats Cape Cod (Round Pond)",
                    "Camp Hi Rock - Main Beach",
                    "Mares Pond Association",
                    "Pinewood Lodge Campground",
                    "Duck Pond",
                    "Sunset Beach",
                    "Attaquin Park (Mashpee-Wakeby Pond)",
                    "Wequaquet Estates Beach Association",
                    "Annawon Drive",
                    "Cordially Colony",
                    "Plunkett Lake Beach",
                    "Thousand Trails",
                    "Orange Town Beach ",
                    "Lee Town Beach",
                    "Long Pond (Long Pond Drive)",
                    "Hammond Acres",
                    "McDonald Beach",
                    "Camp Resolute ",
                    "Crystal Pond Homeowners Assoc Beach",
                    "Beachwood Assoc. ",
                    "North Pond Beach (DCR)",
                    "Flax Pond (DCR)",
                    "Roger's Beach",
                    "King's Campground",
                    "Intercolonial Club of Marlborough",
                    "Windsor Lake",
                    "Richardson",
                    "Sandbar Beach Club",
                    "Camp Taconic Beach",
                    "Sherwood Forest - Arrow Beach",
                    "Crocker Pond",
                    "Camp Overflow Beach",
                    "Sherwood Greens Road District Beach ",
                    "Bell Pond Beach",
                    "S.P.E.N.A. Beach",
                    "North Beach ",
                    "Danvers YMCA Daycamp",
                    "Chilson Beach",
                    "Peter's Pond Town Park 1",
                    "Merino Pond",
                    "Camp Mah-kee-nac",
                    "Flax Pond",
                    "Sweatt Beach",
                    "Cooper's Pond",
                    "Sandpointe Shores Association Inc. - Rock Hollow",
                    "Lake Waushacum",
                    "American Legion Park",
                    "Ellis Beach",
                    "Sunset Lake ",
                    "Centennial Grove",
                    "Mashpee Shores Association",
                    "Lithuanian Outing Assoc.",
                    "Wequaquet Lake Yacht Club",
                    "Woods Pond Cabins",
                    "Fells Pond Village Peninsula Council",
                    "Higgins Pond",
                    "Long Pond (Cahoon Street)",
                    "Jimmy's Beach (Wequaquet Heights Association) ",
                    "Gull Pond (2) - Steele Rd.",
                    "Hathaway's Pond",
                    "Lovell's Pond",
                    "Richmond Pond Association",
                    "Long Pond Farms Neighborhood Association",
                    "Lawrence Pond Village Campground",
                    "Lakewood Hills Property Owners Association",
                    "Buck's Pond",
                    "Pout Pond Beach",
                    "Wequaquet Lake Town",
                    "Blueberry Hills Property Owners Association",
                    "Cranberry Bog Homeowner's Association (Big Sandy Pond)",
                    "Blackmore Pond",
                    "Craig Road Beach",
                    "Coonamessett Pond",
                    "Holly Point Beach and Tennis Association",
                    "Sand Pond",
                    "Wianno Club (Crystal Lake)",
                    "Slough Pond",
                    "Stetson",
                    "Robinwood Homeowners Association (Owl Pond)",
                    "Hood Pond-boat ramp",
                    "Baird Center (Bloody Pond)",
                    "Baby Beach Lost Lake",
                    "Plainfield Pond",
                    "Otis Town Beach",
                    "Village Green Family Campground",
                    "Littleton Town Beach",
                    "Lake Garfield",
                    "Upper Mill Pond",
                    "East Boston Camps - Girls Beach",
                    "Center Lake Estates Beach",
                    "Henry F Collins Beach",
                    "Nabnassett American Legion",
                    "Pilgrim Lake",
                    "Asnacomet Pond Beach (DCR) ",
                    "Berry's Grove Campground",
                    "Curlew Pond (DCR)",
                    "Lake Mansfield",
                    "Richard P. Sharon Beach",
                    "Cliff Pond (DCR) ",
                    "Colonial Park",
                    "Rowe Town Beach at Pelham Park ",
                    "East Boston Camps - Boys Beach",
                    "Sandy Beach ",
                    "Sherwood Forest - Excalibur",
                    "Dennis Pond",
                    "Hilltop",
                    "Camp Clark YMCA - Hyles Pond",
                    "Annursnac Hill Assoc.",
                    "Mohawk Estates ",
                    "Pleasant Pond Beach",
                    "Indian Lake Assoc - Dam Beach ",
                    "Musante Beach",
                    "Camp Becket - Main Beach",
                    "Lakeside",
                    "Walker Pond (Oak Cove)",
                    "Ellis Haven",
                    "Plugs Pond ",
                    "Beechwood Landing Property Owners Association",
                    "John's Pond (Public) ",
                    "Long Pond",
                    "Pomps Pond ",
                    "Summer Beach ",
                    "White Pond Town Landing",
                    "Indian Lake Assoc - Boulder Beach",
                    "Indian Lake Assoc - Forest Beach",
                    "Rolling Ridge Farm Homeowners Association (Lawrence Pond)",
                    "Holmes Street",
                    "Island Grove Beach",
                    "Italian-American Sporting Club",
                    "Jemima Pond",
                    "Horse Pond",
                    "Hood's Pond",
                    "Indian Head Resort",
                    "Beacon Park Condominiums",
                    "Barrett Pond (DCR)",
                    "Goose Pond",
                    "Sunrise Beach",
                    "Goose Pond at Leisure Lee Rd.",
                    "Card Pond Beach",
                    "Charge Pond (DCR)",
                    "Center Pond Beach",
                    "Cooper Creek HOA",
                    "College Pond Day Use (DCR)",
                    "Lancaster Town Beach",
                    "Sheep Pond Landing",
                    "Sheep Pond Beach Association",
                    "Shady Point Campground",
                    "Cranberry Cove (aka Camp Kiwanee)",
                    "Country Club of Pittsfield",
                    "Scargo Lake",
                    "Sandy Beach (NIA)",
                    "Sandy Pond Campground",
                    "Sandy Shore Association (Aunt Edies Pond) ",
                    "Seymour Pond",
                    "Shady Lane Homeowners Association",
                    "Sandpointe Shores Association Inc. - Whitecaps",
                    "Summer Village Main Beach",
                    "Wiley Park",
                    "Schoolhouse Pond",
                    "South Shore YMCA - Triangle Pond",
                    "Stiles Pond Beach",
                    "South Beach - Beaver Lake",
                    "Sichols",
                    "Wildwood - Fox Den",
                    "Wildwood - Lakeside",
                    "The Trustees  - Lowell Holly (Mashpee Pond)",
                    "The Trustees  - Lowell Holly (Wakeby Pond)",
                    "Thunderbridge ",
                    "Treasure Island Condominiums",
                    "Tunxis Club",
                    "The Trail at Big Alum Lake Association Beach",
                    "Templeton Fish and Game Club",
                    "The Pines",
                    "Camp Stevenson/Witawentin",
                    "Camp Stepping Stone",
                    "Camp Lyndon",
                    "Camp Romaca ",
                    "Camp Wind-in-the-Pines ",
                    "Camp Winadu",
                    "Wildwood - Meadow",
                    "Wildwood - Main Beach",
                    "Fearings Pond (DCR) ",
                    "East Beach - Beaver Lake",
                    "East Boston Camps - Day Care",
                    "Blueberry Hill Camp (Curlew Pond)",
                    "West Beach - Beaver Lake",
                    "Camp Wingate - Kirland",
                    "Wallum Lake Terrace",
                    "Berkshire Lake Estates",
                    "Wakeby Pond",
                    "Valley Pond",
                    "Upper Highland Lake - Campers Beach (DCR)",
                    "Wildwood - Otter Pond Beach",
                    "Forge Village Beach",
                    "Ashumet Valley Property Owners, Inc./Holly Sands Homeowners Corp.",
                    "Arcand Park Beach",
                    "Wales Town Beach",
                    "Lingan Street",
                    "Little Sandy Pond",
                    "Camp Lowe Beach",
                    "Breezy Picnic Grounds",
                    "Camp Farley (Mashpee-Wakeby Pond)",
                    "Camp Burgess",
                    "Camp Hayward",
                    "Camp Hi Rock - Bear Rock Beach",
                    "Pinecrest Property Owners Assoc.",
                    "Princess Beach-Scargo Lake",
                    "Pontoosuc Lake - Decom Beach",
                    "Plymouth Estates",
                    "Bolton Town Beach",
                    "Richmond Town Beach",
                    "Otis Reservoir Beach (DCR)",
                    "Peter's Pond RV Park ",
                    "White Pond Assoc",
                    "Camp Watitoh Beach",
                    "Richmond Shores South Pond",
                    "NARA Beach",
                    "Moores Pond Beach",
                    "Noble's Cove Beach",
                    "Onota Lake - Controy Pavillion",
                    "Mountain Grove Assoc. Beach",
                    "Nauset Haven Condo Association (Minister's Pond)",
                    "Lake House at Laurel Lake",
                    "Lake Wyola Association: East Beach",
                    "Lake Manchaug Camping",
                    "Lake Wyola Association: North Beach",
                    "Lakeside Meadows",
                    "Lakefield Farms Trust",
                    "Great Pond",
                    "Lyman Lane",
                    "Memorial Beach ",
                    "Massapoag Yacht Club",
                    "Maple Park Campground ",
                    "Onota Lake - Decom Beach",
                    "Onota Lake - Public Beach at Burbank Park",
                    "Minister's Pond",
                    "Middle Pond",
                    "North Beach (NIA)",
                    "Hickory Hills (Island Rd.)",
                    "Marylou's Beach (NIA)",
                    "Herring Pond",
                    "Heart Pond",
                    "Hinkley's Pond",
                    "Long Pond (Rte 124)",
                    "Regency Drive Homeowners Association ",
                    "Hartsuff Park",
                    "Hamblin's Pond",
                    "Hedges Pond",
                    "Halcyon Condominiums/Horse Pond Corporation",
                    "Gull Pond",
                    "Grove",
                    "Grotonwood Camp",
                    "Groton Town Beach (Sargisson Beach)",
                    "Grossman Beach",
                    "Grew's Pond",
                    "Great Sand Lakes Association - Vacation Ln. (John Joseph Pond)",
                    "Great Sand Lakes Association - Clearwater Dr. (Bucks Pond)",
                    "Lake Boone",
                    "Lake Attitash - A.L.S.I.A.",
                    "Kildeer Island (AKA Sandy Shore)",
                    "Joshua's Pond"
                ]
```
<!-- /original:subtask.1.answer -->

### 子任务 2：environment-hard-15-2

问题原文：

<!-- original:subtask.2.query chars:46 -->
```text
What beach types are included in the analysis?
```
<!-- /original:subtask.2.query -->

标准答案原文：

<!-- original:subtask.2.answer chars:5 -->
```text
Fresh
```
<!-- /original:subtask.2.answer -->

### 子任务 3：environment-hard-15-3

问题原文：

<!-- original:subtask.3.query chars:56 -->
```text
What character is used to split the 'Beach Name' column?
```
<!-- /original:subtask.3.query -->

标准答案原文：

<!-- original:subtask.3.answer chars:1 -->
```text
@
```
<!-- /original:subtask.3.answer -->

### 子任务 4：environment-hard-15-4

问题原文：

<!-- original:subtask.4.query chars:160 -->
```text
What is the per-beach sample count and violation count for all years? Return the values for 2020 as [beach name, sample count in 2020, exceedance count in 2020]
```
<!-- /original:subtask.4.query -->

标准答案原文：

<!-- original:subtask.4.answer chars:62505 -->
```json
[
                    [
                        "Damon Pond Beach (DCR)",
                        19,
                        13.0
                    ],
                    [
                        "Beamans Pond - Day Use (DCR)",
                        15,
                        2.0
                    ],
                    [
                        "Beamans Pond - Campground (DCR)",
                        15,
                        1.0
                    ],
                    [
                        "Robinson Pond Beach (DCR)",
                        16,
                        0.0
                    ],
                    [
                        "Pearl Hill Pond Beach (DCR)",
                        20,
                        4.0
                    ],
                    [
                        "Waushakum Beach",
                        11,
                        4.0
                    ],
                    [
                        "Learned Pond Beach",
                        10,
                        4.0
                    ],
                    [
                        "Lake Quinsigamond-Regatta Point Beach (DCR)",
                        21,
                        6.0
                    ],
                    [
                        "Community Center Beach",
                        19,
                        9.0
                    ],
                    [
                        "Bass Pond ",
                        10,
                        4.0
                    ],
                    [
                        "Merrimac River - Bath House",
                        19,
                        8.0
                    ],
                    [
                        "Dunn Pond (DCR)",
                        13,
                        2.0
                    ],
                    [
                        "Peckham Pond ",
                        19,
                        3.0
                    ],
                    [
                        "Shannon Beach ",
                        21,
                        2.0
                    ],
                    [
                        "Camp Wilder ",
                        6,
                        4.0
                    ],
                    [
                        "Lake Wyola (DCR)",
                        16,
                        0.0
                    ],
                    [
                        "Hopkinton Reservoir-Main Beach (DCR)",
                        17,
                        2.0
                    ],
                    [
                        "Eagle Lake",
                        6,
                        2.0
                    ],
                    [
                        "Sherwood Forest - North Beach",
                        18,
                        2.0
                    ],
                    [
                        "Puffers Pond (AKA Factory Hollow Pond) ",
                        36,
                        5.0
                    ],
                    [
                        "Pearce Lake ",
                        27,
                        10.0
                    ],
                    [
                        "Cold River Pool (DCR)",
                        17,
                        3.0
                    ],
                    [
                        "Houghton's Pond ",
                        16,
                        1.0
                    ],
                    [
                        "Frye Pond Beach (DCR)",
                        18,
                        2.0
                    ],
                    [
                        "Mendon Town Beach",
                        9,
                        0.0
                    ],
                    [
                        "Lake Gardner",
                        15,
                        3.0
                    ],
                    [
                        "Hampton Ponds - Kingsley Beach (DCR)",
                        17,
                        2.0
                    ],
                    [
                        "Hopkinton Reservoir-Upper Beach (DCR)",
                        19,
                        3.0
                    ],
                    [
                        "Sherwood Forest - Grassy Beach",
                        17,
                        0.0
                    ],
                    [
                        "Ashland Reservoir-Main Beach (DCR)",
                        17,
                        3.0
                    ],
                    [
                        "Sutton Falls Camp",
                        17,
                        3.0
                    ],
                    [
                        "Lulu Pond Beach (DCR)",
                        16,
                        3.0
                    ],
                    [
                        "Seth's Pond ",
                        26,
                        12.0
                    ],
                    [
                        "Coes Pond Beach (Mill St.)",
                        24,
                        11.0
                    ],
                    [
                        "Hampton Ponds - Lamberts Beach (DCR)",
                        17,
                        2.0
                    ],
                    [
                        "Miacomet Pond",
                        12,
                        1.0
                    ],
                    [
                        "Paddle Club ",
                        10,
                        2.0
                    ],
                    [
                        "Pleasure Point",
                        16,
                        1.0
                    ],
                    [
                        "Lake Lashaway",
                        12,
                        1.0
                    ],
                    [
                        "Crow Hill Pond Beach (DCR)",
                        18,
                        5.0
                    ],
                    [
                        "Mauserts Pond (DCR)",
                        16,
                        1.0
                    ],
                    [
                        "Shore Park",
                        14,
                        5.0
                    ],
                    [
                        "Whitehall Pond Beach (DCR)",
                        17,
                        1.0
                    ],
                    [
                        "Fair Acres Country Day School",
                        7,
                        2.0
                    ],
                    [
                        "Medford Boat Club ",
                        35,
                        6.0
                    ],
                    [
                        "Furnace Colony",
                        12,
                        0.0
                    ],
                    [
                        "Silver Hill Assoc",
                        17,
                        1.0
                    ],
                    [
                        "Greenfield Municipal Bathing Beach",
                        13,
                        1.0
                    ],
                    [
                        "Picture Lake (Flax Pond)",
                        16,
                        2.0
                    ],
                    [
                        "Glen Devin Condominiums",
                        14,
                        1.0
                    ],
                    [
                        "Berry Pond Beach (DCR)",
                        17,
                        1.0
                    ],
                    [
                        "Chicopee Beach (DCR)",
                        16,
                        2.0
                    ],
                    [
                        "Stoddard Park",
                        16,
                        1.0
                    ],
                    [
                        "Watsons Pond (DCR)",
                        19,
                        3.0
                    ],
                    [
                        "Laurel Lake (DCR)",
                        16,
                        0.0
                    ],
                    [
                        "Upper Highland Lake - Day use area beach (DCR)",
                        18,
                        2.0
                    ],
                    [
                        "Benedict Pond Beach (DCR)",
                        15,
                        0.0
                    ],
                    [
                        "Morses Beach",
                        15,
                        1.0
                    ],
                    [
                        "Conway Swimming Pool",
                        16,
                        0.0
                    ],
                    [
                        "Camp Marshall Beach",
                        9,
                        2.0
                    ],
                    [
                        "Santuit Pond ",
                        29,
                        1.0
                    ],
                    [
                        "Upton Town Beach",
                        18,
                        5.0
                    ],
                    [
                        "St. Laurent Camp",
                        32,
                        10.0
                    ],
                    [
                        "Walden Pond - Main (DCR)",
                        17,
                        2.0
                    ],
                    [
                        "Lake Quinsigamond-Lake Park Beach (DCR)",
                        17,
                        2.0
                    ],
                    [
                        "Smith Pond",
                        14,
                        2.0
                    ],
                    [
                        "Arrive Lunenburg (Lake Whalom)",
                        17,
                        4.0
                    ],
                    [
                        "Whispering Pines Condo Association (Muddy Pond)",
                        11,
                        0.0
                    ],
                    [
                        "York Lake Beach (DCR)",
                        15,
                        0.0
                    ],
                    [
                        "Freetown Town Beach",
                        14,
                        2.0
                    ],
                    [
                        "Luther Hill Park",
                        13,
                        0.0
                    ],
                    [
                        "Homestead Residents Association (Crocker Pond)",
                        14,
                        1.0
                    ],
                    [
                        "Farm Pond",
                        16,
                        2.0
                    ],
                    [
                        "Saxonville Beach",
                        8,
                        1.0
                    ],
                    [
                        "Camp Gannet (Everwood/upper)",
                        12,
                        1.0
                    ],
                    [
                        "Camp Danbee",
                        11,
                        1.0
                    ],
                    [
                        "Hickory Hills (Brookview)",
                        13,
                        1.0
                    ],
                    [
                        "Indian Lake Public Beach (Sherburne Ave)",
                        12,
                        2.0
                    ],
                    [
                        "Crystal Lake",
                        43,
                        5.0
                    ],
                    [
                        "Hickory Hills (Hemlock Drive)",
                        15,
                        3.0
                    ],
                    [
                        "Ames Pond",
                        10,
                        1.0
                    ],
                    [
                        "Sherwood Forest - Boat Beach",
                        17,
                        0.0
                    ],
                    [
                        "Massaconet Shores",
                        12,
                        2.0
                    ],
                    [
                        "Hinkley ",
                        28,
                        3.0
                    ],
                    [
                        "Wells State Park - Walker Pond Beach (DCR)",
                        18,
                        2.0
                    ],
                    [
                        "Sesachacha Pond",
                        11,
                        0.0
                    ],
                    [
                        "Damon Pond Association Beach",
                        9,
                        2.0
                    ],
                    [
                        "Memorial Beach (Dug Pond) ",
                        17,
                        2.0
                    ],
                    [
                        "Becket Woods Road District - Beach",
                        16,
                        1.0
                    ],
                    [
                        "Forest Lake: Swimming Beach",
                        13,
                        0.0
                    ],
                    [
                        "Camp Russell",
                        13,
                        2.0
                    ],
                    [
                        "Lunenburg Town Beach",
                        9,
                        1.0
                    ],
                    [
                        "Ashfield Park Beach",
                        12,
                        1.0
                    ],
                    [
                        "Silver Pond Beach",
                        11,
                        3.0
                    ],
                    [
                        "Indian Lake Assoc - Niskayuna Beach",
                        17,
                        0.0
                    ],
                    [
                        "Cedar Lake Recreation Area",
                        21,
                        3.0
                    ],
                    [
                        "Sherwood Forest - Will Scarlett",
                        17,
                        0.0
                    ],
                    [
                        "Lakeland Beach",
                        16,
                        0.0
                    ],
                    [
                        "White Pines Condos (Stockbridge Bowl)",
                        16,
                        0.0
                    ],
                    [
                        "Wallum Lake (DCR)",
                        17,
                        1.0
                    ],
                    [
                        "Ice House Pond",
                        13,
                        1.0
                    ],
                    [
                        "Wayland Town Beach ",
                        40,
                        1.0
                    ],
                    [
                        "Tyngsborough Town Beach",
                        19,
                        3.0
                    ],
                    [
                        "Long Cove (Fresh)",
                        14,
                        2.0
                    ],
                    [
                        "Briarwood Mashpee Association",
                        14,
                        2.0
                    ],
                    [
                        "Long Pond (Depot St.)",
                        14,
                        0.0
                    ],
                    [
                        "Little Sandy",
                        12,
                        0.0
                    ],
                    [
                        "Sand Shores Association",
                        13,
                        1.0
                    ],
                    [
                        "Camp Yomechas",
                        10,
                        1.0
                    ],
                    [
                        "Indian Ranch",
                        9,
                        0.0
                    ],
                    [
                        "Lake Chauncy Beach",
                        14,
                        3.0
                    ],
                    [
                        "Wrights Pond ",
                        35,
                        5.0
                    ],
                    [
                        "Tom Denney Nature Camp",
                        5,
                        0.0
                    ],
                    [
                        "John's Pond",
                        16,
                        2.0
                    ],
                    [
                        "Edwards Town Beach",
                        11,
                        1.0
                    ],
                    [
                        "Lake Dennison State Park (DCR) ",
                        33,
                        1.0
                    ],
                    [
                        "Lake Wyola Association: West Beach",
                        15,
                        3.0
                    ],
                    [
                        "Camp Good News",
                        9,
                        0.0
                    ],
                    [
                        "John's Pond North Cove Association",
                        15,
                        1.0
                    ],
                    [
                        "Halifax Beach Association",
                        14,
                        0.0
                    ],
                    [
                        "Silver Lake",
                        12,
                        0.0
                    ],
                    [
                        "Lake Pearl Restaurant",
                        18,
                        0.0
                    ],
                    [
                        "White Island Association",
                        14,
                        1.0
                    ],
                    [
                        "Lenox Town Beach (Laurel Lake)",
                        13,
                        1.0
                    ],
                    [
                        "Gull Pond Landing",
                        17,
                        1.0
                    ],
                    [
                        "Mascuppic",
                        18,
                        1.0
                    ],
                    [
                        "Collette Drive Beach",
                        11,
                        0.0
                    ],
                    [
                        "Sharon Town Beach ",
                        28,
                        4.0
                    ],
                    [
                        "Everwood Day Camp (Everwood/lower)",
                        11,
                        0.0
                    ],
                    [
                        "Santuit Pond Estates Association",
                        14,
                        0.0
                    ],
                    [
                        "Freeman Lake ",
                        11,
                        2.0
                    ],
                    [
                        "Indian Memorial",
                        17,
                        1.0
                    ],
                    [
                        "Stockbridge Town Beach (Stockbridge Bowl)",
                        17,
                        1.0
                    ],
                    [
                        "Snake Pond",
                        12,
                        1.0
                    ],
                    [
                        "Cochituate State Park Beach (DCR)",
                        18,
                        2.0
                    ],
                    [
                        "Nutting Lake - Micozzi Beach ",
                        18,
                        1.0
                    ],
                    [
                        "Sampson's Pond",
                        15,
                        0.0
                    ],
                    [
                        "John's Pond Estates Association (Fred's)",
                        11,
                        0.0
                    ],
                    [
                        "Walden Pond - Red Cross (DCR) ",
                        36,
                        6.0
                    ],
                    [
                        "Walker Pond - Main Beach",
                        17,
                        0.0
                    ],
                    [
                        "Morton Park ",
                        26,
                        0.0
                    ],
                    [
                        "Shangri-La",
                        13,
                        0.0
                    ],
                    [
                        "White Pond Cottages",
                        15,
                        1.0
                    ],
                    [
                        "Pinecrest Beach Improvement Association (Jenkins Pond)",
                        15,
                        1.0
                    ],
                    [
                        "Fresh Pond ",
                        18,
                        0.0
                    ],
                    [
                        "Dunroamin Park and Cottages",
                        14,
                        0.0
                    ],
                    [
                        "Mirror Lake",
                        14,
                        2.0
                    ],
                    [
                        "Camp Avoda",
                        7,
                        1.0
                    ],
                    [
                        "Camp Sequena ",
                        44,
                        0.0
                    ],
                    [
                        "Lochstead Association",
                        15,
                        1.0
                    ],
                    [
                        "Pinewood Lodge Campground",
                        14,
                        0.0
                    ],
                    [
                        "Queen Sewell Pond",
                        14,
                        0.0
                    ],
                    [
                        "Attaquin Park (Mashpee-Wakeby Pond)",
                        14,
                        0.0
                    ],
                    [
                        "Twin Lakes Condominiums",
                        16,
                        0.0
                    ],
                    [
                        "Mares Pond Association",
                        14,
                        0.0
                    ],
                    [
                        "Oldham Pond",
                        12,
                        0.0
                    ],
                    [
                        "Duck Pond",
                        16,
                        0.0
                    ],
                    [
                        "Camp Hi Rock - Main Beach",
                        11,
                        0.0
                    ],
                    [
                        "Sun Retreats Cape Cod (Round Pond)",
                        15,
                        2.0
                    ],
                    [
                        "Sunset Beach",
                        16,
                        0.0
                    ],
                    [
                        "Water-by Estates Homeowners Association",
                        14,
                        0.0
                    ],
                    [
                        "Wequaquet Estates Beach Association",
                        14,
                        0.0
                    ],
                    [
                        "Annawon Drive",
                        16,
                        1.0
                    ],
                    [
                        "Cordially Colony",
                        18,
                        1.0
                    ],
                    [
                        "Plunkett Lake Beach",
                        15,
                        0.0
                    ],
                    [
                        "Hammond Acres",
                        14,
                        0.0
                    ],
                    [
                        "Thousand Trails",
                        16,
                        1.0
                    ],
                    [
                        "Long Pond (Long Pond Drive)",
                        16,
                        2.0
                    ],
                    [
                        "Lee Town Beach",
                        12,
                        0.0
                    ],
                    [
                        "McDonald Beach",
                        14,
                        0.0
                    ],
                    [
                        "Orange Town Beach ",
                        16,
                        0.0
                    ],
                    [
                        "Camp Resolute ",
                        10,
                        0.0
                    ],
                    [
                        "Crystal Pond Homeowners Assoc Beach",
                        17,
                        0.0
                    ],
                    [
                        "Beachwood Assoc. ",
                        17,
                        1.0
                    ],
                    [
                        "Roger's Beach",
                        14,
                        0.0
                    ],
                    [
                        "Flax Pond (DCR)",
                        16,
                        0.0
                    ],
                    [
                        "Intercolonial Club of Marlborough",
                        14,
                        0.0
                    ],
                    [
                        "Windsor Lake",
                        17,
                        1.0
                    ],
                    [
                        "North Pond Beach (DCR)",
                        15,
                        0.0
                    ],
                    [
                        "King's Campground",
                        1,
                        0.0
                    ],
                    [
                        "Camp Taconic Beach",
                        9,
                        1.0
                    ],
                    [
                        "Sandbar Beach Club",
                        18,
                        2.0
                    ],
                    [
                        "Sherwood Forest - Arrow Beach",
                        14,
                        0.0
                    ],
                    [
                        "Crocker Pond",
                        9,
                        1.0
                    ],
                    [
                        "Richardson",
                        18,
                        2.0
                    ],
                    [
                        "Camp Overflow Beach",
                        20,
                        1.0
                    ],
                    [
                        "Sherwood Greens Road District Beach ",
                        17,
                        0.0
                    ],
                    [
                        "Bell Pond Beach",
                        10,
                        1.0
                    ],
                    [
                        "S.P.E.N.A. Beach",
                        11,
                        0.0
                    ],
                    [
                        "North Beach ",
                        33,
                        0.0
                    ],
                    [
                        "Peter's Pond Town Park 1",
                        11,
                        0.0
                    ],
                    [
                        "Danvers YMCA Daycamp",
                        11,
                        1.0
                    ],
                    [
                        "Merino Pond",
                        11,
                        0.0
                    ],
                    [
                        "Chilson Beach",
                        11,
                        1.0
                    ],
                    [
                        "Camp Mah-kee-nac",
                        7,
                        0.0
                    ],
                    [
                        "Flax Pond",
                        30,
                        0.0
                    ],
                    [
                        "Lake Waushacum",
                        10,
                        0.0
                    ],
                    [
                        "American Legion Park",
                        12,
                        0.0
                    ],
                    [
                        "Ellis Beach",
                        11,
                        0.0
                    ],
                    [
                        "Sweatt Beach",
                        12,
                        1.0
                    ],
                    [
                        "Sandpointe Shores Association Inc. - Rock Hollow",
                        13,
                        0.0
                    ],
                    [
                        "Cooper's Pond",
                        15,
                        0.0
                    ],
                    [
                        "Fells Pond Village Peninsula Council",
                        14,
                        0.0
                    ],
                    [
                        "Centennial Grove",
                        13,
                        1.0
                    ],
                    [
                        "Wequaquet Lake Yacht Club",
                        11,
                        0.0
                    ],
                    [
                        "Woods Pond Cabins",
                        11,
                        0.0
                    ],
                    [
                        "Higgins Pond",
                        16,
                        0.0
                    ],
                    [
                        "Long Pond (Cahoon Street)",
                        14,
                        0.0
                    ],
                    [
                        "Lithuanian Outing Assoc.",
                        16,
                        0.0
                    ],
                    [
                        "Sunset Lake ",
                        12,
                        0.0
                    ],
                    [
                        "Mashpee Shores Association",
                        13,
                        0.0
                    ],
                    [
                        "Jimmy's Beach (Wequaquet Heights Association) ",
                        29,
                        1.0
                    ],
                    [
                        "Lakewood Hills Property Owners Association",
                        11,
                        0.0
                    ],
                    [
                        "Craig Road Beach",
                        10,
                        0.0
                    ],
                    [
                        "Cranberry Bog Homeowner's Association (Big Sandy Pond)",
                        14,
                        0.0
                    ],
                    [
                        "Gull Pond (2) - Steele Rd.",
                        16,
                        0.0
                    ],
                    [
                        "Long Pond Farms Neighborhood Association",
                        12,
                        0.0
                    ],
                    [
                        "Lovell's Pond",
                        13,
                        0.0
                    ],
                    [
                        "Richmond Pond Association",
                        15,
                        0.0
                    ],
                    [
                        "Coonamessett Pond",
                        14,
                        0.0
                    ],
                    [
                        "Holly Point Beach and Tennis Association",
                        14,
                        0.0
                    ],
                    [
                        "Buck's Pond",
                        14,
                        0.0
                    ],
                    [
                        "Wianno Club (Crystal Lake)",
                        14,
                        0.0
                    ],
                    [
                        "Lawrence Pond Village Campground",
                        14,
                        0.0
                    ],
                    [
                        "Blueberry Hills Property Owners Association",
                        14,
                        0.0
                    ],
                    [
                        "Wequaquet Lake Town",
                        13,
                        0.0
                    ],
                    [
                        "Pout Pond Beach",
                        15,
                        0.0
                    ],
                    [
                        "Sand Pond",
                        14,
                        0.0
                    ],
                    [
                        "Robinwood Homeowners Association (Owl Pond)",
                        12,
                        0.0
                    ],
                    [
                        "Slough Pond",
                        14,
                        0.0
                    ],
                    [
                        "Hathaway's Pond",
                        14,
                        1.0
                    ],
                    [
                        "Blackmore Pond",
                        13,
                        0.0
                    ],
                    [
                        "Stetson",
                        12,
                        0.0
                    ],
                    [
                        "Otis Town Beach",
                        14,
                        0.0
                    ],
                    [
                        "Littleton Town Beach",
                        14,
                        0.0
                    ],
                    [
                        "Plainfield Pond",
                        11,
                        0.0
                    ],
                    [
                        "Baby Beach Lost Lake",
                        14,
                        0.0
                    ],
                    [
                        "Upper Mill Pond",
                        15,
                        1.0
                    ],
                    [
                        "Baird Center (Bloody Pond)",
                        14,
                        0.0
                    ],
                    [
                        "Lake Garfield",
                        14,
                        0.0
                    ],
                    [
                        "Village Green Family Campground",
                        12,
                        0.0
                    ],
                    [
                        "Hood Pond-boat ramp",
                        10,
                        0.0
                    ],
                    [
                        "East Boston Camps - Girls Beach",
                        16,
                        0.0
                    ],
                    [
                        "East Boston Camps - Boys Beach",
                        16,
                        0.0
                    ],
                    [
                        "Lake Mansfield",
                        16,
                        0.0
                    ],
                    [
                        "Asnacomet Pond Beach (DCR) ",
                        16,
                        0.0
                    ],
                    [
                        "Curlew Pond (DCR)",
                        16,
                        0.0
                    ],
                    [
                        "Berry's Grove Campground",
                        17,
                        0.0
                    ],
                    [
                        "Cliff Pond (DCR) ",
                        32,
                        0.0
                    ],
                    [
                        "Center Lake Estates Beach",
                        16,
                        0.0
                    ],
                    [
                        "Colonial Park",
                        11,
                        0.0
                    ],
                    [
                        "Nabnassett American Legion",
                        16,
                        0.0
                    ],
                    [
                        "Richard P. Sharon Beach",
                        14,
                        0.0
                    ],
                    [
                        "Rowe Town Beach at Pelham Park ",
                        32,
                        0.0
                    ],
                    [
                        "Pilgrim Lake",
                        16,
                        0.0
                    ],
                    [
                        "Henry F Collins Beach",
                        14,
                        0.0
                    ],
                    [
                        "Sandy Beach ",
                        29,
                        0.0
                    ],
                    [
                        "Annursnac Hill Assoc.",
                        16,
                        0.0
                    ],
                    [
                        "Mohawk Estates ",
                        16,
                        0.0
                    ],
                    [
                        "Sherwood Forest - Excalibur",
                        17,
                        0.0
                    ],
                    [
                        "Hilltop",
                        17,
                        1.0
                    ],
                    [
                        "Camp Clark YMCA - Hyles Pond",
                        17,
                        1.0
                    ],
                    [
                        "Pleasant Pond Beach",
                        17,
                        1.0
                    ],
                    [
                        "Dennis Pond",
                        17,
                        1.0
                    ],
                    [
                        "Indian Lake Assoc - Dam Beach ",
                        18,
                        1.0
                    ],
                    [
                        "Musante Beach",
                        11,
                        0.0
                    ],
                    [
                        "Camp Becket - Main Beach",
                        18,
                        1.0
                    ],
                    [
                        "Lakeside",
                        12,
                        0.0
                    ],
                    [
                        "Walker Pond (Oak Cove)",
                        16,
                        0.0
                    ],
                    [
                        "Ellis Haven",
                        17,
                        0.0
                    ],
                    [
                        "Plugs Pond ",
                        10,
                        0.0
                    ],
                    [
                        "Beechwood Landing Property Owners Association",
                        26,
                        0.0
                    ],
                    [
                        "John's Pond (Public) ",
                        28,
                        0.0
                    ],
                    [
                        "Long Pond",
                        30,
                        0.0
                    ],
                    [
                        "Pomps Pond ",
                        42,
                        1.0
                    ],
                    [
                        "Summer Beach ",
                        36,
                        0.0
                    ],
                    [
                        "Upper Highland Lake - Campers Beach (DCR)",
                        16,
                        0.0
                    ],
                    [
                        "Tunxis Club",
                        15,
                        0.0
                    ],
                    [
                        "The Trustees  - Lowell Holly (Wakeby Pond)",
                        12,
                        0.0
                    ],
                    [
                        "Camp Farley (Mashpee-Wakeby Pond)",
                        1,
                        0.0
                    ],
                    [
                        "Wales Town Beach",
                        16,
                        0.0
                    ],
                    [
                        "The Pines",
                        15,
                        0.0
                    ],
                    [
                        "The Trail at Big Alum Lake Association Beach",
                        3,
                        0.0
                    ],
                    [
                        "The Trustees  - Lowell Holly (Mashpee Pond)",
                        12,
                        0.0
                    ],
                    [
                        "Wildwood - Meadow",
                        15,
                        0.0
                    ],
                    [
                        "Thunderbridge ",
                        7,
                        0.0
                    ],
                    [
                        "Treasure Island Condominiums",
                        11,
                        0.0
                    ],
                    [
                        "Lake Wyola Association: North Beach",
                        14,
                        0.0
                    ],
                    [
                        "Lake Wyola Association: East Beach",
                        14,
                        0.0
                    ],
                    [
                        "Lakeside Meadows",
                        16,
                        0.0
                    ],
                    [
                        "Lakefield Farms Trust",
                        13,
                        0.0
                    ],
                    [
                        "Horse Pond",
                        16,
                        0.0
                    ],
                    [
                        "Indian Head Resort",
                        14,
                        0.0
                    ],
                    [
                        "Indian Lake Assoc - Boulder Beach",
                        17,
                        0.0
                    ],
                    [
                        "Hood's Pond",
                        13,
                        0.0
                    ],
                    [
                        "Indian Lake Assoc - Forest Beach",
                        17,
                        0.0
                    ],
                    [
                        "Lake Boone",
                        8,
                        0.0
                    ],
                    [
                        "Kildeer Island (AKA Sandy Shore)",
                        11,
                        0.0
                    ],
                    [
                        "Lake Attitash - A.L.S.I.A.",
                        14,
                        0.0
                    ],
                    [
                        "Joshua's Pond",
                        13,
                        0.0
                    ],
                    [
                        "Jemima Pond",
                        14,
                        0.0
                    ],
                    [
                        "Italian-American Sporting Club",
                        15,
                        0.0
                    ],
                    [
                        "Island Grove Beach",
                        6,
                        0.0
                    ],
                    [
                        "Heart Pond",
                        10,
                        0.0
                    ],
                    [
                        "Gull Pond",
                        19,
                        0.0
                    ],
                    [
                        "Halcyon Condominiums/Horse Pond Corporation",
                        14,
                        0.0
                    ],
                    [
                        "Hamblin's Pond",
                        13,
                        0.0
                    ],
                    [
                        "Hedges Pond",
                        9,
                        0.0
                    ],
                    [
                        "Hartsuff Park",
                        9,
                        0.0
                    ],
                    [
                        "Arcand Park Beach",
                        7,
                        0.0
                    ],
                    [
                        "Grotonwood Camp",
                        8,
                        0.0
                    ],
                    [
                        "Great Sand Lakes Association - Vacation Ln. (John Joseph Pond)",
                        14,
                        0.0
                    ],
                    [
                        "Grew's Pond",
                        14,
                        0.0
                    ],
                    [
                        "Grossman Beach",
                        7,
                        0.0
                    ],
                    [
                        "Great Sand Lakes Association - Clearwater Dr. (Bucks Pond)",
                        14,
                        0.0
                    ],
                    [
                        "Hinkley's Pond",
                        14,
                        0.0
                    ],
                    [
                        "Holmes Street",
                        16,
                        0.0
                    ],
                    [
                        "Hickory Hills (Island Rd.)",
                        13,
                        0.0
                    ],
                    [
                        "Herring Pond",
                        14,
                        0.0
                    ],
                    [
                        "Fearings Pond (DCR) ",
                        32,
                        0.0
                    ],
                    [
                        "Grove",
                        16,
                        0.0
                    ],
                    [
                        "Groton Town Beach (Sargisson Beach)",
                        7,
                        0.0
                    ],
                    [
                        "Camp Burgess",
                        6,
                        0.0
                    ],
                    [
                        "East Beach - Beaver Lake",
                        4,
                        0.0
                    ],
                    [
                        "Forge Village Beach",
                        10,
                        0.0
                    ],
                    [
                        "East Boston Camps - Day Care",
                        16,
                        0.0
                    ],
                    [
                        "Ashumet Valley Property Owners, Inc./Holly Sands Homeowners Corp.",
                        14,
                        0.0
                    ],
                    [
                        "Wakeby Pond",
                        11,
                        0.0
                    ],
                    [
                        "Valley Pond",
                        20,
                        0.0
                    ],
                    [
                        "White Pond Assoc",
                        16,
                        0.0
                    ],
                    [
                        "Wildwood - Lakeside",
                        15,
                        0.0
                    ],
                    [
                        "Wildwood - Main Beach",
                        15,
                        0.0
                    ],
                    [
                        "White Pond Town Landing",
                        14,
                        0.0
                    ],
                    [
                        "Wildwood - Fox Den",
                        15,
                        0.0
                    ],
                    [
                        "West Beach - Beaver Lake",
                        4,
                        0.0
                    ],
                    [
                        "Wiley Park",
                        14,
                        0.0
                    ],
                    [
                        "Wildwood - Otter Pond Beach",
                        15,
                        0.0
                    ],
                    [
                        "College Pond Day Use (DCR)",
                        15,
                        0.0
                    ],
                    [
                        "Cooper Creek HOA",
                        6,
                        0.0
                    ],
                    [
                        "Moores Pond Beach",
                        5,
                        0.0
                    ],
                    [
                        "Mountain Grove Assoc. Beach",
                        14,
                        0.0
                    ],
                    [
                        "Cranberry Cove (aka Camp Kiwanee)",
                        6,
                        0.0
                    ],
                    [
                        "Country Club of Pittsfield",
                        15,
                        0.0
                    ],
                    [
                        "Center Pond Beach",
                        16,
                        0.0
                    ],
                    [
                        "Charge Pond (DCR)",
                        16,
                        0.0
                    ],
                    [
                        "Lancaster Town Beach",
                        10,
                        0.0
                    ],
                    [
                        "Lingan Street",
                        14,
                        0.0
                    ],
                    [
                        "Lake Manchaug Camping",
                        15,
                        0.0
                    ],
                    [
                        "Lake House at Laurel Lake",
                        7,
                        0.0
                    ],
                    [
                        "Little Sandy Pond",
                        16,
                        0.0
                    ],
                    [
                        "Long Pond (Rte 124)",
                        14,
                        0.0
                    ],
                    [
                        "Camp Romaca ",
                        1,
                        0.0
                    ],
                    [
                        "Camp Stepping Stone",
                        10,
                        0.0
                    ],
                    [
                        "Camp Stevenson/Witawentin",
                        9,
                        0.0
                    ],
                    [
                        "Camp Watitoh Beach",
                        12,
                        0.0
                    ],
                    [
                        "Camp Winadu",
                        7,
                        0.0
                    ],
                    [
                        "Noble's Cove Beach",
                        16,
                        0.0
                    ],
                    [
                        "Nauset Haven Condo Association (Minister's Pond)",
                        14,
                        0.0
                    ],
                    [
                        "NARA Beach",
                        17,
                        0.0
                    ],
                    [
                        "Onota Lake - Decom Beach",
                        15,
                        0.0
                    ],
                    [
                        "Onota Lake - Controy Pavillion",
                        15,
                        0.0
                    ],
                    [
                        "Onota Lake - Public Beach at Burbank Park",
                        15,
                        0.0
                    ],
                    [
                        "North Beach (NIA)",
                        16,
                        0.0
                    ],
                    [
                        "Lyman Lane",
                        16,
                        0.0
                    ],
                    [
                        "Maple Park Campground ",
                        32,
                        0.0
                    ],
                    [
                        "Peter's Pond RV Park ",
                        28,
                        0.0
                    ],
                    [
                        "Otis Reservoir Beach (DCR)",
                        15,
                        0.0
                    ],
                    [
                        "Goose Pond",
                        14,
                        0.0
                    ],
                    [
                        "Goose Pond at Leisure Lee Rd.",
                        16,
                        0.0
                    ],
                    [
                        "Great Pond",
                        30,
                        0.0
                    ],
                    [
                        "Minister's Pond",
                        14,
                        0.0
                    ],
                    [
                        "Marylou's Beach (NIA)",
                        16,
                        0.0
                    ],
                    [
                        "Middle Pond",
                        13,
                        0.0
                    ],
                    [
                        "Memorial Beach ",
                        36,
                        0.0
                    ],
                    [
                        "Massapoag Yacht Club",
                        10,
                        0.0
                    ],
                    [
                        "Sandy Pond Campground",
                        14,
                        0.0
                    ],
                    [
                        "Sandy Shore Association (Aunt Edies Pond) ",
                        14,
                        0.0
                    ],
                    [
                        "Pinecrest Property Owners Assoc.",
                        10,
                        0.0
                    ],
                    [
                        "Pontoosuc Lake - Decom Beach",
                        15,
                        0.0
                    ],
                    [
                        "Plymouth Estates",
                        1,
                        0.0
                    ],
                    [
                        "Camp Hayward",
                        6,
                        0.0
                    ],
                    [
                        "Camp Lyndon",
                        13,
                        0.0
                    ],
                    [
                        "Camp Lowe Beach",
                        8,
                        0.0
                    ],
                    [
                        "Summer Village Main Beach",
                        16,
                        0.0
                    ],
                    [
                        "Sunrise Beach",
                        16,
                        0.0
                    ],
                    [
                        "Templeton Fish and Game Club",
                        14,
                        0.0
                    ],
                    [
                        "Richmond Town Beach",
                        15,
                        0.0
                    ],
                    [
                        "Richmond Shores South Pond",
                        13,
                        0.0
                    ],
                    [
                        "Sandy Beach (NIA)",
                        16,
                        0.0
                    ],
                    [
                        "Sandpointe Shores Association Inc. - Whitecaps",
                        13,
                        0.0
                    ],
                    [
                        "Rolling Ridge Farm Homeowners Association (Lawrence Pond)",
                        14,
                        0.0
                    ],
                    [
                        "Princess Beach-Scargo Lake",
                        14,
                        0.0
                    ],
                    [
                        "Regency Drive Homeowners Association ",
                        13,
                        0.0
                    ],
                    [
                        "Camp Hi Rock - Bear Rock Beach",
                        11,
                        0.0
                    ],
                    [
                        "Stiles Pond Beach",
                        13,
                        0.0
                    ],
                    [
                        "South Shore YMCA - Triangle Pond",
                        6,
                        0.0
                    ],
                    [
                        "South Beach - Beaver Lake",
                        4,
                        0.0
                    ],
                    [
                        "Sichols",
                        16,
                        0.0
                    ],
                    [
                        "Card Pond Beach",
                        15,
                        0.0
                    ],
                    [
                        "Schoolhouse Pond",
                        14,
                        0.0
                    ],
                    [
                        "Seymour Pond",
                        14,
                        0.0
                    ],
                    [
                        "Shady Lane Homeowners Association",
                        12,
                        0.0
                    ],
                    [
                        "Shady Point Campground",
                        7,
                        0.0
                    ],
                    [
                        "Sheep Pond Beach Association",
                        14,
                        0.0
                    ],
                    [
                        "Sheep Pond Landing",
                        14,
                        0.0
                    ],
                    [
                        "Camp Wind-in-the-Pines ",
                        13,
                        0.0
                    ],
                    [
                        "Camp Wingate - Kirland",
                        14,
                        0.0
                    ],
                    [
                        "Blueberry Hill Camp (Curlew Pond)",
                        14,
                        0.0
                    ],
                    [
                        "Bolton Town Beach",
                        13,
                        0.0
                    ],
                    [
                        "Wallum Lake Terrace",
                        16,
                        0.0
                    ],
                    [
                        "Breezy Picnic Grounds",
                        13,
                        0.0
                    ],
                    [
                        "Scargo Lake",
                        14,
                        0.0
                    ],
                    [
                        "Berkshire Lake Estates",
                        16,
                        0.0
                    ],
                    [
                        "Beacon Park Condominiums",
                        11,
                        0.0
                    ],
                    [
                        "Barrett Pond (DCR)",
                        16,
                        0.0
                    ]
                ]
```
<!-- /original:subtask.4.answer -->

### 子任务 5：environment-hard-15-5

问题原文：

<!-- original:subtask.5.query chars:144 -->
```text
What are the yearly exceedance rates for each beach? Return the exceedance rates for all beaches in 2020 in the form [beach_name, rate in 2020].
```
<!-- /original:subtask.5.query -->

标准答案原文：

<!-- original:subtask.5.answer chars:52768 -->
```json
[
                    [
                        "Damon Pond Beach (DCR)",
                        0.6842105263157895
                    ],
                    [
                        "Beamans Pond - Day Use (DCR)",
                        0.13333333333333333
                    ],
                    [
                        "Beamans Pond - Campground (DCR)",
                        0.06666666666666667
                    ],
                    [
                        "Robinson Pond Beach (DCR)",
                        0.0
                    ],
                    [
                        "Pearl Hill Pond Beach (DCR)",
                        0.2
                    ],
                    [
                        "Waushakum Beach",
                        0.36363636363636365
                    ],
                    [
                        "Learned Pond Beach",
                        0.4
                    ],
                    [
                        "Lake Quinsigamond-Regatta Point Beach (DCR)",
                        0.2857142857142857
                    ],
                    [
                        "Community Center Beach",
                        0.47368421052631576
                    ],
                    [
                        "Bass Pond ",
                        0.4
                    ],
                    [
                        "Merrimac River - Bath House",
                        0.42105263157894735
                    ],
                    [
                        "Dunn Pond (DCR)",
                        0.15384615384615385
                    ],
                    [
                        "Peckham Pond ",
                        0.15789473684210525
                    ],
                    [
                        "Shannon Beach ",
                        0.09523809523809523
                    ],
                    [
                        "Camp Wilder ",
                        0.6666666666666666
                    ],
                    [
                        "Lake Wyola (DCR)",
                        0.0
                    ],
                    [
                        "Hopkinton Reservoir-Main Beach (DCR)",
                        0.11764705882352941
                    ],
                    [
                        "Eagle Lake",
                        0.3333333333333333
                    ],
                    [
                        "Sherwood Forest - North Beach",
                        0.1111111111111111
                    ],
                    [
                        "Puffers Pond (AKA Factory Hollow Pond) ",
                        0.1388888888888889
                    ],
                    [
                        "Pearce Lake ",
                        0.37037037037037035
                    ],
                    [
                        "Cold River Pool (DCR)",
                        0.17647058823529413
                    ],
                    [
                        "Houghton's Pond ",
                        0.0625
                    ],
                    [
                        "Frye Pond Beach (DCR)",
                        0.1111111111111111
                    ],
                    [
                        "Mendon Town Beach",
                        0.0
                    ],
                    [
                        "Lake Gardner",
                        0.2
                    ],
                    [
                        "Hampton Ponds - Kingsley Beach (DCR)",
                        0.11764705882352941
                    ],
                    [
                        "Hopkinton Reservoir-Upper Beach (DCR)",
                        0.15789473684210525
                    ],
                    [
                        "Sherwood Forest - Grassy Beach",
                        0.0
                    ],
                    [
                        "Ashland Reservoir-Main Beach (DCR)",
                        0.17647058823529413
                    ],
                    [
                        "Sutton Falls Camp",
                        0.17647058823529413
                    ],
                    [
                        "Lulu Pond Beach (DCR)",
                        0.1875
                    ],
                    [
                        "Seth's Pond ",
                        0.46153846153846156
                    ],
                    [
                        "Coes Pond Beach (Mill St.)",
                        0.4583333333333333
                    ],
                    [
                        "Hampton Ponds - Lamberts Beach (DCR)",
                        0.11764705882352941
                    ],
                    [
                        "Miacomet Pond",
                        0.08333333333333333
                    ],
                    [
                        "Paddle Club ",
                        0.2
                    ],
                    [
                        "Pleasure Point",
                        0.0625
                    ],
                    [
                        "Lake Lashaway",
                        0.08333333333333333
                    ],
                    [
                        "Crow Hill Pond Beach (DCR)",
                        0.2777777777777778
                    ],
                    [
                        "Mauserts Pond (DCR)",
                        0.0625
                    ],
                    [
                        "Shore Park",
                        0.35714285714285715
                    ],
                    [
                        "Whitehall Pond Beach (DCR)",
                        0.058823529411764705
                    ],
                    [
                        "Fair Acres Country Day School",
                        0.2857142857142857
                    ],
                    [
                        "Medford Boat Club ",
                        0.17142857142857143
                    ],
                    [
                        "Furnace Colony",
                        0.0
                    ],
                    [
                        "Silver Hill Assoc",
                        0.058823529411764705
                    ],
                    [
                        "Greenfield Municipal Bathing Beach",
                        0.07692307692307693
                    ],
                    [
                        "Picture Lake (Flax Pond)",
                        0.125
                    ],
                    [
                        "Glen Devin Condominiums",
                        0.07142857142857142
                    ],
                    [
                        "Berry Pond Beach (DCR)",
                        0.058823529411764705
                    ],
                    [
                        "Chicopee Beach (DCR)",
                        0.125
                    ],
                    [
                        "Stoddard Park",
                        0.0625
                    ],
                    [
                        "Watsons Pond (DCR)",
                        0.15789473684210525
                    ],
                    [
                        "Laurel Lake (DCR)",
                        0.0
                    ],
                    [
                        "Upper Highland Lake - Day use area beach (DCR)",
                        0.1111111111111111
                    ],
                    [
                        "Benedict Pond Beach (DCR)",
                        0.0
                    ],
                    [
                        "Morses Beach",
                        0.06666666666666667
                    ],
                    [
                        "Conway Swimming Pool",
                        0.0
                    ],
                    [
                        "Camp Marshall Beach",
                        0.2222222222222222
                    ],
                    [
                        "Santuit Pond ",
                        0.034482758620689655
                    ],
                    [
                        "Upton Town Beach",
                        0.2777777777777778
                    ],
                    [
                        "St. Laurent Camp",
                        0.3125
                    ],
                    [
                        "Walden Pond - Main (DCR)",
                        0.11764705882352941
                    ],
                    [
                        "Lake Quinsigamond-Lake Park Beach (DCR)",
                        0.11764705882352941
                    ],
                    [
                        "Smith Pond",
                        0.14285714285714285
                    ],
                    [
                        "Arrive Lunenburg (Lake Whalom)",
                        0.23529411764705882
                    ],
                    [
                        "Whispering Pines Condo Association (Muddy Pond)",
                        0.0
                    ],
                    [
                        "York Lake Beach (DCR)",
                        0.0
                    ],
                    [
                        "Freetown Town Beach",
                        0.14285714285714285
                    ],
                    [
                        "Luther Hill Park",
                        0.0
                    ],
                    [
                        "Homestead Residents Association (Crocker Pond)",
                        0.07142857142857142
                    ],
                    [
                        "Farm Pond",
                        0.125
                    ],
                    [
                        "Saxonville Beach",
                        0.125
                    ],
                    [
                        "Camp Gannet (Everwood/upper)",
                        0.08333333333333333
                    ],
                    [
                        "Camp Danbee",
                        0.09090909090909091
                    ],
                    [
                        "Hickory Hills (Brookview)",
                        0.07692307692307693
                    ],
                    [
                        "Indian Lake Public Beach (Sherburne Ave)",
                        0.16666666666666666
                    ],
                    [
                        "Crystal Lake",
                        0.11627906976744186
                    ],
                    [
                        "Hickory Hills (Hemlock Drive)",
                        0.2
                    ],
                    [
                        "Ames Pond",
                        0.1
                    ],
                    [
                        "Sherwood Forest - Boat Beach",
                        0.0
                    ],
                    [
                        "Massaconet Shores",
                        0.16666666666666666
                    ],
                    [
                        "Hinkley ",
                        0.10714285714285714
                    ],
                    [
                        "Wells State Park - Walker Pond Beach (DCR)",
                        0.1111111111111111
                    ],
                    [
                        "Sesachacha Pond",
                        0.0
                    ],
                    [
                        "Damon Pond Association Beach",
                        0.2222222222222222
                    ],
                    [
                        "Memorial Beach (Dug Pond) ",
                        0.11764705882352941
                    ],
                    [
                        "Becket Woods Road District - Beach",
                        0.0625
                    ],
                    [
                        "Forest Lake: Swimming Beach",
                        0.0
                    ],
                    [
                        "Camp Russell",
                        0.15384615384615385
                    ],
                    [
                        "Lunenburg Town Beach",
                        0.1111111111111111
                    ],
                    [
                        "Ashfield Park Beach",
                        0.08333333333333333
                    ],
                    [
                        "Silver Pond Beach",
                        0.2727272727272727
                    ],
                    [
                        "Indian Lake Assoc - Niskayuna Beach",
                        0.0
                    ],
                    [
                        "Cedar Lake Recreation Area",
                        0.14285714285714285
                    ],
                    [
                        "Sherwood Forest - Will Scarlett",
                        0.0
                    ],
                    [
                        "Lakeland Beach",
                        0.0
                    ],
                    [
                        "White Pines Condos (Stockbridge Bowl)",
                        0.0
                    ],
                    [
                        "Wallum Lake (DCR)",
                        0.058823529411764705
                    ],
                    [
                        "Ice House Pond",
                        0.07692307692307693
                    ],
                    [
                        "Wayland Town Beach ",
                        0.025
                    ],
                    [
                        "Tyngsborough Town Beach",
                        0.15789473684210525
                    ],
                    [
                        "Long Cove (Fresh)",
                        0.14285714285714285
                    ],
                    [
                        "Briarwood Mashpee Association",
                        0.14285714285714285
                    ],
                    [
                        "Long Pond (Depot St.)",
                        0.0
                    ],
                    [
                        "Little Sandy",
                        0.0
                    ],
                    [
                        "Sand Shores Association",
                        0.07692307692307693
                    ],
                    [
                        "Camp Yomechas",
                        0.1
                    ],
                    [
                        "Indian Ranch",
                        0.0
                    ],
                    [
                        "Lake Chauncy Beach",
                        0.21428571428571427
                    ],
                    [
                        "Wrights Pond ",
                        0.14285714285714285
                    ],
                    [
                        "Tom Denney Nature Camp",
                        0.0
                    ],
                    [
                        "John's Pond",
                        0.125
                    ],
                    [
                        "Edwards Town Beach",
                        0.09090909090909091
                    ],
                    [
                        "Lake Dennison State Park (DCR) ",
                        0.030303030303030304
                    ],
                    [
                        "Lake Wyola Association: West Beach",
                        0.2
                    ],
                    [
                        "Camp Good News",
                        0.0
                    ],
                    [
                        "John's Pond North Cove Association",
                        0.06666666666666667
                    ],
                    [
                        "Halifax Beach Association",
                        0.0
                    ],
                    [
                        "Silver Lake",
                        0.0
                    ],
                    [
                        "Lake Pearl Restaurant",
                        0.0
                    ],
                    [
                        "White Island Association",
                        0.07142857142857142
                    ],
                    [
                        "Lenox Town Beach (Laurel Lake)",
                        0.07692307692307693
                    ],
                    [
                        "Gull Pond Landing",
                        0.058823529411764705
                    ],
                    [
                        "Mascuppic",
                        0.05555555555555555
                    ],
                    [
                        "Collette Drive Beach",
                        0.0
                    ],
                    [
                        "Sharon Town Beach ",
                        0.14285714285714285
                    ],
                    [
                        "Everwood Day Camp (Everwood/lower)",
                        0.0
                    ],
                    [
                        "Santuit Pond Estates Association",
                        0.0
                    ],
                    [
                        "Freeman Lake ",
                        0.18181818181818182
                    ],
                    [
                        "Indian Memorial",
                        0.058823529411764705
                    ],
                    [
                        "Stockbridge Town Beach (Stockbridge Bowl)",
                        0.058823529411764705
                    ],
                    [
                        "Snake Pond",
                        0.08333333333333333
                    ],
                    [
                        "Cochituate State Park Beach (DCR)",
                        0.1111111111111111
                    ],
                    [
                        "Nutting Lake - Micozzi Beach ",
                        0.05555555555555555
                    ],
                    [
                        "Sampson's Pond",
                        0.0
                    ],
                    [
                        "John's Pond Estates Association (Fred's)",
                        0.0
                    ],
                    [
                        "Walden Pond - Red Cross (DCR) ",
                        0.16666666666666666
                    ],
                    [
                        "Walker Pond - Main Beach",
                        0.0
                    ],
                    [
                        "Morton Park ",
                        0.0
                    ],
                    [
                        "Shangri-La",
                        0.0
                    ],
                    [
                        "White Pond Cottages",
                        0.06666666666666667
                    ],
                    [
                        "Pinecrest Beach Improvement Association (Jenkins Pond)",
                        0.06666666666666667
                    ],
                    [
                        "Fresh Pond ",
                        0.0
                    ],
                    [
                        "Dunroamin Park and Cottages",
                        0.0
                    ],
                    [
                        "Mirror Lake",
                        0.14285714285714285
                    ],
                    [
                        "Camp Avoda",
                        0.14285714285714285
                    ],
                    [
                        "Camp Sequena ",
                        0.0
                    ],
                    [
                        "Lochstead Association",
                        0.06666666666666667
                    ],
                    [
                        "Pinewood Lodge Campground",
                        0.0
                    ],
                    [
                        "Queen Sewell Pond",
                        0.0
                    ],
                    [
                        "Attaquin Park (Mashpee-Wakeby Pond)",
                        0.0
                    ],
                    [
                        "Twin Lakes Condominiums",
                        0.0
                    ],
                    [
                        "Mares Pond Association",
                        0.0
                    ],
                    [
                        "Oldham Pond",
                        0.0
                    ],
                    [
                        "Duck Pond",
                        0.0
                    ],
                    [
                        "Camp Hi Rock - Main Beach",
                        0.0
                    ],
                    [
                        "Sun Retreats Cape Cod (Round Pond)",
                        0.13333333333333333
                    ],
                    [
                        "Sunset Beach",
                        0.0
                    ],
                    [
                        "Water-by Estates Homeowners Association",
                        0.0
                    ],
                    [
                        "Wequaquet Estates Beach Association",
                        0.0
                    ],
                    [
                        "Annawon Drive",
                        0.0625
                    ],
                    [
                        "Cordially Colony",
                        0.05555555555555555
                    ],
                    [
                        "Plunkett Lake Beach",
                        0.0
                    ],
                    [
                        "Hammond Acres",
                        0.0
                    ],
                    [
                        "Thousand Trails",
                        0.0625
                    ],
                    [
                        "Long Pond (Long Pond Drive)",
                        0.125
                    ],
                    [
                        "Lee Town Beach",
                        0.0
                    ],
                    [
                        "McDonald Beach",
                        0.0
                    ],
                    [
                        "Orange Town Beach ",
                        0.0
                    ],
                    [
                        "Camp Resolute ",
                        0.0
                    ],
                    [
                        "Crystal Pond Homeowners Assoc Beach",
                        0.0
                    ],
                    [
                        "Beachwood Assoc. ",
                        0.058823529411764705
                    ],
                    [
                        "Roger's Beach",
                        0.0
                    ],
                    [
                        "Flax Pond (DCR)",
                        0.0
                    ],
                    [
                        "Intercolonial Club of Marlborough",
                        0.0
                    ],
                    [
                        "Windsor Lake",
                        0.058823529411764705
                    ],
                    [
                        "North Pond Beach (DCR)",
                        0.0
                    ],
                    [
                        "King's Campground",
                        0.0
                    ],
                    [
                        "Camp Taconic Beach",
                        0.1111111111111111
                    ],
                    [
                        "Sandbar Beach Club",
                        0.1111111111111111
                    ],
                    [
                        "Sherwood Forest - Arrow Beach",
                        0.0
                    ],
                    [
                        "Crocker Pond",
                        0.1111111111111111
                    ],
                    [
                        "Richardson",
                        0.1111111111111111
                    ],
                    [
                        "Camp Overflow Beach",
                        0.05
                    ],
                    [
                        "Sherwood Greens Road District Beach ",
                        0.0
                    ],
                    [
                        "Bell Pond Beach",
                        0.1
                    ],
                    [
                        "S.P.E.N.A. Beach",
                        0.0
                    ],
                    [
                        "North Beach ",
                        0.0
                    ],
                    [
                        "Peter's Pond Town Park 1",
                        0.0
                    ],
                    [
                        "Danvers YMCA Daycamp",
                        0.09090909090909091
                    ],
                    [
                        "Merino Pond",
                        0.0
                    ],
                    [
                        "Chilson Beach",
                        0.09090909090909091
                    ],
                    [
                        "Camp Mah-kee-nac",
                        0.0
                    ],
                    [
                        "Flax Pond",
                        0.0
                    ],
                    [
                        "Lake Waushacum",
                        0.0
                    ],
                    [
                        "American Legion Park",
                        0.0
                    ],
                    [
                        "Ellis Beach",
                        0.0
                    ],
                    [
                        "Sweatt Beach",
                        0.08333333333333333
                    ],
                    [
                        "Sandpointe Shores Association Inc. - Rock Hollow",
                        0.0
                    ],
                    [
                        "Cooper's Pond",
                        0.0
                    ],
                    [
                        "Fells Pond Village Peninsula Council",
                        0.0
                    ],
                    [
                        "Centennial Grove",
                        0.07692307692307693
                    ],
                    [
                        "Wequaquet Lake Yacht Club",
                        0.0
                    ],
                    [
                        "Woods Pond Cabins",
                        0.0
                    ],
                    [
                        "Higgins Pond",
                        0.0
                    ],
                    [
                        "Long Pond (Cahoon Street)",
                        0.0
                    ],
                    [
                        "Lithuanian Outing Assoc.",
                        0.0
                    ],
                    [
                        "Sunset Lake ",
                        0.0
                    ],
                    [
                        "Mashpee Shores Association",
                        0.0
                    ],
                    [
                        "Jimmy's Beach (Wequaquet Heights Association) ",
                        0.034482758620689655
                    ],
                    [
                        "Lakewood Hills Property Owners Association",
                        0.0
                    ],
                    [
                        "Craig Road Beach",
                        0.0
                    ],
                    [
                        "Cranberry Bog Homeowner's Association (Big Sandy Pond)",
                        0.0
                    ],
                    [
                        "Gull Pond (2) - Steele Rd.",
                        0.0
                    ],
                    [
                        "Long Pond Farms Neighborhood Association",
                        0.0
                    ],
                    [
                        "Lovell's Pond",
                        0.0
                    ],
                    [
                        "Richmond Pond Association",
                        0.0
                    ],
                    [
                        "Coonamessett Pond",
                        0.0
                    ],
                    [
                        "Holly Point Beach and Tennis Association",
                        0.0
                    ],
                    [
                        "Buck's Pond",
                        0.0
                    ],
                    [
                        "Wianno Club (Crystal Lake)",
                        0.0
                    ],
                    [
                        "Lawrence Pond Village Campground",
                        0.0
                    ],
                    [
                        "Blueberry Hills Property Owners Association",
                        0.0
                    ],
                    [
                        "Wequaquet Lake Town",
                        0.0
                    ],
                    [
                        "Pout Pond Beach",
                        0.0
                    ],
                    [
                        "Sand Pond",
                        0.0
                    ],
                    [
                        "Robinwood Homeowners Association (Owl Pond)",
                        0.0
                    ],
                    [
                        "Slough Pond",
                        0.0
                    ],
                    [
                        "Hathaway's Pond",
                        0.07142857142857142
                    ],
                    [
                        "Blackmore Pond",
                        0.0
                    ],
                    [
                        "Stetson",
                        0.0
                    ],
                    [
                        "Otis Town Beach",
                        0.0
                    ],
                    [
                        "Littleton Town Beach",
                        0.0
                    ],
                    [
                        "Plainfield Pond",
                        0.0
                    ],
                    [
                        "Baby Beach Lost Lake",
                        0.0
                    ],
                    [
                        "Upper Mill Pond",
                        0.06666666666666667
                    ],
                    [
                        "Baird Center (Bloody Pond)",
                        0.0
                    ],
                    [
                        "Lake Garfield",
                        0.0
                    ],
                    [
                        "Village Green Family Campground",
                        0.0
                    ],
                    [
                        "Hood Pond-boat ramp",
                        0.0
                    ],
                    [
                        "East Boston Camps - Girls Beach",
                        0.0
                    ],
                    [
                        "East Boston Camps - Boys Beach",
                        0.0
                    ],
                    [
                        "Lake Mansfield",
                        0.0
                    ],
                    [
                        "Asnacomet Pond Beach (DCR) ",
                        0.0
                    ],
                    [
                        "Curlew Pond (DCR)",
                        0.0
                    ],
                    [
                        "Berry's Grove Campground",
                        0.0
                    ],
                    [
                        "Cliff Pond (DCR) ",
                        0.0
                    ],
                    [
                        "Center Lake Estates Beach",
                        0.0
                    ],
                    [
                        "Colonial Park",
                        0.0
                    ],
                    [
                        "Nabnassett American Legion",
                        0.0
                    ],
                    [
                        "Richard P. Sharon Beach",
                        0.0
                    ],
                    [
                        "Rowe Town Beach at Pelham Park ",
                        0.0
                    ],
                    [
                        "Pilgrim Lake",
                        0.0
                    ],
                    [
                        "Henry F Collins Beach",
                        0.0
                    ],
                    [
                        "Sandy Beach ",
                        0.0
                    ],
                    [
                        "Annursnac Hill Assoc.",
                        0.0
                    ],
                    [
                        "Mohawk Estates ",
                        0.0
                    ],
                    [
                        "Sherwood Forest - Excalibur",
                        0.0
                    ],
                    [
                        "Hilltop",
                        0.058823529411764705
                    ],
                    [
                        "Camp Clark YMCA - Hyles Pond",
                        0.058823529411764705
                    ],
                    [
                        "Pleasant Pond Beach",
                        0.058823529411764705
                    ],
                    [
                        "Dennis Pond",
                        0.058823529411764705
                    ],
                    [
                        "Indian Lake Assoc - Dam Beach ",
                        0.05555555555555555
                    ],
                    [
                        "Musante Beach",
                        0.0
                    ],
                    [
                        "Camp Becket - Main Beach",
                        0.05555555555555555
                    ],
                    [
                        "Lakeside",
                        0.0
                    ],
                    [
                        "Walker Pond (Oak Cove)",
                        0.0
                    ],
                    [
                        "Ellis Haven",
                        0.0
                    ],
                    [
                        "Plugs Pond ",
                        0.0
                    ],
                    [
                        "Beechwood Landing Property Owners Association",
                        0.0
                    ],
                    [
                        "John's Pond (Public) ",
                        0.0
                    ],
                    [
                        "Long Pond",
                        0.0
                    ],
                    [
                        "Pomps Pond ",
                        0.023809523809523808
                    ],
                    [
                        "Summer Beach ",
                        0.0
                    ],
                    [
                        "Upper Highland Lake - Campers Beach (DCR)",
                        0.0
                    ],
                    [
                        "Tunxis Club",
                        0.0
                    ],
                    [
                        "The Trustees  - Lowell Holly (Wakeby Pond)",
                        0.0
                    ],
                    [
                        "Camp Farley (Mashpee-Wakeby Pond)",
                        0.0
                    ],
                    [
                        "Wales Town Beach",
                        0.0
                    ],
                    [
                        "The Pines",
                        0.0
                    ],
                    [
                        "The Trail at Big Alum Lake Association Beach",
                        0.0
                    ],
                    [
                        "The Trustees  - Lowell Holly (Mashpee Pond)",
                        0.0
                    ],
                    [
                        "Wildwood - Meadow",
                        0.0
                    ],
                    [
                        "Thunderbridge ",
                        0.0
                    ],
                    [
                        "Treasure Island Condominiums",
                        0.0
                    ],
                    [
                        "Lake Wyola Association: North Beach",
                        0.0
                    ],
                    [
                        "Lake Wyola Association: East Beach",
                        0.0
                    ],
                    [
                        "Lakeside Meadows",
                        0.0
                    ],
                    [
                        "Lakefield Farms Trust",
                        0.0
                    ],
                    [
                        "Horse Pond",
                        0.0
                    ],
                    [
                        "Indian Head Resort",
                        0.0
                    ],
                    [
                        "Indian Lake Assoc - Boulder Beach",
                        0.0
                    ],
                    [
                        "Hood's Pond",
                        0.0
                    ],
                    [
                        "Indian Lake Assoc - Forest Beach",
                        0.0
                    ],
                    [
                        "Lake Boone",
                        0.0
                    ],
                    [
                        "Kildeer Island (AKA Sandy Shore)",
                        0.0
                    ],
                    [
                        "Lake Attitash - A.L.S.I.A.",
                        0.0
                    ],
                    [
                        "Joshua's Pond",
                        0.0
                    ],
                    [
                        "Jemima Pond",
                        0.0
                    ],
                    [
                        "Italian-American Sporting Club",
                        0.0
                    ],
                    [
                        "Island Grove Beach",
                        0.0
                    ],
                    [
                        "Heart Pond",
                        0.0
                    ],
                    [
                        "Gull Pond",
                        0.0
                    ],
                    [
                        "Halcyon Condominiums/Horse Pond Corporation",
                        0.0
                    ],
                    [
                        "Hamblin's Pond",
                        0.0
                    ],
                    [
                        "Hedges Pond",
                        0.0
                    ],
                    [
                        "Hartsuff Park",
                        0.0
                    ],
                    [
                        "Arcand Park Beach",
                        0.0
                    ],
                    [
                        "Grotonwood Camp",
                        0.0
                    ],
                    [
                        "Great Sand Lakes Association - Vacation Ln. (John Joseph Pond)",
                        0.0
                    ],
                    [
                        "Grew's Pond",
                        0.0
                    ],
                    [
                        "Grossman Beach",
                        0.0
                    ],
                    [
                        "Great Sand Lakes Association - Clearwater Dr. (Bucks Pond)",
                        0.0
                    ],
                    [
                        "Hinkley's Pond",
                        0.0
                    ],
                    [
                        "Holmes Street",
                        0.0
                    ],
                    [
                        "Hickory Hills (Island Rd.)",
                        0.0
                    ],
                    [
                        "Herring Pond",
                        0.0
                    ],
                    [
                        "Fearings Pond (DCR) ",
                        0.0
                    ],
                    [
                        "Grove",
                        0.0
                    ],
                    [
                        "Groton Town Beach (Sargisson Beach)",
                        0.0
                    ],
                    [
                        "Camp Burgess",
                        0.0
                    ],
                    [
                        "East Beach - Beaver Lake",
                        0.0
                    ],
                    [
                        "Forge Village Beach",
                        0.0
                    ],
                    [
                        "East Boston Camps - Day Care",
                        0.0
                    ],
                    [
                        "Ashumet Valley Property Owners, Inc./Holly Sands Homeowners Corp.",
                        0.0
                    ],
                    [
                        "Wakeby Pond",
                        0.0
                    ],
                    [
                        "Valley Pond",
                        0.0
                    ],
                    [
                        "White Pond Assoc",
                        0.0
                    ],
                    [
                        "Wildwood - Lakeside",
                        0.0
                    ],
                    [
                        "Wildwood - Main Beach",
                        0.0
                    ],
                    [
                        "White Pond Town Landing",
                        0.0
                    ],
                    [
                        "Wildwood - Fox Den",
                        0.0
                    ],
                    [
                        "West Beach - Beaver Lake",
                        0.0
                    ],
                    [
                        "Wiley Park",
                        0.0
                    ],
                    [
                        "Wildwood - Otter Pond Beach",
                        0.0
                    ],
                    [
                        "College Pond Day Use (DCR)",
                        0.0
                    ],
                    [
                        "Cooper Creek HOA",
                        0.0
                    ],
                    [
                        "Moores Pond Beach",
                        0.0
                    ],
                    [
                        "Mountain Grove Assoc. Beach",
                        0.0
                    ],
                    [
                        "Cranberry Cove (aka Camp Kiwanee)",
                        0.0
                    ],
                    [
                        "Country Club of Pittsfield",
                        0.0
                    ],
                    [
                        "Center Pond Beach",
                        0.0
                    ],
                    [
                        "Charge Pond (DCR)",
                        0.0
                    ],
                    [
                        "Lancaster Town Beach",
                        0.0
                    ],
                    [
                        "Lingan Street",
                        0.0
                    ],
                    [
                        "Lake Manchaug Camping",
                        0.0
                    ],
                    [
                        "Lake House at Laurel Lake",
                        0.0
                    ],
                    [
                        "Little Sandy Pond",
                        0.0
                    ],
                    [
                        "Long Pond (Rte 124)",
                        0.0
                    ],
                    [
                        "Camp Romaca ",
                        0.0
                    ],
                    [
                        "Camp Stepping Stone",
                        0.0
                    ],
                    [
                        "Camp Stevenson/Witawentin",
                        0.0
                    ],
                    [
                        "Camp Watitoh Beach",
                        0.0
                    ],
                    [
                        "Camp Winadu",
                        0.0
                    ],
                    [
                        "Noble's Cove Beach",
                        0.0
                    ],
                    [
                        "Nauset Haven Condo Association (Minister's Pond)",
                        0.0
                    ],
                    [
                        "NARA Beach",
                        0.0
                    ],
                    [
                        "Onota Lake - Decom Beach",
                        0.0
                    ],
                    [
                        "Onota Lake - Controy Pavillion",
                        0.0
                    ],
                    [
                        "Onota Lake - Public Beach at Burbank Park",
                        0.0
                    ],
                    [
                        "North Beach (NIA)",
                        0.0
                    ],
                    [
                        "Lyman Lane",
                        0.0
                    ],
                    [
                        "Maple Park Campground ",
                        0.0
                    ],
                    [
                        "Peter's Pond RV Park ",
                        0.0
                    ],
                    [
                        "Otis Reservoir Beach (DCR)",
                        0.0
                    ],
                    [
                        "Goose Pond",
                        0.0
                    ],
                    [
                        "Goose Pond at Leisure Lee Rd.",
                        0.0
                    ],
                    [
                        "Great Pond",
                        0.0
                    ],
                    [
                        "Minister's Pond",
                        0.0
                    ],
                    [
                        "Marylou's Beach (NIA)",
                        0.0
                    ],
                    [
                        "Middle Pond",
                        0.0
                    ],
                    [
                        "Memorial Beach ",
                        0.0
                    ],
                    [
                        "Massapoag Yacht Club",
                        0.0
                    ],
                    [
                        "Sandy Pond Campground",
                        0.0
                    ],
                    [
                        "Sandy Shore Association (Aunt Edies Pond) ",
                        0.0
                    ],
                    [
                        "Pinecrest Property Owners Assoc.",
                        0.0
                    ],
                    [
                        "Pontoosuc Lake - Decom Beach",
                        0.0
                    ],
                    [
                        "Plymouth Estates",
                        0.0
                    ],
                    [
                        "Camp Hayward",
                        0.0
                    ],
                    [
                        "Camp Lyndon",
                        0.0
                    ],
                    [
                        "Camp Lowe Beach",
                        0.0
                    ],
                    [
                        "Summer Village Main Beach",
                        0.0
                    ],
                    [
                        "Sunrise Beach",
                        0.0
                    ],
                    [
                        "Templeton Fish and Game Club",
                        0.0
                    ],
                    [
                        "Richmond Town Beach",
                        0.0
                    ],
                    [
                        "Richmond Shores South Pond",
                        0.0
                    ],
                    [
                        "Sandy Beach (NIA)",
                        0.0
                    ],
                    [
                        "Sandpointe Shores Association Inc. - Whitecaps",
                        0.0
                    ],
                    [
                        "Rolling Ridge Farm Homeowners Association (Lawrence Pond)",
                        0.0
                    ],
                    [
                        "Princess Beach-Scargo Lake",
                        0.0
                    ],
                    [
                        "Regency Drive Homeowners Association ",
                        0.0
                    ],
                    [
                        "Camp Hi Rock - Bear Rock Beach",
                        0.0
                    ],
                    [
                        "Stiles Pond Beach",
                        0.0
                    ],
                    [
                        "South Shore YMCA - Triangle Pond",
                        0.0
                    ],
                    [
                        "South Beach - Beaver Lake",
                        0.0
                    ],
                    [
                        "Sichols",
                        0.0
                    ],
                    [
                        "Card Pond Beach",
                        0.0
                    ],
                    [
                        "Schoolhouse Pond",
                        0.0
                    ],
                    [
                        "Seymour Pond",
                        0.0
                    ],
                    [
                        "Shady Lane Homeowners Association",
                        0.0
                    ],
                    [
                        "Shady Point Campground",
                        0.0
                    ],
                    [
                        "Sheep Pond Beach Association",
                        0.0
                    ],
                    [
                        "Sheep Pond Landing",
                        0.0
                    ],
                    [
                        "Camp Wind-in-the-Pines ",
                        0.0
                    ],
                    [
                        "Camp Wingate - Kirland",
                        0.0
                    ],
                    [
                        "Blueberry Hill Camp (Curlew Pond)",
                        0.0
                    ],
                    [
                        "Bolton Town Beach",
                        0.0
                    ],
                    [
                        "Wallum Lake Terrace",
                        0.0
                    ],
                    [
                        "Breezy Picnic Grounds",
                        0.0
                    ],
                    [
                        "Scargo Lake",
                        0.0
                    ],
                    [
                        "Berkshire Lake Estates",
                        0.0
                    ],
                    [
                        "Beacon Park Condominiums",
                        0.0
                    ],
                    [
                        "Barrett Pond (DCR)",
                        0.0
                    ]
                ]
```
<!-- /original:subtask.5.answer -->

### 子任务 6：environment-hard-15-6

问题原文：

<!-- original:subtask.6.query chars:161 -->
```text
What is the average exceedance rate across all years for all beaches? Return the average exceedance rates for all beaches in the form [beach_name, average rate].
```
<!-- /original:subtask.6.query -->

标准答案原文：

<!-- original:subtask.6.answer chars:55003 -->
```json
[
                    [
                        "Damon Pond Beach (DCR)",
                        0.5807748538011696
                    ],
                    [
                        "Beamans Pond - Day Use (DCR)",
                        0.47862838915470496
                    ],
                    [
                        "Beamans Pond - Campground (DCR)",
                        0.47521929824561404
                    ],
                    [
                        "Robinson Pond Beach (DCR)",
                        0.4651515151515152
                    ],
                    [
                        "Pearl Hill Pond Beach (DCR)",
                        0.40661764705882353
                    ],
                    [
                        "Waushakum Beach",
                        0.4052473262032085
                    ],
                    [
                        "Learned Pond Beach",
                        0.3631340579710145
                    ],
                    [
                        "Lake Quinsigamond-Regatta Point Beach (DCR)",
                        0.35944026733500417
                    ],
                    [
                        "Community Center Beach",
                        0.35149761659049583
                    ],
                    [
                        "Bass Pond ",
                        0.3108391608391609
                    ],
                    [
                        "Merrimac River - Bath House",
                        0.28159369010762203
                    ],
                    [
                        "Dunn Pond (DCR)",
                        0.2735309829059829
                    ],
                    [
                        "Peckham Pond ",
                        0.27256748991462615
                    ],
                    [
                        "Shannon Beach ",
                        0.2702380952380953
                    ],
                    [
                        "Camp Wilder ",
                        0.26489898989898986
                    ],
                    [
                        "Lake Wyola (DCR)",
                        0.2536764705882353
                    ],
                    [
                        "Hopkinton Reservoir-Main Beach (DCR)",
                        0.24285130718954248
                    ],
                    [
                        "Eagle Lake",
                        0.23333333333333334
                    ],
                    [
                        "Sherwood Forest - North Beach",
                        0.2328861369109047
                    ],
                    [
                        "Puffers Pond (AKA Factory Hollow Pond) ",
                        0.22139081678555364
                    ],
                    [
                        "Pearce Lake ",
                        0.21374105197634607
                    ],
                    [
                        "Cold River Pool (DCR)",
                        0.21372549019607845
                    ],
                    [
                        "Houghton's Pond ",
                        0.21325622640360492
                    ],
                    [
                        "Frye Pond Beach (DCR)",
                        0.20864661654135339
                    ],
                    [
                        "Mendon Town Beach",
                        0.20189950980392157
                    ],
                    [
                        "Lake Gardner",
                        0.2016544117647059
                    ],
                    [
                        "Hampton Ponds - Kingsley Beach (DCR)",
                        0.19645721925133688
                    ],
                    [
                        "Hopkinton Reservoir-Upper Beach (DCR)",
                        0.1956140350877193
                    ],
                    [
                        "Sherwood Forest - Grassy Beach",
                        0.18974673202614378
                    ],
                    [
                        "Ashland Reservoir-Main Beach (DCR)",
                        0.18872549019607843
                    ],
                    [
                        "Sutton Falls Camp",
                        0.1857843137254902
                    ],
                    [
                        "Lulu Pond Beach (DCR)",
                        0.1826593137254902
                    ],
                    [
                        "Seth's Pond ",
                        0.18037785405939563
                    ],
                    [
                        "Coes Pond Beach (Mill St.)",
                        0.17529761904761904
                    ],
                    [
                        "Hampton Ponds - Lamberts Beach (DCR)",
                        0.17398413312693498
                    ],
                    [
                        "Miacomet Pond",
                        0.16506410256410256
                    ],
                    [
                        "Paddle Club ",
                        0.1625
                    ],
                    [
                        "Pleasure Point",
                        0.16021825396825395
                    ],
                    [
                        "Lake Lashaway",
                        0.1579861111111111
                    ],
                    [
                        "Crow Hill Pond Beach (DCR)",
                        0.15729166666666666
                    ],
                    [
                        "Mauserts Pond (DCR)",
                        0.15641447368421052
                    ],
                    [
                        "Shore Park",
                        0.15595238095238095
                    ],
                    [
                        "Whitehall Pond Beach (DCR)",
                        0.15240690574475405
                    ],
                    [
                        "Fair Acres Country Day School",
                        0.15184815184815187
                    ],
                    [
                        "Medford Boat Club ",
                        0.15179554488065128
                    ],
                    [
                        "Furnace Colony",
                        0.14423076923076922
                    ],
                    [
                        "Silver Hill Assoc",
                        0.13723552662171587
                    ],
                    [
                        "Greenfield Municipal Bathing Beach",
                        0.13471166514644775
                    ],
                    [
                        "Picture Lake (Flax Pond)",
                        0.1327651515151515
                    ],
                    [
                        "Glen Devin Condominiums",
                        0.1324404761904762
                    ],
                    [
                        "Berry Pond Beach (DCR)",
                        0.12879635549872123
                    ],
                    [
                        "Chicopee Beach (DCR)",
                        0.12582236842105263
                    ],
                    [
                        "Stoddard Park",
                        0.12248774509803922
                    ],
                    [
                        "Watsons Pond (DCR)",
                        0.1223501461988304
                    ],
                    [
                        "Laurel Lake (DCR)",
                        0.11805555555555555
                    ],
                    [
                        "Upper Highland Lake - Day use area beach (DCR)",
                        0.11785130718954248
                    ],
                    [
                        "Benedict Pond Beach (DCR)",
                        0.11341589267285862
                    ],
                    [
                        "Morses Beach",
                        0.11282051282051282
                    ],
                    [
                        "Conway Swimming Pool",
                        0.1125
                    ],
                    [
                        "Camp Marshall Beach",
                        0.10912698412698413
                    ],
                    [
                        "Santuit Pond ",
                        0.10876688848558178
                    ],
                    [
                        "Upton Town Beach",
                        0.10653235653235653
                    ],
                    [
                        "St. Laurent Camp",
                        0.10590277777777778
                    ],
                    [
                        "Walden Pond - Main (DCR)",
                        0.10477941176470588
                    ],
                    [
                        "Lake Quinsigamond-Lake Park Beach (DCR)",
                        0.10294117647058823
                    ],
                    [
                        "Smith Pond",
                        0.10267857142857142
                    ],
                    [
                        "Arrive Lunenburg (Lake Whalom)",
                        0.10222630718954248
                    ],
                    [
                        "Whispering Pines Condo Association (Muddy Pond)",
                        0.10125291375291375
                    ],
                    [
                        "York Lake Beach (DCR)",
                        0.09791666666666667
                    ],
                    [
                        "Freetown Town Beach",
                        0.09578373015873015
                    ],
                    [
                        "Luther Hill Park",
                        0.09226190476190475
                    ],
                    [
                        "Homestead Residents Association (Crocker Pond)",
                        0.08928571428571427
                    ],
                    [
                        "Farm Pond",
                        0.08806818181818182
                    ],
                    [
                        "Saxonville Beach",
                        0.08607456140350876
                    ],
                    [
                        "Camp Gannet (Everwood/upper)",
                        0.08551864801864802
                    ],
                    [
                        "Camp Danbee",
                        0.08522727272727273
                    ],
                    [
                        "Hickory Hills (Brookview)",
                        0.08381410256410257
                    ],
                    [
                        "Indian Lake Public Beach (Sherburne Ave)",
                        0.08333333333333333
                    ],
                    [
                        "Crystal Lake",
                        0.08137239902080784
                    ],
                    [
                        "Hickory Hills (Hemlock Drive)",
                        0.08125
                    ],
                    [
                        "Ames Pond",
                        0.08055555555555555
                    ],
                    [
                        "Sherwood Forest - Boat Beach",
                        0.0804953560371517
                    ],
                    [
                        "Massaconet Shores",
                        0.07738095238095238
                    ],
                    [
                        "Hinkley ",
                        0.07726648351648352
                    ],
                    [
                        "Wells State Park - Walker Pond Beach (DCR)",
                        0.07569444444444444
                    ],
                    [
                        "Sesachacha Pond",
                        0.07478632478632478
                    ],
                    [
                        "Damon Pond Association Beach",
                        0.0734126984126984
                    ],
                    [
                        "Memorial Beach (Dug Pond) ",
                        0.07243712702472294
                    ],
                    [
                        "Becket Woods Road District - Beach",
                        0.07118055555555555
                    ],
                    [
                        "Forest Lake: Swimming Beach",
                        0.07083333333333333
                    ],
                    [
                        "Camp Russell",
                        0.06971153846153846
                    ],
                    [
                        "Lunenburg Town Beach",
                        0.06944444444444445
                    ],
                    [
                        "Ashfield Park Beach",
                        0.06887254901960785
                    ],
                    [
                        "Silver Pond Beach",
                        0.06818181818181818
                    ],
                    [
                        "Indian Lake Assoc - Niskayuna Beach",
                        0.06783088235294117
                    ],
                    [
                        "Cedar Lake Recreation Area",
                        0.06604516806722689
                    ],
                    [
                        "Sherwood Forest - Will Scarlett",
                        0.06470588235294118
                    ],
                    [
                        "Lakeland Beach",
                        0.0625
                    ],
                    [
                        "White Pines Condos (Stockbridge Bowl)",
                        0.0625
                    ],
                    [
                        "Wallum Lake (DCR)",
                        0.059742647058823525
                    ],
                    [
                        "Ice House Pond",
                        0.05631868131868132
                    ],
                    [
                        "Wayland Town Beach ",
                        0.05598118279569893
                    ],
                    [
                        "Tyngsborough Town Beach",
                        0.055098684210526314
                    ],
                    [
                        "Long Cove (Fresh)",
                        0.054945054945054944
                    ],
                    [
                        "Briarwood Mashpee Association",
                        0.054945054945054944
                    ],
                    [
                        "Long Pond (Depot St.)",
                        0.054945054945054944
                    ],
                    [
                        "Little Sandy",
                        0.054945054945054944
                    ],
                    [
                        "Sand Shores Association",
                        0.054945054945054944
                    ],
                    [
                        "Camp Yomechas",
                        0.054411764705882354
                    ],
                    [
                        "Indian Ranch",
                        0.05438899868247694
                    ],
                    [
                        "Lake Chauncy Beach",
                        0.05357142857142857
                    ],
                    [
                        "Wrights Pond ",
                        0.05295566502463054
                    ],
                    [
                        "Tom Denney Nature Camp",
                        0.05277777777777778
                    ],
                    [
                        "John's Pond",
                        0.05208333333333333
                    ],
                    [
                        "Edwards Town Beach",
                        0.050505050505050504
                    ],
                    [
                        "Lake Dennison State Park (DCR) ",
                        0.05012501865950142
                    ],
                    [
                        "Lake Wyola Association: West Beach",
                        0.05
                    ],
                    [
                        "Camp Good News",
                        0.05
                    ],
                    [
                        "John's Pond North Cove Association",
                        0.05
                    ],
                    [
                        "Halifax Beach Association",
                        0.05
                    ],
                    [
                        "Silver Lake",
                        0.05
                    ],
                    [
                        "Lake Pearl Restaurant",
                        0.049560041407867496
                    ],
                    [
                        "White Island Association",
                        0.049107142857142856
                    ],
                    [
                        "Lenox Town Beach (Laurel Lake)",
                        0.048642533936651584
                    ],
                    [
                        "Gull Pond Landing",
                        0.048039215686274506
                    ],
                    [
                        "Mascuppic",
                        0.04722222222222222
                    ],
                    [
                        "Collette Drive Beach",
                        0.046875
                    ],
                    [
                        "Sharon Town Beach ",
                        0.046583850931677016
                    ],
                    [
                        "Everwood Day Camp (Everwood/lower)",
                        0.04583333333333334
                    ],
                    [
                        "Santuit Pond Estates Association",
                        0.045454545454545456
                    ],
                    [
                        "Freeman Lake ",
                        0.045454545454545456
                    ],
                    [
                        "Indian Memorial",
                        0.044117647058823525
                    ],
                    [
                        "Stockbridge Town Beach (Stockbridge Bowl)",
                        0.044117647058823525
                    ],
                    [
                        "Snake Pond",
                        0.043560606060606064
                    ],
                    [
                        "Cochituate State Park Beach (DCR)",
                        0.043402777777777776
                    ],
                    [
                        "Nutting Lake - Micozzi Beach ",
                        0.04311965811965812
                    ],
                    [
                        "Sampson's Pond",
                        0.041666666666666664
                    ],
                    [
                        "John's Pond Estates Association (Fred's)",
                        0.041666666666666664
                    ],
                    [
                        "Walden Pond - Red Cross (DCR) ",
                        0.041666666666666664
                    ],
                    [
                        "Walker Pond - Main Beach",
                        0.04131652661064426
                    ],
                    [
                        "Morton Park ",
                        0.039818548387096774
                    ],
                    [
                        "Shangri-La",
                        0.03708791208791209
                    ],
                    [
                        "White Pond Cottages",
                        0.035897435897435895
                    ],
                    [
                        "Pinecrest Beach Improvement Association (Jenkins Pond)",
                        0.035897435897435895
                    ],
                    [
                        "Fresh Pond ",
                        0.03588516746411483
                    ],
                    [
                        "Dunroamin Park and Cottages",
                        0.03571428571428571
                    ],
                    [
                        "Mirror Lake",
                        0.03571428571428571
                    ],
                    [
                        "Camp Avoda",
                        0.03571428571428571
                    ],
                    [
                        "Camp Sequena ",
                        0.03485576923076923
                    ],
                    [
                        "Lochstead Association",
                        0.034523809523809526
                    ],
                    [
                        "Pinewood Lodge Campground",
                        0.03333333333333333
                    ],
                    [
                        "Queen Sewell Pond",
                        0.03333333333333333
                    ],
                    [
                        "Attaquin Park (Mashpee-Wakeby Pond)",
                        0.03333333333333333
                    ],
                    [
                        "Twin Lakes Condominiums",
                        0.03333333333333333
                    ],
                    [
                        "Mares Pond Association",
                        0.03333333333333333
                    ],
                    [
                        "Oldham Pond",
                        0.03333333333333333
                    ],
                    [
                        "Duck Pond",
                        0.03333333333333333
                    ],
                    [
                        "Camp Hi Rock - Main Beach",
                        0.03333333333333333
                    ],
                    [
                        "Sun Retreats Cape Cod (Round Pond)",
                        0.03333333333333333
                    ],
                    [
                        "Sunset Beach",
                        0.03333333333333333
                    ],
                    [
                        "Water-by Estates Homeowners Association",
                        0.03333333333333333
                    ],
                    [
                        "Wequaquet Estates Beach Association",
                        0.03333333333333333
                    ],
                    [
                        "Annawon Drive",
                        0.03229166666666666
                    ],
                    [
                        "Cordially Colony",
                        0.031746031746031744
                    ],
                    [
                        "Plunkett Lake Beach",
                        0.03137254901960784
                    ],
                    [
                        "Hammond Acres",
                        0.03125
                    ],
                    [
                        "Thousand Trails",
                        0.03125
                    ],
                    [
                        "Long Pond (Long Pond Drive)",
                        0.03125
                    ],
                    [
                        "Lee Town Beach",
                        0.03125
                    ],
                    [
                        "McDonald Beach",
                        0.03125
                    ],
                    [
                        "Orange Town Beach ",
                        0.03125
                    ],
                    [
                        "Camp Resolute ",
                        0.03125
                    ],
                    [
                        "Crystal Pond Homeowners Assoc Beach",
                        0.030330882352941176
                    ],
                    [
                        "Beachwood Assoc. ",
                        0.030330882352941176
                    ],
                    [
                        "Roger's Beach",
                        0.029411764705882353
                    ],
                    [
                        "Flax Pond (DCR)",
                        0.029411764705882353
                    ],
                    [
                        "Intercolonial Club of Marlborough",
                        0.029411764705882353
                    ],
                    [
                        "Windsor Lake",
                        0.029411764705882353
                    ],
                    [
                        "North Pond Beach (DCR)",
                        0.029411764705882353
                    ],
                    [
                        "King's Campground",
                        0.029411764705882353
                    ],
                    [
                        "Camp Taconic Beach",
                        0.027777777777777776
                    ],
                    [
                        "Sandbar Beach Club",
                        0.027777777777777776
                    ],
                    [
                        "Sherwood Forest - Arrow Beach",
                        0.027777777777777776
                    ],
                    [
                        "Crocker Pond",
                        0.027777777777777776
                    ],
                    [
                        "Richardson",
                        0.027777777777777776
                    ],
                    [
                        "Camp Overflow Beach",
                        0.027205882352941177
                    ],
                    [
                        "Sherwood Greens Road District Beach ",
                        0.026834659593280283
                    ],
                    [
                        "Bell Pond Beach",
                        0.025
                    ],
                    [
                        "S.P.E.N.A. Beach",
                        0.025
                    ],
                    [
                        "North Beach ",
                        0.02393162393162393
                    ],
                    [
                        "Peter's Pond Town Park 1",
                        0.022727272727272728
                    ],
                    [
                        "Danvers YMCA Daycamp",
                        0.022727272727272728
                    ],
                    [
                        "Merino Pond",
                        0.022727272727272728
                    ],
                    [
                        "Chilson Beach",
                        0.022727272727272728
                    ],
                    [
                        "Camp Mah-kee-nac",
                        0.022727272727272728
                    ],
                    [
                        "Flax Pond",
                        0.022727272727272728
                    ],
                    [
                        "Lake Waushacum",
                        0.020833333333333332
                    ],
                    [
                        "American Legion Park",
                        0.020833333333333332
                    ],
                    [
                        "Ellis Beach",
                        0.020833333333333332
                    ],
                    [
                        "Sweatt Beach",
                        0.020833333333333332
                    ],
                    [
                        "Sandpointe Shores Association Inc. - Rock Hollow",
                        0.020833333333333332
                    ],
                    [
                        "Cooper's Pond",
                        0.020833333333333332
                    ],
                    [
                        "Fells Pond Village Peninsula Council",
                        0.019230769230769232
                    ],
                    [
                        "Centennial Grove",
                        0.019230769230769232
                    ],
                    [
                        "Wequaquet Lake Yacht Club",
                        0.019230769230769232
                    ],
                    [
                        "Woods Pond Cabins",
                        0.019230769230769232
                    ],
                    [
                        "Higgins Pond",
                        0.019230769230769232
                    ],
                    [
                        "Long Pond (Cahoon Street)",
                        0.019230769230769232
                    ],
                    [
                        "Lithuanian Outing Assoc.",
                        0.019230769230769232
                    ],
                    [
                        "Sunset Lake ",
                        0.019230769230769232
                    ],
                    [
                        "Mashpee Shores Association",
                        0.019230769230769232
                    ],
                    [
                        "Jimmy's Beach (Wequaquet Heights Association) ",
                        0.017879948914431672
                    ],
                    [
                        "Lakewood Hills Property Owners Association",
                        0.017857142857142856
                    ],
                    [
                        "Craig Road Beach",
                        0.017857142857142856
                    ],
                    [
                        "Cranberry Bog Homeowner's Association (Big Sandy Pond)",
                        0.017857142857142856
                    ],
                    [
                        "Gull Pond (2) - Steele Rd.",
                        0.017857142857142856
                    ],
                    [
                        "Long Pond Farms Neighborhood Association",
                        0.017857142857142856
                    ],
                    [
                        "Lovell's Pond",
                        0.017857142857142856
                    ],
                    [
                        "Richmond Pond Association",
                        0.017857142857142856
                    ],
                    [
                        "Coonamessett Pond",
                        0.017857142857142856
                    ],
                    [
                        "Holly Point Beach and Tennis Association",
                        0.017857142857142856
                    ],
                    [
                        "Buck's Pond",
                        0.017857142857142856
                    ],
                    [
                        "Wianno Club (Crystal Lake)",
                        0.017857142857142856
                    ],
                    [
                        "Lawrence Pond Village Campground",
                        0.017857142857142856
                    ],
                    [
                        "Blueberry Hills Property Owners Association",
                        0.017857142857142856
                    ],
                    [
                        "Wequaquet Lake Town",
                        0.017857142857142856
                    ],
                    [
                        "Pout Pond Beach",
                        0.017857142857142856
                    ],
                    [
                        "Sand Pond",
                        0.017857142857142856
                    ],
                    [
                        "Robinwood Homeowners Association (Owl Pond)",
                        0.017857142857142856
                    ],
                    [
                        "Slough Pond",
                        0.017857142857142856
                    ],
                    [
                        "Hathaway's Pond",
                        0.017857142857142856
                    ],
                    [
                        "Blackmore Pond",
                        0.017857142857142856
                    ],
                    [
                        "Stetson",
                        0.017857142857142856
                    ],
                    [
                        "Otis Town Beach",
                        0.016666666666666666
                    ],
                    [
                        "Littleton Town Beach",
                        0.016666666666666666
                    ],
                    [
                        "Plainfield Pond",
                        0.016666666666666666
                    ],
                    [
                        "Baby Beach Lost Lake",
                        0.016666666666666666
                    ],
                    [
                        "Upper Mill Pond",
                        0.016666666666666666
                    ],
                    [
                        "Baird Center (Bloody Pond)",
                        0.016666666666666666
                    ],
                    [
                        "Lake Garfield",
                        0.016666666666666666
                    ],
                    [
                        "Village Green Family Campground",
                        0.016666666666666666
                    ],
                    [
                        "Hood Pond-boat ramp",
                        0.016666666666666666
                    ],
                    [
                        "East Boston Camps - Girls Beach",
                        0.015625
                    ],
                    [
                        "East Boston Camps - Boys Beach",
                        0.015625
                    ],
                    [
                        "Lake Mansfield",
                        0.015625
                    ],
                    [
                        "Asnacomet Pond Beach (DCR) ",
                        0.015625
                    ],
                    [
                        "Curlew Pond (DCR)",
                        0.015625
                    ],
                    [
                        "Berry's Grove Campground",
                        0.015625
                    ],
                    [
                        "Cliff Pond (DCR) ",
                        0.015625
                    ],
                    [
                        "Center Lake Estates Beach",
                        0.015625
                    ],
                    [
                        "Colonial Park",
                        0.015625
                    ],
                    [
                        "Nabnassett American Legion",
                        0.015625
                    ],
                    [
                        "Richard P. Sharon Beach",
                        0.015625
                    ],
                    [
                        "Rowe Town Beach at Pelham Park ",
                        0.015625
                    ],
                    [
                        "Pilgrim Lake",
                        0.015625
                    ],
                    [
                        "Henry F Collins Beach",
                        0.015625
                    ],
                    [
                        "Sandy Beach ",
                        0.015238704177323103
                    ],
                    [
                        "Annursnac Hill Assoc.",
                        0.014705882352941176
                    ],
                    [
                        "Mohawk Estates ",
                        0.014705882352941176
                    ],
                    [
                        "Sherwood Forest - Excalibur",
                        0.014705882352941176
                    ],
                    [
                        "Hilltop",
                        0.014705882352941176
                    ],
                    [
                        "Camp Clark YMCA - Hyles Pond",
                        0.014705882352941176
                    ],
                    [
                        "Pleasant Pond Beach",
                        0.014705882352941176
                    ],
                    [
                        "Dennis Pond",
                        0.014705882352941176
                    ],
                    [
                        "Indian Lake Assoc - Dam Beach ",
                        0.013888888888888888
                    ],
                    [
                        "Musante Beach",
                        0.013888888888888888
                    ],
                    [
                        "Camp Becket - Main Beach",
                        0.013888888888888888
                    ],
                    [
                        "Lakeside",
                        0.013157894736842105
                    ],
                    [
                        "Walker Pond (Oak Cove)",
                        0.011904761904761904
                    ],
                    [
                        "Ellis Haven",
                        0.011363636363636364
                    ],
                    [
                        "Plugs Pond ",
                        0.010869565217391304
                    ],
                    [
                        "Beechwood Landing Property Owners Association",
                        0.01
                    ],
                    [
                        "John's Pond (Public) ",
                        0.009259259259259259
                    ],
                    [
                        "Long Pond",
                        0.009259259259259259
                    ],
                    [
                        "Pomps Pond ",
                        0.005952380952380952
                    ],
                    [
                        "Summer Beach ",
                        0.005813953488372093
                    ],
                    [
                        "Upper Highland Lake - Campers Beach (DCR)",
                        0.0
                    ],
                    [
                        "Tunxis Club",
                        0.0
                    ],
                    [
                        "The Trustees  - Lowell Holly (Wakeby Pond)",
                        0.0
                    ],
                    [
                        "Camp Farley (Mashpee-Wakeby Pond)",
                        0.0
                    ],
                    [
                        "Wales Town Beach",
                        0.0
                    ],
                    [
                        "The Pines",
                        0.0
                    ],
                    [
                        "The Trail at Big Alum Lake Association Beach",
                        0.0
                    ],
                    [
                        "The Trustees  - Lowell Holly (Mashpee Pond)",
                        0.0
                    ],
                    [
                        "Wildwood - Meadow",
                        0.0
                    ],
                    [
                        "Thunderbridge ",
                        0.0
                    ],
                    [
                        "Treasure Island Condominiums",
                        0.0
                    ],
                    [
                        "Lake Wyola Association: North Beach",
                        0.0
                    ],
                    [
                        "Lake Wyola Association: East Beach",
                        0.0
                    ],
                    [
                        "Lakeside Meadows",
                        0.0
                    ],
                    [
                        "Lakefield Farms Trust",
                        0.0
                    ],
                    [
                        "Horse Pond",
                        0.0
                    ],
                    [
                        "Indian Head Resort",
                        0.0
                    ],
                    [
                        "Indian Lake Assoc - Boulder Beach",
                        0.0
                    ],
                    [
                        "Hood's Pond",
                        0.0
                    ],
                    [
                        "Indian Lake Assoc - Forest Beach",
                        0.0
                    ],
                    [
                        "Lake Boone",
                        0.0
                    ],
                    [
                        "Kildeer Island (AKA Sandy Shore)",
                        0.0
                    ],
                    [
                        "Lake Attitash - A.L.S.I.A.",
                        0.0
                    ],
                    [
                        "Joshua's Pond",
                        0.0
                    ],
                    [
                        "Jemima Pond",
                        0.0
                    ],
                    [
                        "Italian-American Sporting Club",
                        0.0
                    ],
                    [
                        "Island Grove Beach",
                        0.0
                    ],
                    [
                        "Heart Pond",
                        0.0
                    ],
                    [
                        "Gull Pond",
                        0.0
                    ],
                    [
                        "Halcyon Condominiums/Horse Pond Corporation",
                        0.0
                    ],
                    [
                        "Hamblin's Pond",
                        0.0
                    ],
                    [
                        "Hedges Pond",
                        0.0
                    ],
                    [
                        "Hartsuff Park",
                        0.0
                    ],
                    [
                        "Arcand Park Beach",
                        0.0
                    ],
                    [
                        "Grotonwood Camp",
                        0.0
                    ],
                    [
                        "Great Sand Lakes Association - Vacation Ln. (John Joseph Pond)",
                        0.0
                    ],
                    [
                        "Grew's Pond",
                        0.0
                    ],
                    [
                        "Grossman Beach",
                        0.0
                    ],
                    [
                        "Great Sand Lakes Association - Clearwater Dr. (Bucks Pond)",
                        0.0
                    ],
                    [
                        "Hinkley's Pond",
                        0.0
                    ],
                    [
                        "Holmes Street",
                        0.0
                    ],
                    [
                        "Hickory Hills (Island Rd.)",
                        0.0
                    ],
                    [
                        "Herring Pond",
                        0.0
                    ],
                    [
                        "Fearings Pond (DCR) ",
                        0.0
                    ],
                    [
                        "Grove",
                        0.0
                    ],
                    [
                        "Groton Town Beach (Sargisson Beach)",
                        0.0
                    ],
                    [
                        "Camp Burgess",
                        0.0
                    ],
                    [
                        "East Beach - Beaver Lake",
                        0.0
                    ],
                    [
                        "Forge Village Beach",
                        0.0
                    ],
                    [
                        "East Boston Camps - Day Care",
                        0.0
                    ],
                    [
                        "Ashumet Valley Property Owners, Inc./Holly Sands Homeowners Corp.",
                        0.0
                    ],
                    [
                        "Wakeby Pond",
                        0.0
                    ],
                    [
                        "Valley Pond",
                        0.0
                    ],
                    [
                        "White Pond Assoc",
                        0.0
                    ],
                    [
                        "Wildwood - Lakeside",
                        0.0
                    ],
                    [
                        "Wildwood - Main Beach",
                        0.0
                    ],
                    [
                        "White Pond Town Landing",
                        0.0
                    ],
                    [
                        "Wildwood - Fox Den",
                        0.0
                    ],
                    [
                        "West Beach - Beaver Lake",
                        0.0
                    ],
                    [
                        "Wiley Park",
                        0.0
                    ],
                    [
                        "Wildwood - Otter Pond Beach",
                        0.0
                    ],
                    [
                        "College Pond Day Use (DCR)",
                        0.0
                    ],
                    [
                        "Cooper Creek HOA",
                        0.0
                    ],
                    [
                        "Moores Pond Beach",
                        0.0
                    ],
                    [
                        "Mountain Grove Assoc. Beach",
                        0.0
                    ],
                    [
                        "Cranberry Cove (aka Camp Kiwanee)",
                        0.0
                    ],
                    [
                        "Country Club of Pittsfield",
                        0.0
                    ],
                    [
                        "Center Pond Beach",
                        0.0
                    ],
                    [
                        "Charge Pond (DCR)",
                        0.0
                    ],
                    [
                        "Lancaster Town Beach",
                        0.0
                    ],
                    [
                        "Lingan Street",
                        0.0
                    ],
                    [
                        "Lake Manchaug Camping",
                        0.0
                    ],
                    [
                        "Lake House at Laurel Lake",
                        0.0
                    ],
                    [
                        "Little Sandy Pond",
                        0.0
                    ],
                    [
                        "Long Pond (Rte 124)",
                        0.0
                    ],
                    [
                        "Camp Romaca ",
                        0.0
                    ],
                    [
                        "Camp Stepping Stone",
                        0.0
                    ],
                    [
                        "Camp Stevenson/Witawentin",
                        0.0
                    ],
                    [
                        "Camp Watitoh Beach",
                        0.0
                    ],
                    [
                        "Camp Winadu",
                        0.0
                    ],
                    [
                        "Noble's Cove Beach",
                        0.0
                    ],
                    [
                        "Nauset Haven Condo Association (Minister's Pond)",
                        0.0
                    ],
                    [
                        "NARA Beach",
                        0.0
                    ],
                    [
                        "Onota Lake - Decom Beach",
                        0.0
                    ],
                    [
                        "Onota Lake - Controy Pavillion",
                        0.0
                    ],
                    [
                        "Onota Lake - Public Beach at Burbank Park",
                        0.0
                    ],
                    [
                        "North Beach (NIA)",
                        0.0
                    ],
                    [
                        "Lyman Lane",
                        0.0
                    ],
                    [
                        "Maple Park Campground ",
                        0.0
                    ],
                    [
                        "Peter's Pond RV Park ",
                        0.0
                    ],
                    [
                        "Otis Reservoir Beach (DCR)",
                        0.0
                    ],
                    [
                        "Goose Pond",
                        0.0
                    ],
                    [
                        "Goose Pond at Leisure Lee Rd.",
                        0.0
                    ],
                    [
                        "Great Pond",
                        0.0
                    ],
                    [
                        "Minister's Pond",
                        0.0
                    ],
                    [
                        "Marylou's Beach (NIA)",
                        0.0
                    ],
                    [
                        "Middle Pond",
                        0.0
                    ],
                    [
                        "Memorial Beach ",
                        0.0
                    ],
                    [
                        "Massapoag Yacht Club",
                        0.0
                    ],
                    [
                        "Sandy Pond Campground",
                        0.0
                    ],
                    [
                        "Sandy Shore Association (Aunt Edies Pond) ",
                        0.0
                    ],
                    [
                        "Pinecrest Property Owners Assoc.",
                        0.0
                    ],
                    [
                        "Pontoosuc Lake - Decom Beach",
                        0.0
                    ],
                    [
                        "Plymouth Estates",
                        0.0
                    ],
                    [
                        "Camp Hayward",
                        0.0
                    ],
                    [
                        "Camp Lyndon",
                        0.0
                    ],
                    [
                        "Camp Lowe Beach",
                        0.0
                    ],
                    [
                        "Summer Village Main Beach",
                        0.0
                    ],
                    [
                        "Sunrise Beach",
                        0.0
                    ],
                    [
                        "Templeton Fish and Game Club",
                        0.0
                    ],
                    [
                        "Richmond Town Beach",
                        0.0
                    ],
                    [
                        "Richmond Shores South Pond",
                        0.0
                    ],
                    [
                        "Sandy Beach (NIA)",
                        0.0
                    ],
                    [
                        "Sandpointe Shores Association Inc. - Whitecaps",
                        0.0
                    ],
                    [
                        "Rolling Ridge Farm Homeowners Association (Lawrence Pond)",
                        0.0
                    ],
                    [
                        "Princess Beach-Scargo Lake",
                        0.0
                    ],
                    [
                        "Regency Drive Homeowners Association ",
                        0.0
                    ],
                    [
                        "Camp Hi Rock - Bear Rock Beach",
                        0.0
                    ],
                    [
                        "Stiles Pond Beach",
                        0.0
                    ],
                    [
                        "South Shore YMCA - Triangle Pond",
                        0.0
                    ],
                    [
                        "South Beach - Beaver Lake",
                        0.0
                    ],
                    [
                        "Sichols",
                        0.0
                    ],
                    [
                        "Card Pond Beach",
                        0.0
                    ],
                    [
                        "Schoolhouse Pond",
                        0.0
                    ],
                    [
                        "Seymour Pond",
                        0.0
                    ],
                    [
                        "Shady Lane Homeowners Association",
                        0.0
                    ],
                    [
                        "Shady Point Campground",
                        0.0
                    ],
                    [
                        "Sheep Pond Beach Association",
                        0.0
                    ],
                    [
                        "Sheep Pond Landing",
                        0.0
                    ],
                    [
                        "Camp Wind-in-the-Pines ",
                        0.0
                    ],
                    [
                        "Camp Wingate - Kirland",
                        0.0
                    ],
                    [
                        "Blueberry Hill Camp (Curlew Pond)",
                        0.0
                    ],
                    [
                        "Bolton Town Beach",
                        0.0
                    ],
                    [
                        "Wallum Lake Terrace",
                        0.0
                    ],
                    [
                        "Breezy Picnic Grounds",
                        0.0
                    ],
                    [
                        "Scargo Lake",
                        0.0
                    ],
                    [
                        "Berkshire Lake Estates",
                        0.0
                    ],
                    [
                        "Beacon Park Condominiums",
                        0.0
                    ],
                    [
                        "Barrett Pond (DCR)",
                        0.0
                    ]
                ]
```
<!-- /original:subtask.6.answer -->

### 子任务 7：environment-hard-15-7

问题原文：

<!-- original:subtask.7.query chars:63 -->
```text
Which beach has the highest average exceedance rate since 2020?
```
<!-- /original:subtask.7.query -->

标准答案原文：

<!-- original:subtask.7.answer chars:22 -->
```text
Damon Pond Beach (DCR)
```
<!-- /original:subtask.7.answer -->

## 5. 逐步记录

每一步对应一次模型回复；原 `call` 和执行 `step` 另列。只保存该次回复一份，不重复请求历史或 provider_response 副本。没有 tool 历史反馈时不以本地输出补写。原文字段由 HTML 标记和字符长度定位，代码围栏前的展示换行不计入原文。

### 第 1 步（模型 call=1；执行 step=1）

#### 模型可读输出

`content=null`。

可读 reasoning 原文（`reasoning`）：

<!-- original:step.1.reasoning.1 chars:426 -->
```text
**Assessing data for analysis**

I need to conduct a data analysis by inspecting files related to freshwater beach bacterial exceedance rates. The goal is to identify candidate beaches between 2020 and 2023. To start, I’ll make a list of files to inspect, focusing on the relevant sheets and CSV formats. This should help me derive the necessary insights effectively, ensuring I cover the right data points across those years!
```
<!-- /original:step.1.reasoning.1 -->

有加密 reasoning，2284 字符

同一步中逐字相同的 reasoning / reasoning_details 文本只保留一份。

#### 执行的代码

<!-- original:step.1.code chars:279 -->
```python
import os, pandas as pd
p='/home/katherine/dac/benchmarks/KramaBench/data/environment/input'
print(os.listdir(p))
for f in os.listdir(p):
 if 'datasheet' in f:
  d=pd.read_csv(os.path.join(p,f))
  print('\n',f,d.shape,d.columns.tolist())
  print(d.head(3).to_string(index=False))
```
<!-- /original:step.1.code -->

#### 模型实际看到的执行反馈

模型看到的被截断：看到 4000 字符，完整输出 7451 字符

<!-- original:step.1.feedback chars:4000 -->
```text
['malibu_beach_datasheet.csv', 'water-body-testing-2003.csv', 'water-body-testing-2019.csv', 'water-body-testing-2015.csv', 'precipitations_beaches_community.csv', 'carson_beach_datasheet.csv', 'water-body-testing-2013.csv', 'water-body-testing-2010.csv', 'water-body-testing-2007.csv', 'city_point_beach_datasheet.csv', 'water-body-testing-2020.csv', 'boston-harbor-beaches.txt', 'water-body-testing-2017.csv', 'constitution_beach_datasheet.csv', 'water-body-testing-2014.csv', 'm_street_beach_datasheet.csv', 'water-body-testing-2011.csv', 'monthly_precipitations_chatham.csv', 'water-body-testing-2012.csv', 'water-body-testing-2005.csv', 'monthly_precipitations_amherst.csv', 'water-body-testing-2021.csv', 'water-body-testing-2016.csv', 'wollaston_beach_datasheet.csv', 'environmental-justice-populations.csv', 'water-body-testing-2009.csv', 'water-body-testing-2004.csv', 'water-body-testing-2018.csv', 'water-body-testing-2008.csv', 'pleasure_bay_and_castle_island_beach_datasheet.csv', 'water-body-testing-2006.csv', 'tenean_beach_datasheet.csv', 'water-body-testing-2023.csv', 'water-body-testing-2002.csv', 'monthly_precipitations_ashburnham.csv', 'monthly_precipitations_boston.csv', 'water-body-testing-2022.csv']

 malibu_beach_datasheet.csv (1160, 6) ['Malibu Beach, Dorchester: Bacterial Water Quality', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5']
Malibu Beach, Dorchester: Bacterial Water Quality Unnamed: 1 Unnamed: 2 Unnamed: 3   Unnamed: 4   Unnamed: 5
                                              NaN        NaN        NaN        NaN Malibu Beach          NaN
                                             Date 1-Day Rain 2-Day Rain 3-Day Rain          Tag Enterococcus
                                September 1, 2024          0          0          0          NaN           41

 carson_beach_datasheet.csv (1134, 8) ['Carson Beach, South Boston: Bacterial Water Quality', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 
... [output truncated] ...
Date 1-Day Rain 2-Day Rain 3-Day Rain         Tag Enterococcus             Tag Enterococcus           Tag Enterococcus         Tag Enterococcus
                               September 1, 2024          0          0          0         NaN           10               <           10             <           10           <           10

 pleasure_bay_and_castle_island_beach_datasheet.csv (862, 10) ['Pleasure Bay Beach, South Boston: Bacterial Water Quality', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9']
Pleasure Bay Beach, South Boston: Bacterial Water Quality Unnamed: 1 Unnamed: 2 Unnamed: 3              Unnamed: 4   Unnamed: 5              Unnamed: 6   Unnamed: 7               Unnamed: 8   Unnamed: 9
                                                      NaN        NaN        NaN        NaN Pleasure Bay @ Broadway          NaN Pleasure Bay @ Flagpole          NaN Castle Island Playground          NaN
                                                     Date 1-Day Rain 2-Day Rain 3-Day Rain                     Tag Enterococcus                     Tag Enterococcus                      Tag Enterococcus
                                          August 27, 2024       0.00          0          0                     NaN           30                     NaN           10                      NaN           20

 tenean_beach_datasheet.csv (1882, 6) ['Tenean Beach, Dorchester: Bacterial Water Quality', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5']
Tenean Beach, Dorchester: Bacterial Water Quality Unnamed: 1 Unnamed: 2 Unnamed: 3 Unnamed: 4   Unnamed: 5
                                              NaN        NaN        NaN        NaN     Middle          NaN
                                             Date 1-Day Rain 2-Day Rain 3-Day Rain        Tag Enterococcus
                                September 1, 2024          0          0          0          <           10
```
<!-- /original:step.1.feedback -->

#### files_read 原字段

<!-- original:step.1.files_read chars:319 -->
```json
["data/carson_beach_datasheet.csv", "data/city_point_beach_datasheet.csv", "data/constitution_beach_datasheet.csv", "data/m_street_beach_datasheet.csv", "data/malibu_beach_datasheet.csv", "data/pleasure_bay_and_castle_island_beach_datasheet.csv", "data/tenean_beach_datasheet.csv", "data/wollaston_beach_datasheet.csv"]
```
<!-- /original:step.1.files_read -->

### 第 2 步（模型 call=2；执行 step=2）

#### 模型可读输出

`content=null`。

可读 reasoning 原文（`reasoning`）：

<!-- original:step.2.reasoning.1 chars:486 -->
```text
**Inspecting data structures**

I need to take a closer look at all the structure headers and year data. It seems the data sheets focus on beach surfaces rather than freshwater. This likely involves inland bathing water records from a water-body testing dataset. Maybe the beaches I'm considering are all saltwater, aside from possibly "Tenean," which might be a freshwater beach. I should confirm the freshwater identities and exceedance rates in the datasets regarding Boston beaches.
```
<!-- /original:step.2.reasoning.1 -->

有加密 reasoning，3008 字符

同一步中逐字相同的 reasoning / reasoning_details 文本只保留一份。

#### 执行的代码

<!-- original:step.2.code chars:179 -->
```python
for yr in [2020,2021,2022,2023]:
 d=pd.read_csv(os.path.join(p,f'water-body-testing-{yr}.csv'))
 print('\n',yr,d.shape,d.columns.tolist())
 print(d.head(4).to_string(index=False))
```
<!-- /original:step.2.code -->

#### 模型实际看到的执行反馈

模型看到的被截断：看到 4000 字符，完整输出 4200 字符

<!-- original:step.2.feedback chars:4000 -->
```text

 2020 (14796, 11) ['Community Code', 'Community', 'County Code', 'County Description', 'Year', 'Sample Date', 'Beach Name', 'Beach Type Description', 'Organism', 'Indicator Level', 'Violation']
 Community Code    Community  County Code County Description  Year         Sample Date            Beach Name Beach Type Description    Organism  Indicator Level Violation
            242 Provincetown            1         Barnstable  2020 2020-08-03 00:00:00 333 Commercial Street                 Marine Enterococci              5.0        No
            242 Provincetown            1         Barnstable  2020 2020-07-13 00:00:00 333 Commercial Street                 Marine Enterococci             10.0        No
            242 Provincetown            1         Barnstable  2020 2020-06-22 00:00:00 333 Commercial Street                 Marine Enterococci             10.0        No
            242 Provincetown            1         Barnstable  2020 2020-06-15 00:00:00 333 Commercial Street                 Marine Enterococci              5.0        No

 2021 (16020, 11) ['Community Code', 'Community', 'County Code', 'County Description', 'Year', 'Sample Date', 'Beach Name', 'Beach Type Description', 'Organism', 'Indicator Level', 'Violation']
 Community Code    Community  County Code County Description  Year         Sample Date            Beach Name Beach Type Description    Organism  Indicator Level Violation
            242 Provincetown            1         Barnstable  2021 2021-08-02 00:00:00 333 Commercial Street                 Marine Enterococci             20.0        NO
            242 Provincetown            1         Barnstable  2021 2021-07-19 00:00:00 333 Commercial Street                 Marine Enterococci             10.0        NO
            242 Provincetown            1         Barnstable  2021 2021-08-16 00:00:00 333 Commercial Street                 Marine Enterococci             31.0        NO
            242 Provincetown            1         Barnsta
... [output truncated] ...
ach Name', 'Beach Type Description', 'Organism', 'Indicator Level', 'Violation']
 Community Code    Community  County Code County Description  Year         Sample Date            Beach Name Beach Type Description    Organism  Indicator Level Violation
            242 Provincetown            1         Barnstable  2022 2022-08-08 00:00:00 333 Commercial Street                 Marine Enterococci              5.0        No
            242 Provincetown            1         Barnstable  2022 2022-06-21 00:00:00 333 Commercial Street                 Marine Enterococci              5.0        No
            242 Provincetown            1         Barnstable  2022 2022-08-23 00:00:00 333 Commercial Street                 Marine Enterococci              5.0        No
            242 Provincetown            1         Barnstable  2022 2022-06-06 00:00:00 333 Commercial Street                 Marine Enterococci             10.0        No

 2023 (16258, 11) ['Community Code', 'Community', 'County Code', 'County Description', 'Year', 'Sample Date', 'Beach Name', 'Beach Type Description', 'Organism', 'Indicator Level', 'Violation']
 Community Code    Community  County Code County Description  Year         Sample Date            Beach Name Beach Type Description    Organism  Indicator Level Violation
            242 Provincetown            1         Barnstable  2023 2023-07-10 00:00:00 333 Commercial Street                 Marine Enterococci              5.0        No
            242 Provincetown            1         Barnstable  2023 2023-06-05 00:00:00 333 Commercial Street                 Marine Enterococci             10.0        No
            242 Provincetown            1         Barnstable  2023 2023-08-07 00:00:00 333 Commercial Street                 Marine Enterococci             20.0        No
            242 Provincetown            1         Barnstable  2023 2023-08-28 00:00:00 333 Commercial Street                 Marine Enterococci             87.0        No
```
<!-- /original:step.2.feedback -->

#### files_read 原字段

<!-- original:step.2.files_read chars:144 -->
```json
["data/water-body-testing-2020.csv", "data/water-body-testing-2021.csv", "data/water-body-testing-2022.csv", "data/water-body-testing-2023.csv"]
```
<!-- /original:step.2.files_read -->

### 第 3 步（模型 call=3；执行 step=3）

#### 模型可读输出

`content=null`。

可读 reasoning 原文（`reasoning`）：

<!-- original:step.3.reasoning.1 chars:468 -->
```text
**Analyzing freshwater data**

I need to analyze the types of freshwater data by concatenating yearly counts. My goal is to identify beaches that have been observed every year and calculate their average violation or exceedance rate. For me, defining an exceedance likely means a confirmed violation, which includes the fraction of samples that indicate that. I also need to think about normalizing these violation values to ensure accuracy. Let's get to work on that!
```
<!-- /original:step.3.reasoning.1 -->

有加密 reasoning，2324 字符

同一步中逐字相同的 reasoning / reasoning_details 文本只保留一份。

#### 执行的代码

<!-- original:step.3.code chars:605 -->
```python
dfs=[]
for yr in range(2020,2024):
 d=pd.read_csv(os.path.join(p,f'water-body-testing-{yr}.csv'))
 dfs.append(d)
allD=pd.concat(dfs,ignore_index=True)
print(allD['Beach Type Description'].value_counts(dropna=False))
print('\nViolation values',allD.Violation.value_counts(dropna=False))
print('\nOrganisms',allD.Organism.value_counts(dropna=False))
print('\nFreshwater beach types example')
f=allD[allD['Beach Type Description'].astype(str).str.contains('fresh',case=False,na=False)]
print(f.shape, f['Beach Name'].nunique())
print(f.groupby(['Beach Name','Year']).size().unstack(fill_value=0).to_string())
```
<!-- /original:step.3.code -->

#### 模型实际看到的执行反馈

模型看到的被截断：看到 4000 字符，完整输出 83756 字符

<!-- original:step.3.feedback chars:4000 -->
```text
Beach Type Description
Marine    33571
Fresh     29589
Name: count, dtype: int64

Violation values Violation
No     44445
NO     14835
Yes     2713
YES     1167
Name: count, dtype: int64

Organisms Organism
Enterococci    37770
E. Coli        25390
Name: count, dtype: int64

Freshwater beach types example
(29589, 11) 607
Year                                                                                                              2020  2021  2022  2023
Beach Name                                                                                                                              
9 Mile Pond                                                                                                          0     0     1     0
American Legion Park                                                                                                12    13    12     7
Ames Pond                                                                                                           10     9     8    10
Annawon Drive                                                                                                       16    15    15    15
Annursnac Hill Assoc.                                                                                               16    17    17    16
Arcand Park Beach                                                                                                    7    14    15    15
Arlington Reservoir                                                                                                  0    13    22    21
Arrive Lunenburg (Lake Whalom)                                                                                      17    16    16    18
Ashfield Park Beach                                                                                                 12    15    17    12
Ashland Reservoir-Main Beach (DCR)                                                                                  17    18    17    17
Ashumet Valley Prop
... [output truncated] ...
                                               15    17    16    15
Wildwood - Meadow                                                                                                   15    17    16    16
Wildwood - Otter Pond Beach                                                                                         15    17    16    15
Wiley Park                                                                                                          14    13    13    13
Wilmington Town Beach @ Center                                                                                       0    12     9    11
Wilmington Town Beach @ Right                                                                                        0    11     9    11
Wind-in-the-Pines - Day Camp @ Day Camp                                                                              0     0     0     9
Wind-in-the-Pines - Residents Camp                                                                                   0     1    10     9
Windsor Lake                                                                                                        17    16    17    15
Woods Pond Cabins                                                                                                   11    12    10    13
Wrights Pond @ Deep End                                                                                             17    13    15    13
Wrights Pond @ Shallow End                                                                                          18    16    15    13
YMCA Beach @ Massapoag Pond                                                                                          0    12    14    14
YMCA Camp Norwich Beach                                                                                              0     0     0    11
York Lake Beach (DCR)                                                                                               15    15    16    15
```
<!-- /original:step.3.feedback -->

#### files_read 原字段

<!-- original:step.3.files_read chars:144 -->
```json
["data/water-body-testing-2020.csv", "data/water-body-testing-2021.csv", "data/water-body-testing-2022.csv", "data/water-body-testing-2023.csv"]
```
<!-- /original:step.3.files_read -->

### 第 4 步（模型 call=4；执行 step=4）

#### 模型可读输出

`content=null`。

无可读 reasoning 文本。

有加密 reasoning，3860 字符

#### 执行的代码

<!-- original:step.4.code chars:823 -->
```python
fresh=allD[allD['Beach Type Description'].eq('Fresh')].copy()
fresh['viol']=fresh.Violation.astype(str).str.strip().str.lower().eq('yes')
years={2020,2021,2022,2023}
counts=fresh.groupby('Beach Name').Year.agg(lambda x:set(x))
complete=counts[counts.map(lambda s:s==years)].index
cf=fresh[fresh['Beach Name'].isin(complete)]
print('fresh beaches',fresh['Beach Name'].nunique(),'complete',len(complete))
# total rate and mean of yearly rates
annual=cf.groupby(['Beach Name','Year']).viol.mean().unstack()
summary=pd.DataFrame({'avg_annual_rate':annual.mean(axis=1),'pooled_rate':cf.groupby('Beach Name').viol.mean(),'samples':cf.groupby('Beach Name').size()}).sort_values('avg_annual_rate',ascending=False)
print(summary.head(20).to_string())
print('\nYearly details leader')
print(annual.loc[summary.index[:5]].to_string())
```
<!-- /original:step.4.code -->

#### 模型实际看到的执行反馈

<!-- original:step.4.feedback chars:2516 -->
```text
fresh beaches 607 complete 448
                                                   avg_annual_rate  pooled_rate  samples
Beach Name                                                                              
Damon Pond Beach (DCR)                                    0.580775     0.583333       72
Beamans Pond - Day Use (DCR)                              0.478628     0.478873       71
Beamans Pond - Campground (DCR)                           0.475219     0.485714       70
Robinson Pond Beach (DCR)                                 0.465152     0.479452       73
Pearl Hill Pond Beach (DCR)                               0.406618     0.391304       69
Waushakum Beach                                           0.405247     0.405797       69
Seth's Pond @ Town Beach                                  0.377747     0.372549       51
Learned Pond Beach                                        0.363134     0.327869       61
Lake Quinsigamond-Regatta Point Beach (DCR)               0.359440     0.354430       79
Community Center Beach                                    0.351498     0.352941       68
Bass Pond @ Right                                         0.310839     0.318182       44
Merrimac River - Bath House                               0.281594     0.292308       65
Puffers Pond (AKA Factory Hollow Pond) @ Mill St.         0.273981     0.262295       61
Dunn Pond (DCR)                                           0.273531     0.298507       67
Peckham Pond @ Camp Nihan (DCR)                           0.272567     0.329412       85
Shannon Beach @ Upper Mystic (DCR)                        0.270238     0.310000      100
Camp Wilder @ Right                                       0.264899     0.222222       36
Lake Wyola (DCR)                                          0.253676     0.257143       70
Hopkinton Reservoir-Main Beach (DCR)                      0.242851     0.263158       76
Eagle Lake                                                0.233333     0.220000       50

Yearly details leader
Year                                 2020      2021      2022      2023
Beach Name                                                             
Damon Pond Beach (DCR)           0.684211  0.750000  0.222222  0.666667
Beamans Pond - Day Use (DCR)     0.133333  0.684211  0.363636  0.733333
Beamans Pond - Campground (DCR)  0.066667  0.684211  0.400000  0.750000
Robinson Pond Beach (DCR)        0.000000  0.400000  0.727273  0.733333
Pearl Hill Pond Beach (DCR)      0.200000  0.500000  0.176471  0.750000
```
<!-- /original:step.4.feedback -->

#### files_read 原字段

<!-- original:step.4.files_read chars:2 -->
```json
[]
```
<!-- /original:step.4.files_read -->

### 第 5 步（模型 call=5；执行 step=5）

#### 模型可读输出

`content=null`。

可读 reasoning 原文（`reasoning`）：

<!-- original:step.5.reasoning.1 chars:492 -->
```text
**Analyzing beach data**

I'm considering Damon Pond Beach (DCR) with an average exceedance rate of around 58%. I need to ensure I clarify the metric for the "average exceedance rate since 2020," looking at both annual rates and counts per beach. Also, I’m wondering about the potential for duplicate beach names across different communities and how that could cause confusion. I'll check the specifics for Damon and might need to pull further details from the dataset to support my findings.
```
<!-- /original:step.5.reasoning.1 -->

有加密 reasoning，3392 字符

同一步中逐字相同的 reasoning / reasoning_details 文本只保留一份。

#### 执行的代码

<!-- original:step.5.code chars:461 -->
```python
leader='Damon Pond Beach (DCR)'
x=cf[cf['Beach Name'].eq(leader)]
print(x.groupby(['Year','Violation']).size().unstack(fill_value=0).to_string())
print(x[['Community','Beach Name','Beach Type Description','Organism']].drop_duplicates().to_string(index=False))
print('overall',x.viol.sum(),len(x),x.viol.mean())
# check same-name across communities for candidate/all leaders
print(cf.groupby('Beach Name').Community.nunique().sort_values(ascending=False).head())
```
<!-- /original:step.5.code -->

#### 模型实际看到的执行反馈

<!-- original:step.5.feedback chars:488 -->
```text
Violation  NO  No  YES  Yes
Year                       
2020        0   6    0   13
2021        5   0   15    0
2022        0  14    0    4
2023        0   5    0   10
Community             Beach Name Beach Type Description    Organism
    Ashby Damon Pond Beach (DCR)                  Fresh Enterococci
overall 42 72 0.5833333333333334
Beach Name
Crystal Lake        3
Long Pond           2
Flax Pond           2
Great Pond          2
Plymouth Estates    1
Name: Community, dtype: int64
```
<!-- /original:step.5.feedback -->

#### files_read 原字段

<!-- original:step.5.files_read chars:2 -->
```json
[]
```
<!-- /original:step.5.files_read -->

### 第 6 步（模型 call=6；执行 step=6）

#### 模型可读输出

`content=null`。

可读 reasoning 原文（`reasoning`）：

<!-- original:step.6.reasoning.1 chars:442 -->
```text
**Calculating annual rates**

I'm noting that the violation rates have normalized for 2020/21. I have annual rates: 13/19, 15/20, 4/18, and 10/15, giving an average of about 0.580775, which is around 58.08%. The pooled average is 58.33%. I need to clarify how I calculated the average annual rate, especially since they might expect a specific answer for a beach. I'll make sure to include the answer string with the rate in the final output.
```
<!-- /original:step.6.reasoning.1 -->

有加密 reasoning，2580 字符

同一步中逐字相同的 reasoning / reasoning_details 文本只保留一份。

#### 执行的代码

<!-- original:step.6.code chars:93 -->
```python
final_answer('Damon Pond Beach (DCR) — average annual exceedance rate of 58.1% (2020–2023).')
```
<!-- /original:step.6.code -->

#### 模型实际看到的执行反馈

消息历史中未发现对应的 role=tool 反馈；没有后续请求记录可证明模型看到的反馈原文。不放入本地完整输出。

#### files_read 原字段

<!-- original:step.6.files_read chars:2 -->
```json
[]
```
<!-- /original:step.6.files_read -->

## 6. 机械统计

- 步数：6（模型回复次数；其中 6 步有执行代码，0 步没有执行代码）。
- 读过的文件清单：12 个不同原始路径字符串；只对 execution.files_read 去重，不归一化路径，不推断未记录的访问。

<!-- original:file.1 chars:31 -->
```text
data/carson_beach_datasheet.csv
```
<!-- /original:file.1 -->

<!-- original:file.2 chars:35 -->
```text
data/city_point_beach_datasheet.csv
```
<!-- /original:file.2 -->

<!-- original:file.3 chars:37 -->
```text
data/constitution_beach_datasheet.csv
```
<!-- /original:file.3 -->

<!-- original:file.4 chars:33 -->
```text
data/m_street_beach_datasheet.csv
```
<!-- /original:file.4 -->

<!-- original:file.5 chars:31 -->
```text
data/malibu_beach_datasheet.csv
```
<!-- /original:file.5 -->

<!-- original:file.6 chars:55 -->
```text
data/pleasure_bay_and_castle_island_beach_datasheet.csv
```
<!-- /original:file.6 -->

<!-- original:file.7 chars:31 -->
```text
data/tenean_beach_datasheet.csv
```
<!-- /original:file.7 -->

<!-- original:file.8 chars:32 -->
```text
data/water-body-testing-2020.csv
```
<!-- /original:file.8 -->

<!-- original:file.9 chars:32 -->
```text
data/water-body-testing-2021.csv
```
<!-- /original:file.9 -->

<!-- original:file.10 chars:32 -->
```text
data/water-body-testing-2022.csv
```
<!-- /original:file.10 -->

<!-- original:file.11 chars:32 -->
```text
data/water-body-testing-2023.csv
```
<!-- /original:file.11 -->

<!-- original:file.12 chars:34 -->
```text
data/wollaston_beach_datasheet.csv
```
<!-- /original:file.12 -->

