#!/bin/bash

uvicorn main:app --host 0.0.0.0 --port 7861 --workers ${SERVER_WORKERS:-4}
