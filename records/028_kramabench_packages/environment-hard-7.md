# environment-hard-7

## 1. 题目信息

- 题号：`environment-hard-7`
- 领域：环境（`environment`）
- 难度：`hard`
- 答案类型：`numeric_exact`

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

来源：`records/027_kramabench_source/runs/20261018_hard_all_01/environment-hard-7_01/meta.json`；归档成员 `20261018_hard_all_01/environment-hard-7_01/messages.jsonl`、`steps.jsonl`；`data/kramabench/workload/environment.json` 中 `id=environment-hard-7`。

## 2. agent 收到的题面原文

来源字段：`meta.prompt_values.query`。

<!-- original:query chars:241 -->
```text
What was the difference in bacterial exceedance rates (to 2 decimal places) for marine beach samples collected in 2023 between communities with more than 50% environmental justice (EJ) populations and those with less than 25% EJ populations?
```
<!-- /original:query -->

## 3. 最终答案与标准答案

### agent 最终答案原文

<!-- original:final_answer chars:23 -->
```text
10.87 percentage points
```
<!-- /original:final_answer -->

### 标准答案原文

<!-- original:gold_answer chars:5 -->
```json
10.87
```
<!-- /original:gold_answer -->

## 4. 子任务

以下内容 agent 看不到，只供标注使用

### 子任务 1：environment-hard-7-1

问题原文：

<!-- original:subtask.1.query chars:75 -->
```text
Which file is needed to obtain information about beach sample data in 2023?
```
<!-- /original:subtask.1.query -->

标准答案原文：

<!-- original:subtask.1.answer chars:27 -->
```text
water-body-testing-2023.csv
```
<!-- /original:subtask.1.answer -->

### 子任务 2：environment-hard-7-2

问题原文：

<!-- original:subtask.2.query chars:91 -->
```text
What are the column names we need to perform joining/filtering on in the water sample data?
```
<!-- /original:subtask.2.query -->

标准答案原文：

<!-- original:subtask.2.answer chars:164 -->
```json
[
                    "Beach Name",
                    "Community",
                    "Violation",
                    "Beach Type Description"
                ]
```
<!-- /original:subtask.2.answer -->

### 子任务 3：environment-hard-7-3

问题原文：

<!-- original:subtask.3.query chars:47 -->
```text
How many 2023 samples were from Marine beaches?
```
<!-- /original:subtask.3.query -->

标准答案原文：

<!-- original:subtask.3.answer chars:4 -->
```json
8491
```
<!-- /original:subtask.3.answer -->

### 子任务 4：environment-hard-7-4

问题原文：

<!-- original:subtask.4.query chars:68 -->
```text
Which municipalities are included in the environmental justice data?
```
<!-- /original:subtask.4.query -->

标准答案原文：

