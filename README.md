# DevSecOps CI/CD Pipeline for a Containerized Flask App on AWS

A small Python (Flask) web app that is built, tested, security-scanned, containerized and deployed to AWS **automatically** on every `git push`. The infrastructure itself is created with **Terraform**, and the app is monitored with **Prometheus + Grafana**.

The goal of this project is to practice the full DevOps flow end to end: code -> test -> security scan -> container image -> cloud deployment -> monitoring.

## Architecture

```
Developer --git push--> GitHub
                          |
                  GitHub Actions pipeline
        +-----------------+------------------------------+
        | 1. test         pytest unit tests              |
        | 2. security     build image + OWASP ZAP scan   |
        | 3. build-push   Docker image -> Docker Hub     |
        | 4. deploy       SSH to EC2, pull & run image   |
        +-----------------+------------------------------+
                          |
                          v
   AWS EC2 (created by Terraform) running the Docker container
                          |
                   /metrics endpoint
                          v
                 Prometheus --> Grafana dashboards
```

## Tech stack

| Area | Tool |
|---|---|
| Application | Python 3.12, Flask, Gunicorn |
| Containers | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Infrastructure as Code | Terraform (AWS provider) |
| Cloud | AWS EC2, Security Groups |
| Security scanning | OWASP ZAP baseline scan |
| Monitoring | Prometheus, Grafana, `prometheus-client` |
| Testing | pytest |

## Repository structure

```
.
├── app/                      Flask application + requirements
├── tests/                    pytest unit tests
├── Dockerfile                Container image (non-root user, healthcheck)
├── docker-compose.yml        App + Prometheus + Grafana for local monitoring
├── monitoring/prometheus.yml Prometheus scrape config
├── terraform/                EC2 + Security Group (Infrastructure as Code)
└── .github/workflows/ci-cd.yml   The CI/CD pipeline
```

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest -v                          # run the tests
python app/app.py                  # http://127.0.0.1:5000
```

With Docker, including monitoring:

```bash
docker compose up --build
```

- App: http://localhost:5000 (try `/health`, `/api/info`, `/metrics`)
- Prometheus: http://localhost:9090 (Status -> Targets should show the app as UP)
- Grafana: http://localhost:3000 (login `admin` / `admin`; add Prometheus as a data source with URL `http://prometheus:9090`, then build a panel with the query `rate(app_requests_total[1m])`)

## Deploy to AWS

You need: an AWS account, AWS CLI configured (`aws configure`), Terraform installed, and an existing EC2 key pair.

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # edit key_name and my_ip_cidr
terraform init
terraform plan
terraform apply
```

Terraform prints the `public_ip` and `app_url`. Docker is installed on the instance automatically on first boot.

**To avoid charges, destroy everything when you are done:**

```bash
terraform destroy
```

Also set an AWS Budget alert in the billing console.

## Configure the pipeline (GitHub Secrets)

In your repo go to **Settings -> Secrets and variables -> Actions** and add:

| Secret | Value |
|---|---|
| `DOCKERHUB_USERNAME` | your Docker Hub username |
| `DOCKERHUB_TOKEN` | a Docker Hub access token (not your password) |
| `EC2_HOST` | public IP from `terraform output` |
| `EC2_SSH_KEY` | full contents of your EC2 `.pem` private key |

Push to `main` and watch the **Actions** tab. The ZAP report is saved as a downloadable artifact on each run.

## Security practices used

- Container runs as a **non-root user**
- Security headers set on every response (CSP, X-Frame-Options, nosniff)
- SSH on the EC2 instance is **restricted to my IP only**
- Encrypted EBS root volume
- Secrets stored in GitHub Secrets, `.pem` and `.tfvars` files are git-ignored
- Automated **OWASP ZAP** scan before every deployment (shift-left security)

## Results (fill this in after you run it)

Add screenshots to a `docs/` folder and link them here:

- [ ] Green GitHub Actions run
- [ ] ZAP report
- [ ] App running on the EC2 public IP
- [ ] Grafana dashboard

## Possible improvements

- Deploy to Kubernetes (minikube / EKS) instead of a single EC2 instance
- Add a Trivy image vulnerability scan stage
- Remote Terraform state in S3 with locking
- Add a load balancer and HTTPS

## What I learned

(Write 3-4 lines in your own words: what broke, how you debugged it, what you would do differently.)
