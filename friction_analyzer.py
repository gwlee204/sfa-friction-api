import os
import pandas as pd
import numpy as np


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data/')
UPLOAD_DIR = os.path.join(DATA_DIR, 'upload/')
RESULT_DIR = os.path.join(DATA_DIR, 'results/')

CAL_LOAD = 139.3
CAL_FRIC = 15.0


class FrictionAnalyzer():
    def __init__(self, filename: str) -> None:
        filepath = os.path.join(UPLOAD_DIR, filename)

        # Create result directory
        if 'results' not in os.listdir(DATA_DIR):
            os.mkdir(RESULT_DIR)
        if filename not in os.listdir(RESULT_DIR):
            os.mkdir(os.path.join(RESULT_DIR, filename))
        self.result_dir = os.path.join(RESULT_DIR, filename)

        # Load data
        f = pd.read_csv(filepath, header=None)
        
        self.raw_time = f[0]
        self.raw_friction = np.round(f[1] * CAL_FRIC, 3)
        self.raw_load = np.round(f[2] * CAL_LOAD, 3)
        self.raw_bimorph = f[3]

        self.start_point()
        self.divide_cycle()

    def start_point(self):
        # Find start point
        max_bimorph = np.max(self.raw_bimorph[0:1000])
        max_bimorph_idx = np.where(self.raw_bimorph == max_bimorph)[0][0]

        self.start_idx = max_bimorph_idx

    def divide_cycle(self):
        # Divide cycle
        self.divided_friction = []
        self.divided_load = []
        for i in range(self.start_idx, len(self.raw_friction) - 1010, 1000):
            self.divided_friction.append(self.raw_friction[i:i + 1010].reset_index(drop=True))
            self.divided_load.append(self.raw_load[i:i + 1010].reset_index(drop=True))
        
        self.divided_data = []
        for i in range(len(self.divided_friction)):
            self.divided_data.append({
                'friction': self.divided_friction[i],
                'load': self.divided_load[i]
            })

    def load(self):
        divided_loads = self.divided_load
        
        loads = []
        for i in range(len(divided_loads)):
            max_load = np.max(np.abs(divided_loads[i]))
            min_load = np.min(np.abs(divided_loads[i]))

            load_mean = round((max_load + min_load) / 2, 2)
            loads.append(load_mean)

        self.loads = loads

        return loads
    
    def friction(self):
        divided_frictions = self.divided_friction
        cut_off_idxs = []

        for i in range(len(divided_frictions)):
            abs_slope = np.abs(np.diff(divided_frictions[i], 1))
            smoothed_abs_slope = np.convolve(abs_slope, np.ones(10) / 10, mode='same')
            mean_abs_slope = np.mean(abs_slope)

            for i in range(10, 500):
                if smoothed_abs_slope[i] > mean_abs_slope:
                    pass
                else:
                    cut_off_idxs.append(i)
                    break
        
        frictions = []
        for i in range(len(divided_frictions)):
            first_friction_mean = np.mean(np.abs(divided_frictions)[i][cut_off_idxs[i]:500])
            second_friction_mean = np.mean(np.abs(divided_frictions)[i][500 + cut_off_idxs[i]:1000])

            friction_mean = round((first_friction_mean + second_friction_mean) / 2, 2)
            frictions.append(friction_mean)

        self.frictions = frictions

        return frictions

    def friction_coefficient(self):
        self.load()
        self.friction()

        ret_val = []
        for cycle_num in range(0, min(len(self.divided_load), len(self.divided_friction))):
            ret_val.append({
                'cycle': cycle_num,
                'friction-coefficient': round(self.frictions[cycle_num] / self.loads[cycle_num], 4)
            })
        return ret_val

    def forces(self):
        return_list = []
        csv_data = []
        for cycle_num in range(0, self.num_cycle):
            return_list.append({'cycle': cycle_num, 'friction-force': round(self.frictions[cycle_num], 4), 'load-force': round(self.loads[cycle_num], 4)})
            csv_data.append([round(self.frictions[cycle_num], 4), round(self.loads[cycle_num], 4)])
        
        if 'forces.csv' in os.listdir(self.result_dir):
            os.remove(os.path.join(self.result_dir, 'forces.csv'))
        df = pd.DataFrame(csv_data)
        df.to_csv(os.path.join(self.result_dir, 'forces.csv'))

        return return_list
    
    def friction_hysteresis(self):
        divided_frictions = self.divided_friction
        cut_off_idxs = []

        for i in range(len(divided_frictions)):
            abs_slope = np.abs(np.diff(divided_frictions[i], 1))
            smoothed_abs_slope = np.convolve(abs_slope, np.ones(10) / 10, mode='same')
            mean_abs_slope = np.mean(abs_slope)

            for i in range(10, 500):
                if smoothed_abs_slope[i] > mean_abs_slope:
                    pass
                else:
                    cut_off_idxs.append(i)
                    break
        
        friction_hysteresis = []
        for i in range(len(divided_frictions)):
            min_gap = np.min(np.abs(divided_frictions)[i][cut_off_idxs[i]:500]) + np.min(np.abs(divided_frictions)[i][cut_off_idxs[i]:500])
            max_gap = np.max(np.abs(divided_frictions)[i][cut_off_idxs[i]:500]) + np.max(np.abs(divided_frictions)[i][cut_off_idxs[i]:500])

            friction_hysteresis.append(round((max_gap - min_gap) / max_gap, 4))

        return friction_hysteresis