import numpy as np
import pickle
import random
from pathlib import Path
import typer
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier


def train_model(data_dir: Path, output_model_dir: Path) -> None:
    # reading parameters
    params = yaml.safe_load(open("params.yaml"))["model"]
    random.seed(params["seed"])

    train_x = np.load(data_dir / "train_x.npy")
    train_y = np.load(data_dir / "train_y.npy")

    model = RandomForestClassifier(
        n_estimators=params["n_estimators"], random_state=params["seed"]
    )

    model.fit(train_x, train_y)

    output_model_dir.mkdir(exist_ok=True, parents=True)

    with open(output_model_dir / "rf.pkl", "wb") as f:
        pickle.dump(model, f)


if __name__ == "__main__":
    typer.run(train_model)
