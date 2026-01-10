import os
import io
import joblib
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import Response

app = FastAPI()

API_TOKEN = os.getenv("API_TOKEN", "")
MODEL_PATH = os.getenv("MODEL_PATH", "model.joblib")

model = None

def require_bearer(request: Request):
    if not API_TOKEN:
        raise HTTPException(status_code=500, detail="API_TOKEN is not set on server")
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = auth.split(" ", 1)[1].strip()
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.on_event("startup")
def load_model():
    global model
    model = joblib.load(MODEL_PATH)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict_csv")
async def predict_csv(request: Request, file: UploadFile = File(...)):
    require_bearer(request)

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    # test_df には Target が無い前提。もし混ざってても落とす。
    if "Target" in df.columns:
        df = df.drop(columns=["Target"])

    if "id" not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain 'id' column")

    ids = df["id"].copy()
    X = df.drop(columns=["id"])

    proba = model.predict_proba(X)[:, 1]
    pred = (proba >= 0.5).astype(int)

    out = pd.DataFrame({"id": ids, "pred": pred, "proba": proba})
    csv_bytes = out.to_csv(index=False).encode("utf-8")

    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=predictions.csv"},
    )