<!-- original:subtask.4.answer chars:6023 -->
```json
[
                    "Acton",
                    "Acushnet",
                    "Adams",
                    "Agawam",
                    "Amesbury",
                    "Amherst",
                    "Andover",
                    "Aquinnah",
                    "Arlington",
                    "Ashland",
                    "Athol",
                    "Attleboro",
                    "Auburn",
                    "Avon",
                    "Ayer",
                    "Barnstable",
                    "Becket",
                    "Bedford",
                    "Bellingham",
                    "Belmont",
                    "Beverly",
                    "Billerica",
                    "Blackstone",
                    "Boston",
                    "Bourne",
                    "Boxborough",
                    "Braintree",
                    "Brewster",
                    "Bridgewater",
                    "Brockton",
                    "Brookfield",
                    "Brookline",
                    "Buckland",
                    "Burlington",
                    "Cambridge",
                    "Canton",
                    "Carver",
                    "Charlemont",
                    "Chatham",
                    "Chelmsford",
                    "Chelsea",
                    "Chicopee",
                    "Clinton",
                    "Concord",
                    "Dalton",
                    "Danvers",
                    "Dartmouth",
                    "Dedham",
                    "Dennis",
                    "Dracut",
                    "Dudley",
                    "Eastham",
                    "Easthampton",
                    "Everett",
                    "Fairhaven",
                    "Fall River",
                    "Falmouth",
                    "Fitchburg",
                    "Foxborough",
                    "Framingham",
                    "Gardner",
                    "Gloucester",
                    "Grafton",
                    "Great Barrington",
                    "Greenfield",
                    "Halifax",
                    "Hamilton",
                    "Hanover",
                    "Hardwick",
                    "Harvard",
                    "Harwich",
                    "Haverhill",
                    "Hawley",
                    "Hingham",
                    "Hinsdale",
                    "Holbrook",
                    "Holliston",
                    "Holyoke",
                    "Hopkinton",
                    "Hudson",
                    "Lancaster",
                    "Lawrence",
                    "Lee",
                    "Leicester",
                    "Lenox",
                    "Leominster",
                    "Lexington",
                    "Lincoln",
                    "Lowell",
                    "Ludlow",
                    "Lynn",
                    "Malden",
                    "Mansfield",
                    "Marblehead",
                    "Marion",
                    "Marlborough",
                    "Marshfield",
                    "Mashpee",
                    "Maynard",
                    "Medford",
                    "Melrose",
                    "Merrimac",
                    "Methuen",
                    "Middleborough",
                    "Milford",
                    "Millbury",
                    "Millis",
                    "Milton",
                    "Monroe",
                    "Monson",
                    "Montague",
                    "Nantucket",
                    "Natick",
                    "New Bedford",
                    "Newburyport",
                    "Newton",
                    "Norfolk",
                    "North Adams",
                    "North Andover",
                    "North Attleborough",
                    "North Brookfield",
                    "Northampton",
                    "Norwood",
                    "Oak Bluffs",
                    "Orange",
                    "Orleans",
                    "Oxford",
                    "Palmer",
                    "Peabody",
                    "Pepperell",
                    "Pittsfield",
                    "Plymouth",
                    "Provincetown",
                    "Quincy",
                    "Randolph",
                    "Reading",
                    "Revere",
                    "Rockland",
                    "Rockport",
                    "Rowe",
                    "Salem",
                    "Sandwich",
                    "Saugus",
                    "Savoy",
                    "Sharon",
                    "Sheffield",
                    "Shelburne",
                    "Shirley",
                    "Shrewsbury",
                    "Somerville",
                    "South Hadley",
                    "Southbridge",
                    "Spencer",
                    "Springfield",
                    "Stockbridge",
                    "Stoneham",
                    "Stoughton",
                    "Sunderland",
                    "Swampscott",
                    "Taunton",
                    "Tisbury",
                    "Townsend",
                    "Truro",
                    "Tyngsborough",
                    "Wakefield",
                    "Walpole",
                    "Waltham",
                    "Ware",
                    "Wareham",
                    "Warren",
                    "Watertown",
                    "Webster",
                    "Wellesley",
                    "West Brookfield",
                    "West Springfield",
                    "Westborough",
                    "Westfield",
                    "Westford",
                    "Westport",
                    "Weymouth",
                    "Williamstown",
                    "Winchendon",
                    "Winchester",
                    "Winthrop",
                    "Woburn",
                    "Worcester",
                    "Yarmouth"
                ]
```
<!-- /original:subtask.4.answer -->

### 子任务 5：environment-hard-7-5

问题原文：

<!-- original:subtask.5.query chars:119 -->
```text
How many communities have more than 50% EJ population? and less than 25% respectively? Answer in a list of two numbers.
```
<!-- /original:subtask.5.query -->

标准答案原文：

<!-- original:subtask.5.answer chars:66 -->
```json
[
                    64,
                    75
                ]
```
<!-- /original:subtask.5.answer -->

### 子任务 6：environment-hard-7-6

问题原文：

<!-- original:subtask.6.query chars:110 -->
```text
What columns are used for the join operation between the marine beach data and the environmental justice data?
```
<!-- /original:subtask.6.query -->

标准答案原文：

<!-- original:subtask.6.answer chars:87 -->
```json
[
                    "Community",
                    "Municipality"
                ]
```
<!-- /original:subtask.6.answer -->

### 子任务 7：environment-hard-7-7

问题原文：

<!-- original:subtask.7.query chars:152 -->
```text
In 2023, what are the marine exceedance rates in >= 50% EJ communities and <= 25% EJ communities respectively? Answer in a list of two fraction numbers.
```
<!-- /original:subtask.7.query -->

