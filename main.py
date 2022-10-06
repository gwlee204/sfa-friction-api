import os
from fastapi import FastAPI, File, UploadFile
from status import status
from friction_analyzer import FrictionAnalyzer


app = FastAPI()
app.title = 'COSMAX Friction api'


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data/')
UPLOAD_DIR = os.path.join(DATA_DIR, 'upload/')


@app.get("/")
async def main():
    try:
        if len(os.listdir(UPLOAD_DIR)) == 0:
            return status(1000)
        ret = {'files': os.listdir(UPLOAD_DIR)}
        return status(200, ret)
    except:
        return status(1001)


@app.post("/upload/")
async def create_upload_file(file: UploadFile = File()):
    try:
        data = await file.read()
    except:
        return status(2000)
    
    if file.filename in os.listdir(UPLOAD_DIR):
        return status(2001)

    if file.filename[-4:] != '.csv':
        return status(2002)
        
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_location, "wb+") as file_object:
            file_object.write(data)
        return status(200)
    except:
        return status(2003)


@app.get("/{file_name}/early-traces")
async def early_trace(file_name):
    if file_name in os.listdir(UPLOAD_DIR):
        try:
            friction_analyzer = FrictionAnalyzer(file_name)
            return status(200, friction_analyzer.friction_trace(0, 10, 1))
        except:
            return status(3001)
    else:
        return status(3000)

@app.get("/{file_name}/long-traces")
async def long_trace(file_name):
    if file_name in os.listdir(UPLOAD_DIR):
        try:
            friction_analyzer = FrictionAnalyzer(file_name)
            return status(200, friction_analyzer.friction_trace(10, 100, 10))
        except:
            return status(3002)
    else:
        return status(3000)

@app.get("/{file_name}/forces")
async def forces(file_name):
    if file_name in os.listdir(UPLOAD_DIR):
        try:
            friction_analyzer = FrictionAnalyzer(file_name)
            return status(200, friction_analyzer.forces())
        except:
            return status(3003)
    else:
        return status(3000)

@app.get("/{file_name}/friction-coefficient")
async def file_result(file_name: str):
    if file_name in os.listdir(UPLOAD_DIR):
        try:
            friction_analyzer = FrictionAnalyzer(file_name)
            return status(200, friction_analyzer.friction_coefficient())
        except:
            return status(3004)
    else:
        return status(3000)

@app.get("/{file_name}/hysteresis")
async def file_result(file_name: str):
    if file_name in os.listdir(UPLOAD_DIR):
        try:
            friction_analyzer = FrictionAnalyzer(file_name)
            return status(200, friction_analyzer.friction_hysteresis())
        except:
            return status(3005)
    else:
        return status(3000)


if __name__ == "__main__":
    import uvicorn

    # 데이터 디렉토리들이 있는지 확인한 이후 없으면 생성.
    if 'data' not in os.listdir(BASE_DIR):
        os.mkdir(DATA_DIR)
    if 'upload' not in os.listdir(DATA_DIR):
        os.mkdir(UPLOAD_DIR)

    uvicorn.run("main:app", host="0.0.0.0", port=42154, reload=True, access_log=True)
