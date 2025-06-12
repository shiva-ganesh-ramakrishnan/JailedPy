# JailedPy

**JailedPy** is a lightweight server that provides an isolated environment to run and test Python code. It offers two deployment modes:

- A **sandboxed version using `nsjail`** for stronger isolation (requires elevated container privileges).
- A **Cloud Run-compatible version without `nsjail`**, for environments where privileged containers are not supported.

---

## Deployments

### 1.Cloud Run Deployment (Without `nsjail`)

Since `nsjail` requires elevated capabilities not available in Google Cloud Run, a simplified version of the server is deployed **without `nsjail`**:

**Service URL**:  
[https://jailedpy-676421710753.us-west1.run.app](https://jailedpy-676421710753.us-west1.run.app)

#### Dockerfile

You can run this version locally using simple port mapping:

```bash
docker build -t jailedpy .
docker run -p 8080:8080 jailedpy
```



### 2. Privileged Mode (With nsjail)
This version wraps code execution using nsjail for a jailed environment.
To enable this, subprocess.run() in modified_app.py has been updated to invoke nsjail.

#### Building and Running
```bash

docker build -f Modified_Dockerfile -t flask-app-nsjail .
docker run --rm -it \
  --cap-add=SYS_ADMIN \
  --cap-add=SYS_CHROOT \
  --security-opt seccomp=unconfined \
  --security-opt apparmor=unconfined \
  -p 8080:8080 flask-app-nsjail
```

**Note: These elevated privileges are necessary due to nsjail's reliance on chroot, mount namespaces, and user isolation.**


#### Example curl:

```
curl --location 'https://jailedpy-676421710753.us-west1.run.app/execute' \
--header 'Content-Type: application/json' \
--data '{
  "script": "import pandas as pd\nimport numpy as np\ndef main():\n    data = {'\''col1'\'': [1, 2], '\''col2'\'': [3, 4]}\n    df = pd.DataFrame(data)\n    result = df.describe().to_dict()\n    print('\''Returned stdout'\'')\n    return result"
}'
```

Example response:

```json
{
    "result": {
        "col1": {
            "25%": 1.25,
            "50%": 1.5,
            "75%": 1.75,
            "count": 2.0,
            "max": 2.0,
            "mean": 1.5,
            "min": 1.0,
            "std": 0.7071067811865476
        },
        "col2": {
            "25%": 3.25,
            "50%": 3.5,
            "75%": 3.75,
            "count": 2.0,
            "max": 4.0,
            "mean": 3.5,
            "min": 3.0,
            "std": 0.7071067811865476
        }
    },
    "stdout": "Returned stdout"
}
```