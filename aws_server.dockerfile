FROM public.ecr.aws/lambda/python:3.9-x86_64

# Install the function's dependencies using file requirements.txt
# from your project folder.

COPY DialogueCacheServer/requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
COPY DialogueCacheServer/nltk_data/ ${LAMBDA_TASK_ROOT}/nltk_data/

# Copy function code
COPY DialogueCacheServer/gptif/ ${LAMBDA_TASK_ROOT}/gptif/
COPY DialogueCacheServer/data/ ${LAMBDA_TASK_ROOT}/data/
COPY DialogueCacheServer/.env ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "gptif.dialogue_cache_server_magnum.handler" ]
