import os
import pandas as pd


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