标准答案原文：

<!-- original:subtask.7.answer chars:98 -->
```json
[
                    0.1512360639844886,
                    0.0424886191198786
                ]
```
<!-- /original:subtask.7.answer -->

### 子任务 8：environment-hard-7-8

问题原文：

<!-- original:subtask.8.query chars:86 -->
```text
What is the final numeric difference in percentage points? Save to two decimal places.
```
<!-- /original:subtask.8.query -->

标准答案原文：

<!-- original:subtask.8.answer chars:5 -->
```text
10.87
```
<!-- /original:subtask.8.answer -->

## 5. 逐步记录

每一步对应一次模型回复；原 `call` 和执行 `step` 另列。只保存该次回复一份，不重复请求历史或 provider_response 副本。没有 tool 历史反馈时不以本地输出补写。原文字段由 HTML 标记和字符长度定位，代码围栏前的展示换行不计入原文。

### 第 1 步（模型 call=1；执行 step=1）

#### 模型可读输出

`content=null`。

可读 reasoning 原文（`reasoning`）：

<!-- original:step.1.reasoning.1 chars:503 -->
```text
**Examining bacterial exceedance rates**

I need to inspect the files and determine the bacterial exceedance rates for marine beach samples from 2023, focusing on communities and their environmental justice (EJ) thresholds. It seems like I'll be working with a dataset that has yearly testing results along with beach and community details, including exceedance rates. I should also check the EJ population file to ensure I have all the necessary information. This is pretty important, so let’s dive in!
```
<!-- /original:step.1.reasoning.1 -->

有加密 reasoning，2284 字符

同一步中逐字相同的 reasoning / reasoning_details 文本只保留一份。

#### 执行的代码

<!-- original:step.1.code chars:364 -->
```python
import os, pandas as pd
base='/home/katherine/dac/benchmarks/KramaBench/data/environment/input'
for f in ['environmental-justice-populations.csv','water-body-testing-2023.csv','carson_beach_datasheet.csv']:
 p=os.path.join(base,f); print('\n',f)
 d=pd.read_csv(p); print(d.shape); print(d.columns.tolist()); print(d.head(3).to_string(index=False)); print(d.dtypes)
```
<!-- /original:step.1.code -->

#### 模型实际看到的执行反馈

模型看到的被截断：看到 4000 字符，完整输出 4042 字符

<!-- original:step.1.feedback chars:4000 -->
```text

 environmental-justice-populations.csv
(187, 9)
['OBJECTID', 'Municipality', 'EJ criteria', 'Number of EJ block groups', 'Total number of block groups', 'Percent of EJ block groups', 'Population in EJ block groups', 'Total population', 'Percent of population in EJ BGs']
 OBJECTID Municipality EJ criteria  Number of EJ block groups  Total number of block groups  Percent of EJ block groups  Population in EJ block groups  Total population  Percent of population in EJ BGs
        1        Acton           M                          3                            16                        18.8                           5621             24021                             23.4
        2     Acushnet           I                          1                             6                        16.7                           1166             10559                             11.0
        3        Adams           I                          6                             8                        75.0                           6761              8166                             82.8
OBJECTID                             int64
Municipality                        object
EJ criteria                         object
Number of EJ block groups            int64
Total number of block groups         int64
Percent of EJ block groups         float64
Population in EJ block groups        int64
Total population                     int64
Percent of population in EJ BGs    float64
dtype: object

 water-body-testing-2023.csv
(16258, 11)
['Community Code', 'Community', 'County Code', 'County Description', 'Year', 'Sample Date', 'Beach Name', 'Beach Type Description', 'Organism', 'Indicator Level', 'Violation']
 Community Code    Community  County Code County Description  Year         Sample Date            Beach Name Beach Type Description    Organism  Indicator Level Violation
            242 Provincetown            1         Barnstable  2023 2023-07-10 00:00:00 333 Commercial Street        
... [output truncated] ...
 Provincetown            1         Barnstable  2023 2023-06-05 00:00:00 333 Commercial Street                 Marine Enterococci             10.0        No
            242 Provincetown            1         Barnstable  2023 2023-08-07 00:00:00 333 Commercial Street                 Marine Enterococci             20.0        No
Community Code              int64
Community                  object
County Code                 int64
County Description         object
Year                        int64
Sample Date                object
Beach Name                 object
Beach Type Description     object
Organism                   object
Indicator Level           float64
Violation                  object
dtype: object

 carson_beach_datasheet.csv
(1134, 8)
['Carson Beach, South Boston: Bacterial Water Quality', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7']
Carson Beach, South Boston: Bacterial Water Quality Unnamed: 1 Unnamed: 2 Unnamed: 3 Unnamed: 4   Unnamed: 5          Unnamed: 6   Unnamed: 7
                                                NaN        NaN        NaN        NaN   I Street          NaN McCormack Bathhouse          NaN
                                               Date 1-Day Rain 2-Day Rain 3-Day Rain        Tag Enterococcus                 Tag Enterococcus
                                    August 27, 2024          0          0          0        NaN           61                 NaN           41
Carson Beach, South Boston: Bacterial Water Quality    object
Unnamed: 1                                             object
Unnamed: 2                                             object
Unnamed: 3                                             object
Unnamed: 4                                             object
Unnamed: 5                                             object
Unnamed: 6                                             object
Unnamed: 7                                             object
dtype: object
```
<!-- /original:step.1.feedback -->

