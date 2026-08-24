import torch.nn as nn
from torchvision.models import resnet18


def get_model(
    architecture: str = "resnet18",
    num_classes: int = 10,
) -> nn.Module:
    # as per configmap.yaml
    if architecture != "resnet18":
        raise Exception(f"{architecture} not supported")

    # train from the scratch
    model = resnet18(weights=None)

    # first convolution layer of neural network, with smaller kernel
    model.conv1 = nn.Conv2d(
        in_channels=3,
        out_channels=64,
        kernel_size=3,
        stride=1,
        padding=1,
        bias=False,
    )

    # 32x32 is too small to downsample
    model.maxpool = nn.Identity()

    # Replace ImageNet's 1000-class classifier with our dimensions
    model.fc = nn.Linear(
        model.fc.in_features,
        num_classes,
    )

    return model
