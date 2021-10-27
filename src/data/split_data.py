import random
import numpy as np
from pathlib import Path
import typer
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import yaml


def prepare_splits(raw_data_path: Path, output_dir: Path) -> None:
    # reading parameters
    params = yaml.safe_load(open("params.yaml"))["split"]
    test_percentage = params["test_percentage"]
    random.seed(params["seed"])

    # Loading data
    df = pd.read_csv(raw_data_path)

    # Encoding classes
    label_encoder = LabelEncoder()
    df["Class"] = label_encoder.fit_transform(df["Class"])

    train_indices, test_indices = train_test_split(
        df["Class"],
        test_size=test_percentage,
        random_state=params["seed"],
        stratify=df["Class"],
    )

    train_indices = np.where(train_indices)
    test_indices = np.where(test_indices)

    print(train_indices)

    df_train = df.iloc[train_indices]
    print(df_train.shape)
    df_test = df.iloc[test_indices]

    output_dir.mkdir(exist_ok=True, parents=True)

    print(df_train.head())

    df_train.to_csv(output_dir / "train.csv")
    df_test.to_csv(output_dir / "test.csv")


if __name__ == "__main__":
    typer.run(prepare_splits)