#### files_read 原字段

<!-- original:step.1.files_read chars:117 -->
```json
["data/carson_beach_datasheet.csv", "data/environmental-justice-populations.csv", "data/water-body-testing-2023.csv"]
```
<!-- /original:step.1.files_read -->

### 第 2 步（模型 call=2；执行 step=2）

#### 模型可读输出

`content=null`。

可读 reasoning 原文（`reasoning`）：

<!-- original:step.2.reasoning.1 chars:604 -->
```text
**Defining bacterial exceedance rates**

I'm focusing on defining the bacterial exceedance rate for potential violations in marine beach samples. One sample might represent a row for each organism, like marine enterococci indicating violations. I need to aggregate community percentages for environmental justice populations based on matching community data. It's crucial to clarify what "bacterial exceedance rates" means, particularly for samples flagged with violations for Marine Beach Type in 2023. I also want to group communities based on specific thresholds and calculate the rates of exceedance.
```
<!-- /original:step.2.reasoning.1 -->

有加密 reasoning，3456 字符

同一步中逐字相同的 reasoning / reasoning_details 文本只保留一份。

#### 执行的代码

<!-- original:step.2.code chars:479 -->
```python
d=pd.read_csv(os.path.join(base,'water-body-testing-2023.csv'))
print(d['Beach Type Description'].value_counts(dropna=False).to_string())
print('\nOrganisms\n',d.Organism.value_counts(dropna=False).to_string())
print('\nviolations\n',d.Violation.value_counts(dropna=False).to_string())
print('\ncommunity sample rows',d.Community.nunique(),d['Beach Name'].nunique())
print(d[d['Beach Type Description'].str.contains('Marine',case=False,na=False)].head(10).to_string(index=False))
```
<!-- /original:step.2.code -->

#### 模型实际看到的执行反馈

<!-- original:step.2.feedback chars:2076 -->
```text
Beach Type Description
Marine    8491
Fresh     7767

Organisms
 Organism
Enterococci    9518
E. Coli        6740

violations
 Violation
No     15145
Yes     1113

community sample rows 222 1164
 Community Code    Community  County Code County Description  Year         Sample Date            Beach Name Beach Type Description    Organism  Indicator Level Violation
            242 Provincetown            1         Barnstable  2023 2023-07-10 00:00:00 333 Commercial Street                 Marine Enterococci              5.0        No
            242 Provincetown            1         Barnstable  2023 2023-06-05 00:00:00 333 Commercial Street                 Marine Enterococci             10.0        No
            242 Provincetown            1         Barnstable  2023 2023-08-07 00:00:00 333 Commercial Street                 Marine Enterococci             20.0        No
            242 Provincetown            1         Barnstable  2023 2023-08-28 00:00:00 333 Commercial Street                 Marine Enterococci             87.0        No
            242 Provincetown            1         Barnstable  2023 2023-07-31 00:00:00 333 Commercial Street                 Marine Enterococci              5.0        No
            242 Provincetown            1         Barnstable  2023 2023-08-21 00:00:00 333 Commercial Street                 Marine Enterococci             10.0        No
            242 Provincetown            1         Barnstable  2023 2023-07-26 00:00:00 333 Commercial Street                 Marine Enterococci            178.0       Yes
            242 Provincetown            1         Barnstable  2023 2023-07-27 00:00:00 333 Commercial Street                 Marine Enterococci             10.0        No
            242 Provincetown            1         Barnstable  2023 2023-06-12 00:00:00 333 Commercial Street                 Marine Enterococci             10.0        No
            242 Provincetown            1         Barnstable  2023 2023-08-14 00:00:00 333 Commercial Street                 Marine Enterococci              5.0        No
```
<!-- /original:step.2.feedback -->

