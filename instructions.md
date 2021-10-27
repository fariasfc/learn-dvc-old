# Install DVC:
`conda install dvc`
`conda install -c conda-forge dvc-s3`

# Create a repo and clone it!
`cd` into the cloned folder

# Initialize DVC
`dvc init`

it will create a few internal files

```
(molclr-cpu) ➜  learn-dvc git:(main) ✗ git status
On branch main
Your branch is up to date with 'origin/main'.

Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	new file:   .dvc/.gitignore
	new file:   .dvc/config
	new file:   .dvc/plots/confusion.json
	new file:   .dvc/plots/confusion_normalized.json
	new file:   .dvc/plots/linear.json
	new file:   .dvc/plots/scatter.json
	new file:   .dvc/plots/simple.json
	new file:   .dvc/plots/smooth.json
	new file:   .dvcignore
```

`git commit -m "Initialize DVC"

# Components
## Data and model versioning
- Regular GIT workflow to store large files (datasets/models) in the repo
  - but with data being stored automatically outside GIT

## Data and model access
- Easily download a specific version of data and/or ML model

## Data pipelines
- How models and data artifacts are built
- Efficient way to reproduce
- Like makefiles for data and ML projects

## Metrics, parameters, and plots
- Can be attached to pipelines
- Capture, navitgate and evaluate ML projects without leaving GIT

## Experiments
- Enable exploration, iteration, and comparison across many ML experiments
- Track experiments with automatic versioning and checkpoint logging
- Compare differences in parameters, metrics, code, and data
- Apply, drop, roll back, resume, or share any experiment


# Data and Model Versioning
`dvc add data/iris.csv`
- Adds `data/iris.csv`to the .gitignore in `data` folder
- Creates `dat/iris.csv.dvc` containing the md5, size and path of the file
- Moved the data to the project's `.dvc/cache` and linked it
- Placeholder for the original file, versioned like source code in GIT
  - `git add data/iris.csv.dvc data/.gitignore`
  - `git commit -m "Add raw data"`

# Storing and sharing
- Configuring the real storage
  - `dvc remote add -d storage s3://entosdvc/dvcstore`
  - `git add .dvc/config`
  - `git commit -m "Configure remote storage"`
- Sending the data
  - `dvc push`
  - Now we are able to `dvc pull` (after a `git clone`/`git pull`)
    - `rm -rf .dvc/cache`
    - `rm -rf data/iris.csv`
	- `dvc pull`

# Storing changes
- Duplicate the data
- `dvc status`
- `dvc add data/iris.csv`
- `git add data/iris.csv.dvc`
- `git commit -m "Dataset update"
- `git push`
- `dvc push`

# Switching between versions
- Hisory of iris placeholder
  - `git log -p data/iris.csv.dvc`
- Loading the previous version of the data
  - `git checkout HEAD~1 data/iris.csv.dvc`
  - `dvc checkout`

----------

# Accessing files
- `dvc get`
	- We can download data even outside of a git/dvc directory.
	- `cd /tmp && dvc get https://github.com/fariasfc/learn-dvc data/iris.csv && wc -l /tmp/iris.csv`
	- If some error occurs (404), it is probably the case that the dataset were not `dvc push`ed into the S3 bucket.
	- If working inside another DVC project, `dvc import` is preferred since it will keep track of versions.
- `dvc import`
  - Similar to `dvc get` + `dvc add`, but the resulting `.dvc` including metadata to track changes in the source repo. You can use `dvc update` later.
  - `dvc import https://github.com/fariasfc/learn-dvc data/iris.csv -o data/iris2.csv
- Python API
```
import dvc.api
with dvc.api.open(
    'get-started/data.xml',
    repo='https://github.com/iterative/dataset-registry'
) as fd:
    # fd is a file descriptor which can be processed normally
```

Until now, we haven't upoloaded the dataset itself, we need to perform a git push


# Pipelines
We will create a simple 3 stages pipeline:
1. split_data: Split the data into train and test sets.
2. featurize_data: Apply a Standard Scaler
3. train_model: Create and train model then save it.
4. evaluate_model: Evaluate the saved model.

## Creating the split stage
```
dvc run --name split \
	--params split.seed,split.test_percentage \
	--deps src/data/split_data.py \
	--deps data/iris.csv \
	--outs data/splits \
	python src/data/split_data.py data/iris.csv data/splits
```
- It will generate a `dvc.yaml` file to reproduce with a single `dvc repro`.
- Another file called `dvc.lock` is also generated with the md5 of the dependencies and outputs of the stage.

## Creating the featurize stage
```
dvc run --name featurize \
	--params featurize.seed \
	--deps src/data/featurize_data.py \
	--deps data/splits \
	--outs data/features \
	python src/data/featurize_data.py data/splits data/features
```
- It updates both `dvc.yaml` with the new stage information and `dvc.lock` with metadata to track changes on dependencies/outputs.

## Creating the train_model stage
```
dvc run --name train_model \
	--params model.seed,model.n_estimators \
	--deps src/models/train_model.py \
	--deps data/features \
	--outs model/rf.pkl \
	python src/models/train_model.py data/features model
```


## Creating the evaluate_model stage
```
dvc run --name evaluate_model \
	--params model.seed,model.n_estimators \
	--deps src/models/train_model.py \
	--deps data/features \
	--outs model/rf.pkl \
	python src/models/train_model.py data/features model
```