
FROM node:16 AS frontend-build

WORKDIR /app/frontend

COPY ./frontend/package.json ./frontend/package-lock.json ./

RUN npm install

COPY ./frontend/ ./

RUN npm run build

FROM python:3.9-slim AS backend-build

WORKDIR /app

COPY requirements.txt .

COPY --from=frontend-build /app/frontend/build /app/frontend/build

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
