from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def check():
   return {"is_it_working": True}
