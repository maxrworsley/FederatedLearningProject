import numpy as np
import pandas as pd
import os


class DataWrapper:
    location = ""
    """Wraps methods for getting and sorting the local data"""
    def __init__(self, data_path):
        self.data_path = data_path

    def get_data(self):
        column_names = ['day', 'max_temp', 'min_temp', 'precipitation_amount', 'target']

        only_files = [os.path.join(self.data_path, file)
                      for file in os.listdir(self.data_path)
                      if os.path.isfile(os.path.join(self.data_path, file))]

        self.location = only_files[0].split("/")[-1].split("_")[0]
        file_path = os.path.join(self.data_path, only_files[0].split("/")[-1])

        raw_dataset = pd.read_csv(file_path, names=column_names,
                                  na_values='#REF!', comment='\t',
                                  sep=',', skipinitialspace=True)
        normalized_df = (raw_dataset - raw_dataset.min()) / (raw_dataset.max() - raw_dataset.min())

        matched_dataset = self.match_records_to_predictions(normalized_df.to_numpy())
        column_names = ['1max_temp', '1min_temp', '1precip',
                        '2max_temp', '2min_temp', '2precip',
                        '3max_temp', '3min_temp', '3precip', 'target']

        dataset = pd.DataFrame(matched_dataset, columns=column_names)
        dataset = dataset.astype(float)

        return dataset.dropna()

    @staticmethod
    def match_records_to_predictions(dataset):
        # Sort records into 3 days of data to one prediction
        lines = dataset.tolist()
        processed_lines = []
        length = len(lines)

        for idx, line in enumerate(lines):
            if idx > length - 4:
                break

            new_record = [lines[idx][1], lines[idx][2], lines[idx][3],
                          lines[idx + 1][1], lines[idx + 1][2], lines[idx + 1][3],
                          lines[idx + 2][1], lines[idx + 2][2], lines[idx + 2][3],
                          lines[idx][4]]

            processed_lines.append(new_record)

        return np.array(processed_lines)
