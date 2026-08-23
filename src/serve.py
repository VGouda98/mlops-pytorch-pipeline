from io import BytesIO
from pathlib import Path
import torch
import torch.nn.functional as F
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image
from torchvision import transforms

from model import get_model

app = FastAPI(title="MLOPS A3 - Image Classifier using CIFAR-10")
CLASS_NAMES = [
    "airplane",
    "automobile",
    "bird",
    "cat",
    "deer",
    "dog",
    "frog",
    "horse",
    "ship",
    "truck",
]
CHECKPOINT_PATH = Path("/app/checkpoints/classifier_v1.pt")
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

# align transformations with dataset.py
preprocess = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.4914, 0.4822, 0.4465],
        std=[0.2470, 0.2435, 0.2616],
    ),
])

model = None
is_model_loaded = False


def load_model():
    global model, is_model_loaded

    if not CHECKPOINT_PATH.exists():
        raise Exception(f"Checkpoint path not found for loading model")

    # create model as per part B, 1st point
    model = get_model(
        architecture="resnet18",
        num_classes=10,
    )
    # load model
    checkpoint = torch.load(CHECKPOINT_PATH, map_location=device)

    #load states stored at best validation loss during training
    model.load_state_dict(
        checkpoint["model_state_dict"]
    )
    model.to(device)
    model.eval()
    is_model_loaded = True


try:
    load_model()
except Exception:
    print(f"Model loading failed")


@app.get("/health")
def health():
    # check for model is loaded, if yes return healthy (200 here)
    if is_model_loaded:
        return {
            "status": "healthy",
            "is_model_loaded": True,
        }

    # raise exception because GET request to /health has failed
    raise Exception("Model is not available to get health")


# asychronous file operation handling by FastAPI
@app.post("/predict")
async def predict(file):
    # check for model loaded
    if not is_model_loaded:
        raise Exception("Model is not loaded for prediction")

    try:
        # read image file bytewise, and convert to RGB channels
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except:
        raise Exception("Invalid image file")

    # preprocess image
    input_tensor = preprocess(image)
    input_tensor = input_tensor.unsqueeze(0).to(device)

    with torch.no_grad():
        # logit outputs, and compute softmax probabilities
        outputs = model(input_tensor)
        probabilities = F.softmax(outputs, dim=1)[0]

    # predict class
    predicted_index = int(torch.argmax(probabilities).item())

    # return predictions
    return {
        "predicted_class": CLASS_NAMES[predicted_index],
        "predicted_class_index": predicted_index,
        "probabilities": {
            CLASS_NAMES[i]: 
                round(float(probabilities[i].item()), 6) for i in range(len(CLASS_NAMES))
        }
    }