```
 conda create -p env python=3.10 -y
```
```
conda activate env
```
```
uvicorn main:app --reload --port 8001
```