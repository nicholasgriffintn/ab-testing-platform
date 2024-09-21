from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import json

from ab_testing_platform.pipeline import run_experiment
from ab_testing_platform.lib.utils import parse_group_buckets

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_html():
    with open(os.path.join("static", "index.html")) as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/run-test/")
async def run_ab_test_api(file: UploadFile = File(...), test_type: str = Form(...)):
    data = await file.read()
    try:
        user_data = json.loads(data)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON data"}

    # TODO: Bring group buckets into the form
    group_buckets = parse_group_buckets("control:0-50,test1:50-100")
    # TODO: Allow the user to specify alpha, prior_successes, and prior_trials
    test_result = run_experiment(user_data=user_data, group_buckets=group_buckets, method=test_type)
    
    return {"result": test_result}