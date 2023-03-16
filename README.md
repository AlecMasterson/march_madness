# march_madness

## Setup

### GMail API
https://developers.google.com/gmail/api/quickstart/python

```shell
docker run --name march_madness --rm -itd --mount type=bind,source="$(pwd)",target=/scripts --mount type=bind,source="//c/Users/Alec/AppData/Local/Google/Chrome/User Data",target=/chrome-data march_madness
```
