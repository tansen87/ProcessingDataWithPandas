# Processing Data With Pandas

> It contains data filter, data merge, data pivot, data split...

#### main window

![image](https://github.com/tansen87/ProcessingDataWithPandas/assets/98570790/0e0534ef-5c20-454a-af01-c9a48f245aa5)

#### Usage

1. `pip install -r requirements.txt`
2. `pip install pycrab`[pycrab](https://github.com/tansen87/pycrab/releases/tag/v0.1.1)
3. `python main.py`

#### Intro

* Data Filter
  * single filter
    1. open file => select csv or excel file
    2. Enter the fields => input column name
    3. condition =>  select conditions
    4. save path => select file save path
    5. filter data => running
  * multi filter (similar to above)
  * single filter > 10GB (similar to above)
* Data Merge
  * Excel merge
    1. choose folder => select a folder with Excel
    2. save path => select file save path
    3. merge excel => running
  * csv merge (similar to above)
  * csv merge > 10GB (similar to above)
* Data Pivot
  * group sum
    1. open file => select csv file
    2. Enter index column
    3. Enter values column
    4. save path => select file save path
    5. pivot => running
* Data Split
  * csv2xlsx
    1. open file => select csv file
    2. Enter the number of split rows
    3. save path => select file save path
    4. csv2xlsx => running
* JET
  * ...
    1. open csv => select csv file
    2. open yaml => select yaml file
    3. save path => select file save path
    4. start => running

##### Thanks

+ This project is based on [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)
