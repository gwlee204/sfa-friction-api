import os
from fastapi import FastAPI
from status import status


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


if __name__ == "__main__":
    import uvicorn

    # 데이터 디렉토리들이 있는지 확인한 이후 없으면 생성.
    if 'data' not in os.listdir(BASE_DIR):
        os.mkdir(DATA_DIR)
    if 'upload' not in os.listdir(DATA_DIR):
        os.mkdir(UPLOAD_DIR)

    uvicorn.run("main:app", host="0.0.0.0", port=42154, reload=True, access_log=True)