#### files_read 原字段

<!-- original:step.2.files_read chars:36 -->
```json
["data/water-body-testing-2023.csv"]
```
<!-- /original:step.2.files_read -->

### 第 3 步（模型 call=3；执行 step=3）

#### 模型可读输出

`content=null`。

无可读 reasoning 文本。

有加密 reasoning，3564 字符

#### 执行的代码

<!-- original:step.3.code chars:605 -->
```python
ej=pd.read_csv(os.path.join(base,'environmental-justice-populations.csv'))
print(ej['Percent of population in EJ BGs'].describe())
print('matched distinct community', d.Community.nunique(), 'ej',ej.Municipality.nunique())
missing=sorted(set(d.Community)-set(ej.Municipality)); print('missing',len(missing),missing[:100])
marine=d[(d['Beach Type Description']=='Marine') & (d.Year==2023)].copy()
print('marine rows',len(marine),'orgs',marine.Organism.value_counts())
print('marine community count',marine.Community.nunique())
print(marine.groupby('Organism').Violation.value_counts().unstack(fill_value=0))
```
<!-- /original:step.3.code -->

#### 模型实际看到的执行反馈

<!-- original:step.3.feedback chars:1641 -->
```text
count    187.000000
mean      42.913369
std       31.952047
min        0.700000
25%       15.600000
50%       33.000000
75%       73.000000
max      100.000000
Name: Percent of population in EJ BGs, dtype: float64
matched distinct community 222 ej 187
missing 99 ['Abington', 'Ashburnham', 'Ashby', 'Ashfield', 'Belchertown', 'Bolton', 'Boxford', 'Brimfield', 'Charlton', 'Chesterfield', 'Chilmark', 'Clarksburg', 'Cohasset', 'Conway', 'Cummington', 'Douglas', 'Dover', 'Dunstable', 'Duxbury', 'East Brookfield', 'Easton', 'Edgartown', 'Erving', 'Essex', 'Florida', 'Franklin', 'Freetown', 'Georgetown', 'Goshen', 'Gosnold', 'Groton', 'Hanson', 'Heath', 'Holden', 'Holland', 'Hubbardston', 'Hull', 'Huntington', 'Ipswich', 'Kingston', 'Lakeville', 'Lanesborough', 'Leyden', 'Littleton', 'Lunenburg', 'Manchester', 'Mattapoisett', 'Medfield', 'Mendon', 'Middleton', 'Monterey', 'Mount Washington', 'Nahant', 'New Marlborough', 'Newbury', 'Oakham', 'Otis', 'Pembroke', 'Peru', 'Plainfield', 'Richmond', 'Rochester', 'Royalston', 'Russell', 'Rutland', 'Salisbury', 'Sandisfield', 'Scituate', 'Sherborn', 'Shutesbury', 'Somerset', 'Southampton', 'Southwick', 'Sterling', 'Stow', 'Sturbridge', 'Sutton', 'Swansea', 'Templeton', 'Tolland', 'Topsfield', 'Tyringham', 'Upton', 'Uxbridge', 'Wales', 'Warwick', 'Wayland', 'Wellfleet', 'Wendell', 'Wenham', 'West Stockbridge', 'West Tisbury', 'Westminster', 'Weston', 'Westwood', 'Whately', 'Wilbraham', 'Wilmington', 'Wrentham']
marine rows 8491 orgs Organism
Enterococci    8491
Name: count, dtype: int64
marine community count 61
Violation      No  Yes
Organism              
Enterococci  7811  680
```
<!-- /original:step.3.feedback -->

#### files_read 原字段

