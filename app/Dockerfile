FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app/

COPY ./ /app

ARG INSTALL_DEV=false
RUN pip install -r requirements.txt
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then pip install -r requirements-dev.txt ; fi"

ENV PYTHONPATH=/app