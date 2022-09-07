from fastapi import FastAPI


app = FastAPI()
app.title = 'COSMAX Friction api'


@app.get("/")
async def main():
    return {"hello": "world"}
