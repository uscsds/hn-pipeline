FROM amazonlinux:2023

RUN yum -y update && yum -y install \
    python3.11 python3.11-devel gcc gcc-c++ make \
    blas-devel lapack-devel libffi-devel openssl-devel wget unzip && \
    alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    python3 --version

RUN python3 -m ensurepip && python3 -m pip install --upgrade pip setuptools wheel

WORKDIR /build

# Install spaCy into /build/python
RUN mkdir -p python && \
    python3 -m pip install --no-cache-dir -t python spacy==3.7.4

# Set PYTHONPATH so spaCy is importable
ENV PYTHONPATH=/build/python

# Download en_core_web_sm wheel directly (explicit URL)
RUN wget https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# Install the model into /build/python
RUN python3 -m pip install --no-cache-dir -t python en_core_web_sm-3.7.1-py3-none-any.whl

# ---- TRIM MODEL ----
RUN python3 -c "\
import en_core_web_sm; \
nlp = en_core_web_sm.load(); \
nlp.disable_pipes(*[pipe for pipe in nlp.pipe_names if pipe not in ['tagger','parser','ner']]); \
nlp.to_disk('/tmp/minimal_model');"

# Remove original (full-size) model and install trimmed model
RUN rm -rf python/en_core_web_sm* && \
    mkdir -p python/en_core_web_sm && \
    cp -r /tmp/minimal_model/* python/en_core_web_sm/

# Cleanup unnecessary files to minimize size
RUN find python -type d -name "tests" -exec rm -rf {} + && \
    find python -type d -name "__pycache__" -exec rm -rf {} + && \
    find python -type d -name "*.dist-info" -exec rm -rf {} + && \
    rm -rf python/*.dist-info python/*.egg-info && \
    rm -rf python/en_core_web_sm/vocab/vectors && \
    rm -rf python/en_core_web_sm/lemmatizer && \
    find python -name "*.so" -exec strip --strip-unneeded {} + || true

# Package the layer
RUN zip -r9 layer.zip python

CMD ["cat", "layer.zip"]

