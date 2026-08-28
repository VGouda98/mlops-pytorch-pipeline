Used:

- python 3.11+, pytorch, torchvision
- docker desktop, assigment executed in WSL, VSCode
- kubectl, minikube
- assignment fully executed in local
- /!\ **DUE TO LACK OF TIME (TOO MANY ASSIGNMENT AND END-TERM DEADLINES IN THE SAME WEEK), THERE ARE MULTIPLE PRs WITHIN A SINGLE FEATURE BRANCH, EXECUTED IN LESS THAN A WEEK** /!\


===

1. All the code is done in a single feature branch and PR is raised as I commit a set of changes.
2. After creating ```develop``` branch, the ```main``` branch was gone.
3. Short write up on challenging part is also attached in git (writeup.md).

===


# PART A

Repository structured as below:

(develop)
.
├── README.md
├── build.log
├── checkpoints
│   └── classifier_v1.pt
├── configs
│   └── training_config.yaml
├── data
│   ├── cifar-10-batches-py
│   │   ├── batches.meta
│   │   ├── data_batch_1
│   │   ├── data_batch_2
│   │   ├── data_batch_3
│   │   ├── data_batch_4
│   │   ├── data_batch_5
│   │   ├── readme.html
│   │   └── test_batch
│   └── cifar-10-python.tar.gz
├── docker
│   ├── Dockerfile.serve
│   └── Dockerfile.train
├── k8s
│   ├── configmap.yaml
│   ├── hpa.yaml
│   ├── namespace.yaml
│   ├── serving-deployment.yaml
│   ├── serving-service.yaml
│   └── training-job.yaml
├── mlopstrainlog.txt
├── requirements
│   ├── serve.txt
│   └── train.txt
├── src
│   ├── dataset.py
│   ├── model.py
│   ├── serve.py
│   └── train.py
├── test_image.png
├── test_image.png:Zone.Identifier
├── tests
|   └── test_model.py
└── writeup.md



# PART B

- src/model.py written for CNN model, with reduced ResNet layers architecture for CIFAR-10 dataset
- src/dataset.py loadss CIFAR-10 data with torchvision.datasets with Transforms and DataLoader setup
- src/train.py written for training, with hypermeters taken from configs/training_config.yaml. Metrics during training are logged on console, screenshot provided and model checkpoint also logged (ss_train_27_08.png)
- output path is configurable via training_config.yaml:output.checkpoint_dir field, and supports early stopping, configurable as training_config.yaml:training.early_stopping_patience set as 3, but not reached  in this training run, as the training is limited to 10 epochs, and 10 epochs are expensive by time.
- src/serve.py is written to load the the saved model chk point, and get its health status, as healthy or 200, if the model not loaded, exception is raised
- with asynchronous file operation handling, predict is posted, that runs the model for given innput and gives out the class with its probabilities.
- fastapi is used, and it is supported by uvicorn


# PART C

- docker/Dockerfile.train is written to make the image for training, with dependencies installed
- docker/Dockerfile.serve is written to make the image for serving, with dependencies installed, port 8080 exposed, also supported healthcheck at 30s interval
- mlops-train:v1 is built with docker build (ss_build_ml-train.png) and trained with docker run (ss_train_27_08.png)
- mlops-serve:v1 is build with docker build (ss_build_ml-serve.png)
- the serving is run in one terminal and predictions captured for test_image.png in second terminal (ss_predict.png)


# PART D

- written k8s/training-job.yaml to use the training image, volume mounts and resource settings as required
- added GPU request with node selector and tolerations


# PART E

- k8s/serving-deployment.yaml is written to run 2 replicas, mount RO chk at /app/checkpoints, configures liveliness and readiness probes as given the question, sets the  resource requesets and uses rolling update strategy as asked for
- k8s/serving-service.yaml is written to create ClusterIP type service over TCP on container port 8080 exposed as port 80


# PART F

- Full workflow is verified in the section running in minikube
- all the 3 manifests applied (ss_apply_manifest.png)
- then the training is done using commands in  PART C
- after that, the serving layer is deployed and the pods are verified to be running healthy (ss_serve_deploy.png)
- port forwarding is done and in another terminal , the test image is given with prediction request and probabilites with their corresponding classes are acheived (ss_portforward_predict.png)


===

1. install the prerequisites, clone the repository
2. Apply kube manifests
```kubectl apply -f k8s/namespace.yaml```
```kubectl apply -f k8s/configmap.yaml```
```kubectl apply -f k8s/training-job.yaml```
2. build the training image and serving image
```docker build -f docker/Dockerfile.train -t mlops-train:v1 .```
```docker build -f docker/Dockerfile.serve -t mlops-serve:v1 .```
3. run the training
```docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/checkpoints:/app/checkpoints \
  -v $(pwd)/configs:/app/configs \
  -e TRAINING_CONFIG=/app/configs/training_config.yaml \
  mlops-train:v1
```
4. verify the pods running and pod health
```kubectl get pods -n ml-training```
```kubectl describe deployment model-serving -n ml-training```
5. forward port
```kubectl port-forward svc/model-serving 8080:80 -n ml-training```
6. send prediction request with an image (preferred are images of those given in CLASS_NAMES in src/serve.py for positive results, otherwise go for any random image)
```curl -X POST http://localhost:8080/predict -F "file=@test_image.png"```

===
