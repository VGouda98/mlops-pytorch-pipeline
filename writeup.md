LINKS

Repository link
https://github.com/VGouda98/mlops-pytorch-pipeline

PR with screenshots
https://github.com/VGouda98/mlops-pytorch-pipeline/pull/2

---

CHALLENGING PART

The following were the most challenging parts for me:
1. docker & training, resouces not enough
2. kubernetes deployemnt

---

The docker with WSL doesn't seem to blend along in this integrations attempt. The image was not being pulled and built correctly, everytime i got the image not pulled error in the beginning. When the training started, the container crashed resulting in empty on docker ps. Then the logs say OOM for this. There was issues with the images that were created but didn't show under READY or COMPLETED for a long time. I had to do a fresh start with all the containers pruned, for this image to get built and further pulled correclty for the training.

Due to torch and torchvision mentioned in the requirements for both train and serve, the build time was 40+ minutes for each. And the image size was not showing, later with some research I could get to know that the size will be somewhere close to 12GB which would not be supported here. Then the torch and torchvision dependencies were removed and the image size settled to less than 2GB.

The training time for 10 epochs is roughly 7 hrs on the CPU. The training was terminated multiple times after 2-4 hours without resulting in anyting. Finally, I was able to train the model 3 times in total, getting a good bunch of predictions. In all the 3 trains, early stopping was not done, full 10 epochs were being run.

---

The setting asked for in Part E was not ideal for my laptop, it keeps getting slower and when i try to deploy and the node is shown to be crashed a few second ago everytime when check the logs. The checkpoints were somehow getting corrupted in the process and i had to start all over again. For a good amount of time, i was not able to see any ports getting up, it showed failed, and later it fails intermittently while running the service. This resulted in server could not be reached some time during testing the model with the test image.

---


