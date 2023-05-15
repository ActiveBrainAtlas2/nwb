# CREATED: 4-MAY-2024
# LAST EDIT: 12-MAY-2023
# AUTHOR: DUANE RINEHART, MBA (drinehart@ucsd.edu)

'''METHODS/FUNCTIONS FOR PROCESSING BEHAVIOR EXPERIMENTAL MODALITY'''

import os
from pathlib import Path, PurePath
import shutil
from scipy.io import loadmat
import numpy as np
import pandas as pd
from pynwb.behavior import TimeSeries, BehavioralTimeSeries


def extract_img_series_data(mat_file):
    '''EXTRACT/COMPILE COMMENTS FOR IMAGE SERIES'''
    img_comments = ''
    titles = ['a', 'b', 'phi', 'X0', 'Y0', 'X0_in', 'Y0_in', 'long_axis', 'short_axis']

    if Path(mat_file).is_file():
        param = loadmat(mat_file)['ellipse_params'].tolist()

        for i in range(9):
            var_name = titles[i]
            var_val = str(param[0][0][i][0][0])
            img_comments += var_name + ':' + var_val + '; '
    else:
        print(f'\tCOMMENTS FOR VIDEO FILE NOT INCLUDED')
    return img_comments


def add_timeseries_data(file, video_sampling_rate_Hz, name, description):
    '''READ FILE, EXTRACT NDARRAY INFO AND CREATE NWB-COMPATIBLE OBJECT
       COMPATIBLE WITH EXCEL (.xlsx) AND MATLAB (.mat)
    '''

    file_extension = Path(file).suffix

    unit = 'NA'

    if file_extension == '.xlsx':
        if name == 'raw_sensor_data':
            nd_array_timeseries_data = pd.read_excel(file, header=None).to_numpy()
        else:
            nd_array_timeseries_data = pd.read_excel(file).to_numpy()

    elif name == 'torso_dlc':
        nd_array_timeseries_data = pd.read_csv(file, header=None).to_numpy()

    else:

        nd_array_timeseries_data = loadmat(file)['data']  # get just the ndarray part

        if nd_array_timeseries_data.shape[0] == 1:
            nd_array_timeseries_data = nd_array_timeseries_data.T

        if name == 'raw_labchart_data':
            unit = ''
            for datastart, dataend in zip(loadmat(file)['datastart'], loadmat(file)['dataend']):
                unit += "({},{}) ".format(str(int(datastart)), str(int(dataend)))


    speed_time_series = TimeSeries(
        name=name,
        data=nd_array_timeseries_data,
        rate = video_sampling_rate_Hz, #float
        description=description,
        unit=unit
    )
    behavioral_time_series = BehavioralTimeSeries(
        time_series=speed_time_series,
        name=name,
    )
    return behavioral_time_series


def add_matrix_data(file, name, description):
    '''NOT REALLY TIMESERIES, JUST A HACK TO ADD MATRIX DATA TO NWB CONTAINER'''

    file_extension = Path(file).suffix

    if file_extension == '.csv': #processing
        csv_data = pd.read_csv(file)
        data = np.array((csv_data.columns.tolist(), csv_data.iloc[0, :].values.tolist())).T
    else: #analysis (.mat)
        bools = loadmat(file)['bBoolsMat']
        data = bools

    unit = 'NA'
    container = TimeSeries(
        name=name,
        data=data,
        rate=0.0,  # float
        description=description,
        unit=unit
    )
    data = BehavioralTimeSeries(
        time_series=container,
        name=name
    )
    return data


def add_str_data(file, name):

    df = pd.read_csv(file)

    data = ','.join(df.columns) + '|'

    if name == 'notes':

        for i in range(df.shape[0]):
            row = df.iloc[i].values.tolist()
            row[1], row[2] = str(row[1]), str(row[2])
            data += ','.join(row) + ' | '

    elif name == 'stimulus_notes':

        for i in range(df.shape[0]):
            row = [str(x) for x in df.iloc[i].values.tolist()]
            data += ','.join(row) + ' | '


    return data