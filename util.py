import os
import pandas as pd
import numpy as np


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data/')
UPLOAD_DIR = os.path.join(DATA_DIR, 'upload/')


class FrictionAnalyzer():
    def __init__(self, filename: str) -> None:
        filepath = os.path.join(UPLOAD_DIR, filename)
        f = pd.read_csv(filepath, index_col=0, header=None)
        
        self.raw_friction = f[1]
        self.raw_load = f[2]
        self.raw_bimorph = f[3]

    def wave_divide(self):
        cycle_time_sec = 20
        data_interval = 20

        cycle_time_datapoints = int(1000 / data_interval * cycle_time_sec)

        for idx in range(0, len(self.raw_bimorph)):
            if self.raw_bimorph.iloc[idx] > np.mean(np.abs(self.raw_bimorph)):
                test_list = self.raw_bimorph.iloc[idx:idx+cycle_time_datapoints]
                start_idx = np.where(test_list == np.max(test_list))[0][0]
                break
        self.wave_division = [i for i in range(start_idx, len(self.raw_bimorph), cycle_time_datapoints)]
