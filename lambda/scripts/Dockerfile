# Use Amazon Linux 2023 base image with Python 3.11
FROM public.ecr.aws/lambda/python:3.11

# Set working directory
WORKDIR /lambda_layer

# Install system dependencies required for building Python packages
RUN yum -y update && \
    yum install -y python3 python3-devel gcc gcc-c++ make libffi-devel openssl-devel zip findutils curl && \
    yum clean all

# Install SpaCy and other dependencies into the correct directory for Lambda Layer
RUN python3 -m venv /lambda_layer/env && \
    /lambda_layer/env/bin/pip install --upgrade pip && \
    /lambda_layer/env/bin/pip install spacy==3.7.4 && \
    /lambda_layer/env/bin/python -m spacy download en_core_web_sm

# Clean unnecessary files to reduce size
RUN rm -rf /lambda_layer/env/share/doc && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/*.dist-info && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/*.egg-info && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/*.pyc && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/*.pyo && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/*tests* && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/spacy/tests && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/spacy/cli && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/spacy/compat && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/spacy/_cython_optimizations.cpython-311-x86_64-linux-gnu.so && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/spacy/schemas && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/spacy/training && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/spacy/pipeline/trainable_pipe && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/numpy/tests && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/numpy/doc && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/spacy/examples && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/spacy/demo* && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/*.libs && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/spacy/__pycache__ && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/en_core_web_sm/*tests* && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/en_core_web_sm/*docs* && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/en_core_web_sm/__pycache__ && \
    rm -rf /lambda_layer/env/lib/python3.11/site-packages/en_core_web_sm/en_core_web_sm-*.tar.gz

# Copy the necessary files for Lambda layer
RUN mkdir -p /lambda_layer/python && \
    cp -r /lambda_layer/env/lib/python3.11/site-packages/* /lambda_layer/python/ && \
    cp -r /lambda_layer/env/lib/python3.11/site-packages/en_core_web_sm /lambda_layer/python/

# Zip up the contents of the Python directory
RUN cd /lambda_layer && \
    zip -r /lambda_layer/spacy_layer.zip python/

# Final command to show that the file was created
#CMD echo "Layer zip file created successfully: /lambda_layer/spacy_layer.zip"
