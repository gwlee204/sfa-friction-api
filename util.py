import os
import pandas as pd
import numpy as np
from starlette.responses import FileResponse


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data/')
UPLOAD_DIR = os.path.join(DATA_DIR, 'upload/')
RESULT_DIR = os.path.join(DATA_DIR, 'results/')

CAL_LOAD = 139.3
CAL_FRIC = 15.0


class FrictionAnalyzer():
    def __init__(self, filename: str) -> None:
        filepath = os.path.join(UPLOAD_DIR, filename)

        if filename not in os.listdir(RESULT_DIR):
            os.mkdir(os.path.join(RESULT_DIR, filename))
        self.result_dir = os.path.join(RESULT_DIR, filename)

        f = pd.read_csv(filepath, index_col=0, header=None)
        
        self.raw_friction = f[1]
        self.raw_load = f[2]
        self.raw_bimorph = f[3]

        self.wave_divide()
        self.wave_cut()

        self.load_force()
        self.friction_force()

    def wave_divide(self):
        cycle_time_sec = 20
        data_interval = 20

        cycle_time_datapoints = int(1000 / data_interval * cycle_time_sec)

        for idx in range(0, len(self.raw_bimorph)):
            if self.raw_bimorph.iloc[idx] > np.mean(np.abs(self.raw_bimorph)):
                test_list = self.raw_bimorph.iloc[idx:idx+cycle_time_datapoints]
                start_idx = idx + np.where(test_list == np.min(test_list))[0][0]
                break
        self.wave_division = [i for i in range(start_idx, len(self.raw_bimorph), cycle_time_datapoints)]
        self.num_division = min(len(self.wave_division), 101)
        self.wave_division = self.wave_division[0:self.num_division]
        self.num_cycle = len(self.wave_division) - 1

    def wave_cut(self):
        self.cuts = []
        for cycle_idx in range(0, self.num_cycle):
            start_idx = self.wave_division[cycle_idx]
            end_idx = self.wave_division[cycle_idx + 1]

            friction_list = self.raw_friction.values.tolist()
            cycle_trace = friction_list[start_idx:end_idx]
            first_cut = 0
            second_cut = 0

            for i in range(1, 500):
                if cycle_trace[i]*cycle_trace[i+1] < 0:
                    first_cut = i
                    break
            
            for i in range(500, 1000):
                if cycle_trace[i-1]*cycle_trace[i] < 0:
                    second_cut = i - 500
                    break
            self.cuts.append([first_cut, second_cut])

    def load_force(self):
        ret_val = []
        for cycle_idx in range(0, self.num_cycle):
            trace_starting_idx = self.wave_division[cycle_idx]
            trace_ending_idx = self.wave_division[cycle_idx+1]
            cycle_loads = self.raw_load.iloc[trace_starting_idx:trace_ending_idx]
            ret_val.append((max(cycle_loads) + min(cycle_loads))*CAL_LOAD/2)
        self.loads = ret_val
        return ret_val

    def friction_force(self):
        ret_val = []
        friction_list = self.raw_friction.values.tolist()
        for cycle_idx in range(0, self.num_cycle):
            cycle_frictions = friction_list[self.wave_division[cycle_idx]:self.wave_division[cycle_idx+1]]
            cut = self.cuts[cycle_idx]
            first_mean = abs(np.mean(cycle_frictions[cut[0]+cut[1]:500]))
            second_mean = abs(np.mean(cycle_frictions[500+cut[0]+cut[1]:]))
            friction_mean = (first_mean + second_mean) * CAL_FRIC / 2
            ret_val.append(friction_mean)
        self.frictions = ret_val
        return ret_val

    def friction_coefficient(self):
        ret_val = []
        for cycle_num in range(0, self.num_cycle):
            ret_val.append({
                'cycle': cycle_num,
                'friction-coefficient': round(self.frictions[cycle_num] / self.loads[cycle_num], 4)
            })
        return ret_val

    def friction_trace(self, start, end, interval = 1):
        return_value = []
        for cycle_idx in range(start, end, interval):
            trace_starting_idx = self.wave_division[cycle_idx]+int((self.cuts[cycle_idx][1] + self.cuts[cycle_idx][0]) / 2)
            trace_ending_idx = self.wave_division[cycle_idx+1]+int(self.cuts[cycle_idx][0])
            vertical_shift = self.raw_friction.iloc[trace_starting_idx]
            if start != end:
                for time_idx in range(trace_ending_idx - trace_starting_idx):
                    trace_value = round((self.raw_friction.iloc[trace_starting_idx + time_idx]-vertical_shift) * 15, 4)
                    return_value.append({'cycle': str(cycle_idx), 'time': time_idx, 'trace_value': trace_value})
            else:
                for time_idx in range(trace_ending_idx - trace_starting_idx):
                    trace_value = round((self.raw_friction.iloc[trace_starting_idx + time_idx]-vertical_shift) * 15, 4)
                    return_value.append({'time': time_idx, 'trace_value': trace_value})
        return return_value

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
        friction_list = self.raw_friction.values.tolist()
        hysteresis_value = []

        for cycle_idx in range(0, self.num_cycle):
            try:
                cycle = friction_list[self.wave_division[cycle_idx]:self.wave_division[cycle_idx+1]]
                cut = self.cuts[cycle_idx]

                first_region = [cut[0]+cut[1], 500]
                second_region = [500+cut[0]+cut[1], len(cycle)]

                hysteresis_max = max(cycle[:500]) - min(cycle[500:])
                hysteresis_min = min(cycle[first_region[0]:first_region[1]]) - max(cycle[second_region[0]:second_region[1]])

                hysteresis = hysteresis_max - hysteresis_min
                hysteresis_value.append(hysteresis * CAL_FRIC)
            except:
                if len(hysteresis_value) > 0:
                    hysteresis_value.append(hysteresis_value[-1])
                else:
                    hysteresis_value.append(0)
        
        return_list = []
        csv_data = []
        for cycle_num in range(0, self.num_cycle):
            return_list.append({'cycle': cycle_num, 'hysteresis': round(hysteresis_value[cycle_num], 4)})
            csv_data.append(round(hysteresis_value[cycle_num], 4))

        if 'friction-hysteresis.csv' in os.listdir(self.result_dir):
            os.remove(os.path.join(self.result_dir, 'friction-hysteresis.csv'))
        df = pd.DataFrame(csv_data)
        df.to_csv(os.path.join(self.result_dir, 'friction-hysteresis.csv'))

        return return_list
