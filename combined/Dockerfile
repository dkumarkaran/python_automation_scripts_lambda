FROM public.ecr.aws/lambda/python:3.8
  
# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

# Run pip install
RUN pip install pandas
RUN pip install openpyxl
# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.handler" ]
