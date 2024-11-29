# march_madness

## Setup

### GMail API
https://developers.google.com/gmail/api/quickstart/python

```shell
docker build . --tag march_madness_selenium
docker run --env-file .env --name march_madness_selenium --rm -itd --mount type=bind,source="$(pwd)",target=/scripts march_madness_selenium
```

python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
