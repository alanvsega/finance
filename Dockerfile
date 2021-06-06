FROM python:3.9

WORKDIR /app/
COPY . .

RUN pip install poetry
RUN make install

ENTRYPOINT ["poetry", "run", "python", "finance/main.py"]