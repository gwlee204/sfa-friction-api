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
    # return list of files in upload directory
    try:
        if len(os.listdir(UPLOAD_DIR)) == 0:
            return status(1000)
        ret = {'files': os.listdir(UPLOAD_DIR)}
        return status(200, ret)
    except:
        return status(1001)


@app.post("/upload/")
async def create_upload_file(file: UploadFile = File()):
    # upload file to upload directory
    try:
        data = await file.read()
    except:
        return status(2000) # Upload 에러, 업로드된 파일의 데이터를 읽을 수 없음
    
    if file.filename in os.listdir(UPLOAD_DIR):
        return status(2001) # Upload 에러, 이미 존재하는 파일 이름

    if file.filename[-4:] != '.csv':
        return status(2002) # Upload 에러, csv 파일이 아님
        
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_location, "wb+") as file_object:
            file_object.write(data)
        return status(200)  # Upload 성공
    except:
        return status(2003) # Upload 에러, 파일 저장 실패
    

@app.get("/{file_name}/cycle/{cycle_idx}")
async def cycle(file_name, cycle_idx):
    if file_name in os.listdir(UPLOAD_DIR):
        try:
            friction_analyzer = FrictionAnalyzer(file_name)
            return status(200, friction_analyzer.divided_data[int(cycle_idx)])
        except:
            return status(3003)
    else:
        return status(3000)


@app.get("/{file_name}/friction")
async def forces(file_name):
    if file_name in os.listdir(UPLOAD_DIR):
        try:
            friction_analyzer = FrictionAnalyzer(file_name)
            return status(200, friction_analyzer.friction())
        except:
            return status(3003)
    else:
        return status(3000)
    

@app.get("/{file_name}/load")
async def forces(file_name):
    if file_name in os.listdir(UPLOAD_DIR):
        try:
            friction_analyzer = FrictionAnalyzer(file_name)
            return status(200, friction_analyzer.load())
        except:
            return status(3003)
    else:
        return status(3000)


@app.get("/{file_name}/friction-coefficient")
async def friction_coefficient(file_name: str):
    if file_name in os.listdir(UPLOAD_DIR):
        try:
            friction_analyzer = FrictionAnalyzer(file_name)
            return status(200, friction_analyzer.friction_coefficient())
        except:
            return status(3004)
    else:
        return status(3000)


@app.get("/{file_name}/hysteresis")
async def hysteresis(file_name: str):
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
