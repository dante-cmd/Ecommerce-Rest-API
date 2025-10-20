FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Sets the PYTHONPATH environment variable to /app.
# PYTHONPATH tells Python where to look for modules and packages. 
# Setting it to /app ensures that Python can import modules from the 
# /app directory, which is useful if your application 
# structure relies on relative imports.
ENV PYTHONPATH=/app

# Set default database driver to pymssql for Docker environment
# ENV DB_DRIVER=pymssql

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]