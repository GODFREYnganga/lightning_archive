import pandas as pd
import os

def create_metadata_csv(data, output_path):
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)

def calculate_score(resolution, timestamp_proximity, vantage_diversity):
    # Simple scoring: higher resolution, closer timestamps, more diverse vantages
    score = (resolution / 1000) * 0.4 + (1 / (1 + timestamp_proximity)) * 0.4 + vantage_diversity * 0.2
    return score

def update_metadata_csv(new_data, csv_path):
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    else:
        df = pd.DataFrame([new_data])
    df.to_csv(csv_path, index=False)
