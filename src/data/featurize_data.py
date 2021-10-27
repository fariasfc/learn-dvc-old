import numpy as np
import random
from pathlib import Path
import typer
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import yaml


def featurize_data(splits_dir: Path, output_dir: Path) -> None:
    # reading parameters
    params = yaml.safe_load(open("params.yaml"))["featurize"]
    random.seed(params["seed"])

    # Loading data
    df_train = pd.read_csv(splits_dir / "train.csv")
    df_test = pd.read_csv(splits_dir / "train.csv")

    train_x = df_train.drop(columns=["Class"]).values
    train_y = df_train["Class"].values

    test_x = df_test.drop(columns=["Class"]).values
    test_y = df_test["Class"].values

    # Scaling features
    scaler = MinMaxScaler(feature_range=eval(params["feature_range"]))
    train_x = scaler.fit_transform(train_x)
    test_x = scaler.transform(test_x)

    output_dir.mkdir(exist_ok=True, parents=True)

    with open(output_dir / "train_x.npy", "wb") as f:
        np.save(f, train_x)

    with open(output_dir / "train_y.npy", "wb") as f:
        np.save(f, train_y)

    with open(output_dir / "test_x.npy", "wb") as f:
        np.save(f, test_x)

    with open(output_dir / "test_y.npy", "wb") as f:
        np.save(f, test_y)


if __name__ == "__main__":
    typer.run(featurize_data)
