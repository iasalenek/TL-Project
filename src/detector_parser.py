import json
import os
import numpy as np
import pandas as pd
from pathlib import Path
import datetime as dt

FOLDER_JSON = 'data/raw'
FOLDER_OUTPUT = 'data/processed/program_1'
START_DATE_TIME = pd.to_datetime('2022-03-01 00:00:00')
END_DATE_TIME =  pd.to_datetime('2022-03-1 23:55:00')
START_TIME = dt.time(0, 0)
END_TIME = dt.time(5, 30)
WEEKDAYS = None
DELTA = 5  # дельта в минутах

DetID_to_DevIDs = {
    '41039':  (['150540'], [2, 3]),  # 55.70808, 37.76822 -- O
    '10330':  (['8005'], [2, 3]),  # 55.703583, 37.766309 -- I
    '14171':  (['3752'], None),  # 55.704492, 37.771681 -- O
    '101126': (['400667'], None),  # 55.706101, 37.759448 -- I
    '101122': (['430653', '400654'], [2, 3, 4]),  # 55.704071, 37.776756 -- I
    '15385':  (['6539'], [2]),  # 55.708185, 37.764589 -- I
    #  April detectors
    '15186':  (['6596'], None),  # 55.701428, 37.763234 -- O
    '15059':  (['6588', '6589'], [2, 3, 4]),  # 55.706743 37.756483 -- O
    '9568':  (['4048'], None)  # 55.703664, 37.776202 -- O
}


def json_to_dataframe(DetID, start_time, end_time, weekdays):

    # Получаем DevIDs, соответствующие входному DetID
    DevIDs = DetID_to_DevIDs[DetID][0]

    # Делаем колоку с датами
    df_final = pd.DataFrame(
        pd.date_range(START_DATE_TIME, END_DATE_TIME,
                      freq=f'{DELTA}T'), columns=['Time'])

    # Фильтры по часам  и дням недели
    if start_time is not None:
        df_final = df_final[df_final['Time'].dt.time > start_time]
    if end_time is not None:
        df_final = df_final[df_final['Time'].dt.time < end_time]
    if weekdays is not None:
        df_final = df_final[df_final['Time'].dt.weekday.isin(weekdays)]

    for DevID in DevIDs:
        # Загружаем json в датасет и сортируем по датам
        with open(f'{FOLDER_JSON}/data_{DevID}.json', 'r') as json_data:
            data = json.load(json_data)[0]
            df = pd.DataFrame(data)
            df['Time'] = pd.to_datetime(df['Time'])
            df = df.sort_values('Time', ignore_index=True)

            # Костыль для апрельских данных
            if df['Time'][0].month != START_DATE_TIME.month:
                # Разница в ближайшее целое число недель
                week_diff = round(
                    (df['Time'][0] - START_DATE_TIME).days / 7)
                df['Time'] -= dt.timedelta(weeks=week_diff)

            # Добавляем столбы для каждой полосы
            for lane_num in np.unique(df['Number']):
                lane_df = df[
                    df['Number'] == lane_num][
                        ["Time", "Volume", "Speed"]]
                lane_df['Volume'] = lane_df['Volume'] * DELTA // 60
                lane_df = lane_df.rename(
                    {'Speed': f'vPKW{lane_num}',
                     'Volume': f'qPKW{lane_num}'}, axis='columns')
                df_final = pd.merge(df_final, lane_df, on='Time', how='left')

    # Считаем процент пропусков для детектора
    p_missing = (df_final.drop('Time', axis=1).isna().sum().sum() /
                 df_final.drop('Time', axis=1).size) * 100
    print(f'Пропусков детектора {DetID}: {"{:2.2f}".format(p_missing)}%')

    # Заполняем NA предыдущими значениями
    df_final = df_final.fillna(method='ffill')

    return df_final


def set_delta_time(time_column):
    delta_time = np.zeros(len(time_column))
    delta_time[time_column != time_column.shift()] = DELTA
    delta_time[0] = 0
    delta_time = np.cumsum(delta_time)
    return delta_time


def get_flow_file(Det_ID, det_df, lanes: None):
    long_df = pd.wide_to_long(
        det_df, stubnames=["vPKW", "qPKW"], j='Lane', i='Time').reset_index()
    if lanes is not None:
        long_df = long_df[long_df['Lane'].isin(lanes)]
    long_df['Detector'] = Det_ID + '_' + long_df['Lane'].map(str)
    long_df = long_df.drop('Lane', axis='columns')
    long_df = long_df.sort_values('Time')
    long_df['Time'] = set_delta_time(long_df['Time'])
    return long_df


class detector():
    def __init__(self, DetID,
                 start_time=None, end_time=None,
                 weekdays=None):
        self.DetID = DetID
        self.lanes = DetID_to_DevIDs[DetID][1]
        self.start_time = start_time
        self.end_time = end_time
        self.weekdays = weekdays
        self.df = json_to_dataframe(
            DetID, start_time, end_time, weekdays)

    def save_flow_file(self, path):
        flow_df = get_flow_file(self.DetID, self.df, self.lanes)
        flow_df.to_csv(f'{path}/{self.DetID}.csv', index=False, sep=';')


if __name__ == "__main__":
    detecors = [detector(DetID, START_TIME, END_TIME, WEEKDAYS)
                for DetID in DetID_to_DevIDs.keys()]
    for det in detecors:
        det.save_flow_file(FOLDER_OUTPUT)

    # Список flow файлов для flowrouter
    print(" ".join([str(Path(FOLDER_OUTPUT, x))
                    for x in os.listdir(FOLDER_OUTPUT)]))