<!-- original:step.3.files_read chars:46 -->
```json
["data/environmental-justice-populations.csv"]
```
<!-- /original:step.3.files_read -->

### 第 4 步（模型 call=4；执行 step=4）

#### 模型可读输出

`content=null`。

无可读 reasoning 文本。

有加密 reasoning，3180 字符

#### 执行的代码

<!-- original:step.4.code chars:753 -->
```python
marine=marine.merge(ej[['Municipality','Percent of population in EJ BGs']],left_on='Community',right_on='Municipality',how='left')
print('marine communities',marine.Community.nunique(),'missing comms',sorted(marine.loc[marine['Percent of population in EJ BGs'].isna(),'Community'].unique()))
print('threshold rows/communities')
for label, cond in [('high',marine['Percent of population in EJ BGs']>50),('low',marine['Percent of population in EJ BGs']<25)]:
 x=marine[cond]
 print(label,len(x),x.Community.nunique(),x.Violation.eq('Yes').sum(),x.Violation.eq('Yes').mean(), 'pct',100*x.Violation.eq('Yes').mean())
 print(x.groupby('Community').agg(n=('Violation','size'),yes=('Violation',lambda s:s.eq('Yes').sum())).sort_values('Community').to_string())
```
<!-- /original:step.4.code -->

#### 模型实际看到的执行反馈

<!-- original:step.4.feedback chars:1223 -->
```text
marine communities 61 missing comms ['Chilmark', 'Cohasset', 'Duxbury', 'Edgartown', 'Essex', 'Gosnold', 'Hull', 'Ipswich', 'Kingston', 'Manchester', 'Mattapoisett', 'Nahant', 'Newbury', 'Salisbury', 'Scituate', 'Somerset', 'Swansea', 'Wellfleet', 'West Tisbury']
threshold rows/communities
high 2063 10 312 0.1512360639844886 pct 15.12360639844886
               n  yes
Community            
Aquinnah      21    2
Boston       556   78
Braintree     13    4
Lynn         258  116
Nantucket    206   10
New Bedford  153    2
Quincy       497   59
Revere        82    8
Salem        169   27
Tisbury      108    6
low 3295 22 140 0.042488619119878605 pct 4.24886191198786
                n  yes
Community             
Bourne        185    5
Brewster      216   10
Chatham       186   11
Danvers        12    5
Dartmouth     220   15
Fairhaven     102    4
Falmouth      579   25
Harwich       231    3
Hingham        96    5
Marblehead     74    6
Marion        127    1
Marshfield     80    2
Mashpee        85    1
Newburyport    84    8
Orleans        60    1
Plymouth       67    6
Provincetown  239    5
Rockport       68    2
Sandwich       87    5
Swampscott     79    8
Westport       48    0
Yarmouth      370   12
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

无可读 reasoning 文本。

有加密 reasoning，4460 字符

#### 执行的代码

<!-- original:step.5.code chars:243 -->
```python
high=marine[marine['Percent of population in EJ BGs']>50]
low=marine[marine['Percent of population in EJ BGs']<25]
diff=round(100*(high.Violation.eq('Yes').mean()-low.Violation.eq('Yes').mean()),2)
final_answer(f'{diff:.2f} percentage points')
```
<!-- /original:step.5.code -->

#### 模型实际看到的执行反馈

消息历史中未发现对应的 role=tool 反馈；没有后续请求记录可证明模型看到的反馈原文。不放入本地完整输出。

#### files_read 原字段

<!-- original:step.5.files_read chars:2 -->
```json
[]
```
<!-- /original:step.5.files_read -->

## 6. 机械统计

- 步数：5（模型回复次数；其中 5 步有执行代码，0 步没有执行代码）。
- 读过的文件清单：3 个不同原始路径字符串；只对 execution.files_read 去重，不归一化路径，不推断未记录的访问。

<!-- original:file.1 chars:31 -->
```text
data/carson_beach_datasheet.csv
```
<!-- /original:file.1 -->

<!-- original:file.2 chars:42 -->
```text
data/environmental-justice-populations.csv
```
<!-- /original:file.2 -->

<!-- original:file.3 chars:32 -->
```text
data/water-body-testing-2023.csv
```
<!-- /original:file.3 -->

