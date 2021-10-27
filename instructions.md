# Install DVC:
`conda install dvc`
`conda install -c conda-forge dvc-s3`

# Copy S3 credentials
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
`dvc add data/phoneme.csv`
- Adds `data/phoneme.csv`to the .gitignore in `data` folder
- Creates `dat/phoneme.csv.dvc` containing the md5, size and path of the file
- Moved the data to the project's `.dvc/cache` and linked it
- Placeholder for the original file, versioned like source code in GIT
  - `git add data/phoneme.csv.dvc data/.gitignore`
  - `git commit -m "Add raw data"`

# Storing and sharing
- Configuring the real storage
  - `dvc remote add -d storage s3://entosdvc/dvcstore`
  - `git add .dvc/config`
  - `git commit -m "Configure remote storage"`
- Sending the data
  - `dvc push`
  - Now we are able to `dvc pull` (after a `git clone`/`git pull`)
    - `rm -model .dvc/cache`
    - `rm -model data/phoneme.csv`
	- `dvc pull`

# Storing changes
- Duplicate the data
- `dvc status`
- `dvc add data/phoneme.csv`
- `git add data/phoneme.csv.dvc`
- `git commit -m "Dataset update"
- `git push`
- `dvc push`

# Switching between versions
- Hisory of phoneme placeholder
  - `git log -p data/phoneme.csv.dvc`
- Loading the previous version of the data
  - `git checkout HEAD~1 data/phoneme.csv.dvc`
  - `dvc checkout`

----------

# Accessing files
- `dvc get`
	- We can download data even outside of a git/dvc directory.
	- `cd /tmp && dvc get https://github.com/fariasfc/learn-dvc data/phoneme.csv && wc -l /tmp/phoneme.csv`
	- If some error occurs (404), it is probably the case that the dataset were not `dvc push`ed into the S3 bucket.
	- If working inside another DVC project, `dvc import` is preferred since it will keep track of versions.
- `dvc import`
  - Similar to `dvc get` + `dvc add`, but the resulting `.dvc` including metadata to track changes in the source repo. You can use `dvc update` later.
  - `dvc import https://github.com/fariasfc/learn-dvc data/phoneme.csv -o data/phoneme2.csv
- Python API
```
import dvc.api
with dvc.api.open(
    'get-started/data.xml',
    repo='https://github.com/iterative/dataset-registry'
) as fd:
    # fd is a file descriptor which can be processed normally
```

Until now, we haven't upoloaded the dataset itself, we need to pemodelorm a git push


# Pipelines
We will create a simple 4 stages pipeline:
1. split_data: Split the data into train and test sets.
2. featurize_data: Apply a Standard Scaler
3. train_model: Create and train model then save it.
4. evaluate_model: Evaluate the saved model.

## Creating the split stage
```
dvc run --name split \
	--params split.seed,split.test_percentage \
	--deps src/data/split_data.py \
	--deps data/phoneme.csv \
	--outs data/splits \
	python src/data/split_data.py data/phoneme.csv data/splits
```
- It will generate a `dvc.yaml` file to reproduce with a single `dvc repro`.
- Another file called `dvc.lock` is also generated with the md5 of the dependencies and outputs of the stage.

## Creating the featurize stage
```
dvc run --name featurize \
	--params featurize.feature_range \
	--deps src/data/featurize_data.py \
	--deps data/splits \
	--outs data/features \
	python src/data/featurize_data.py data/splits data/features
```
- It updates both `dvc.yaml` with the new stage information and `dvc.lock` with metadata to track changes on dependencies/outputs.

## Creating the train_model stage
```
dvc run --name train_model \
	--params model \
	--deps src/models/train_model.py \
	--deps data/features \
	--outs model/model.pkl \
	python src/models/train_model.py data/features model
```

### Try dvc repro
- `dvc repro`
  - Everything is cached
- Change featurize.feature_range and run `dvc repro` again
  - Only the featurize stage would run again.
- Change featurize.feature_range to the old value and `dvc repro` again
  - It won't run anything, since it cached the repro before.

# Show the dvc dag
`dvc dag`

## Creating the evaluate_model stage
- Metrics: scalar values
- plots: history
  - it is possible to create other templates
```
dvc run --name evaluate_model \
	--deps src/models/evaluate_model.py \
	--deps data/features \
	--deps model/model.pkl \
	--metrics-no-cache scores.json \
	--plots-no-cache roc.json \
	python src/models/evaluate_model.py data/features model/model.pkl scores.json roc.json
```

## Running dvc repro again

Now we need to commit both `roc.json` and `scores.json` so we can compare between commits.
- `dvc repro`
- `dvc plots show`
	- Open file in browser
- `dvc plots modify roc.json -x fpr -y tpr`
- `git add scores.json roc.json`
- `git commit -m "first experiment"`
- Changes hidden_layer_sizes to (100, 50)
- `dvc`repro`
- `dvc plots show`
	- Open file in browser
- `dvc metrics show --all-commits`
- `dvc plots diff HEAD~1`



- `dvc get --rev githash https://github.com/fariasfc/learn-dvc model/model.pkl`


# Experiments
- `dvc exp show`
- `dvc exp run --set-param model.hidden_layer_sizes="(40,10)"`
We can also run experiments in batches using queues
- `dvc exp run --queue --set-param model.hidden_layer_sizes="(1,2)"`
- `dvc exp run --queue --set-param model.hidden_layer_sizes="(3,4)"`
- `dvc exp run --queue --set-param model.hidden_layer_sizes="(1,2)" --set-param featurize.feature_range="(0,1)"`
- `dvc exp run --queue --set-param model.hidden_layer_sizes="(100,20)" --set-param featurize.feature_range="(0.1,0.9)"`
- `dvc exp run --queue --set-param model.hidden_layer_sizes="(3,4)"`
- `dvc exp run --run-all --jobs 2`
- `dvc exp show`

## Creating a branch from a specific experiment
- `dvc exp branch exp-41691 "(40,10)"`