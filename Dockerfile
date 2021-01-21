# syntax=docker/dockerfile:experimental
ARG BASE_IMAGE=continuumio/miniconda3:4.8.2

# # 1. Create COMPILE image

FROM $BASE_IMAGE AS compile-image

# Install compilers for certain pip requirements.
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install conda environments. Minification inspired by [1].
# [1] https://jcrist.github.io/conda-docker-tips.html
COPY environment.*.yml ./
RUN --mount=type=ssh pip install conda-merge && \
    conda-merge environment.run.yml environment.dev.yml > environment.yml && \
    conda install mamba --channel conda-forge --yes && \
    mamba update --yes --name base conda && \
    mamba env create --file environment.yml && \
    mamba env create --file environment.run.yml && \
    conda clean --yes --all --force-pkgs-dirs --quiet && \
    cd /opt/conda/envs/accessibility-check-backend-run-env/lib/python*/site-packages && du --max-depth=3 --threshold=5M -h | sort -h && cd - && \
    find /opt/conda/ -follow -type d -name '__pycache__' -exec rm -rf {} + && \
    find /opt/conda/ -follow -type d -name 'examples' -exec rm -rf {} + && \
    find /opt/conda/ -follow -type d -name 'tests' -exec rm -rf {} + && \
    find /opt/conda/ -follow -type f -name '*.a' -delete && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete && \
    find /opt/conda/ -follow -type f -name '*.pyc' -delete && \
    find /opt/conda/ -follow -type f -name '*.pyo' -delete && \
    cd /opt/conda/envs/accessibility-check-backend-run-env/lib/python*/site-packages && du --max-depth=3 --threshold=5M -h | sort -h && cd -

# # 2. Create application image

FROM $BASE_IMAGE AS app-image

# Copy the conda environment from the compile-image.
COPY --from=compile-image /root/.conda/ /root/.conda/
COPY --from=compile-image /opt/conda/ /opt/conda/

# Automatically activate conda environment when opening a bash shell with `/bin/bash`.
WORKDIR /app/src/
ENV PYTHONPATH /app/src/:$PYTHONPATH
ENV PATH /opt/conda/envs/accessibility-check-backend-run-env/bin:$PATH
RUN echo "source activate accessibility-check-backend-run-env" >> ~/.bashrc

# Create Docker entrypoint.
RUN printf '#!/usr/bin/env bash\n\
    \n\
    set -e\n\
    \n\
    function run_dev {\n\
    echo "Running Development Server on 0.0.0.0:8000"\n\
    uvicorn "accessibility_check_backend.api:app" --reload --log-level debug --host 0.0.0.0\n\
    }\n\
    \n\
    function run_serve {\n\
    echo "Running Production Server on 0.0.0.0:8000"\n\
    gunicorn --bind 0.0.0.0 --workers=2 --timeout 120 --graceful-timeout 120 --keep-alive 10 --worker-tmp-dir /dev/shm --access-logfile - --log-file - -k uvicorn.workers.UvicornWorker "accessibility_check_backend.api:app"\n\
    }\n\
    \n\
    case "$1" in\n\
    dev)\n\
    run_dev\n\
    ;;\n\
    serve)\n\
    run_serve\n\
    ;;\n\
    bash)\n\
    /bin/bash "${@:2}"\n\
    ;;\n\
    esac\n\
    ' > /usr/local/bin/entrypoint.sh && chmod ugo+x /usr/local/bin/entrypoint.sh

# Configure application.
ARG PORT=8000
EXPOSE $PORT
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["serve"]

# Install Chrome (and some dependencies)
RUN apt-get -y update && \
    apt-get install -y unzip wget gnupg2 && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get -y update && \
    apt-get install -y google-chrome-stable

# Download the latest Chrome Driver and put it in /usr/local/bin
RUN CHROME_VERSION=$(wget -q -O - http://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Add source code to the `WORKDIR`.
COPY src .

# Environment variables `SOURCE_COMMIT` and `SOURCE_BRANCH` are set by build systems [1].
# [1] https://docs.docker.com/docker-hub/builds/advanced/
ARG ENVIRONMENT
ENV ENVIRONMENT $ENVIRONMENT
ARG SOURCE_BRANCH
ENV SOURCE_BRANCH $SOURCE_BRANCH
ARG SOURCE_COMMIT
ENV SOURCE_COMMIT $SOURCE_COMMIT
ARG SOURCE_TIMESTAMP
ENV SOURCE_TIMESTAMP $SOURCE_TIMESTAMP
