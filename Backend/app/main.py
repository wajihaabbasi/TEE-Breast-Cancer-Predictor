from app.model import predict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
	title = "Breast Cancer Prediction"
	)

class TumorFeatures(BaseModel):
	
    radius_mean: float
    texture_mean: float
    perimeter_mean: float
    area_mean: float
    smoothness_mean: float
    compactness_mean: float
    concavity_mean: float
    concave_points_mean: float = Field(alias="concave points_mean")
    symmetry_mean: float
    fractal_dimension_mean: float

    radius_se: float
    texture_se: float
    perimeter_se: float
    area_se: float
    smoothness_se: float
    compactness_se: float
    concavity_se: float
    concave_points_se: float = Field(alias="concave points_se")
    symmetry_se: float
    fractal_dimension_se: float

    radius_worst: float
    texture_worst: float
    perimeter_worst: float
    area_worst: float
    smoothness_worst: float
    compactness_worst: float
    concavity_worst: float
    concave_points_worst: float = Field(alias="concave points_worst")
    symmetry_worst: float
    fractal_dimension_worst: float
	
class Config: 
	populate_by_name  = True

@app.get("/")
def root():
	return{"message" : "Breast Cancer Prediction API is running. Visit \\docs to test."}

@app.get("/health")
def health():
	return{"status" : "ok"}

@app.post("/predict")
def make_prediction(features : TumorFeatures):
	try:
		input_dict = features.model_dump(by_alias = True)
		result = predict(input_dict)
		return result
	except ValueError as e:
		raise HTTPException(status_code = 400, detail = str (e))
