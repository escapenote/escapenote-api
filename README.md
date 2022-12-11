# Escapenote API

## ✨ Requirements

- Python 3.8

## 📚 Technical Stacks

- FastAPI
- Swagger
- Prisma(ORM)

## 🌩 AWS Architecture

- Application Loadbalancer
- ECS
- Fargate
- Parameter Store(for env)

## 🚡 CI / CD

- Github Actions

## 📦 Install

```shell
# 가상환경 설정
$ pip install virtualenv
$ virtualenv venv
$ source venv/bin/activate

# 라이브러리 설치
$(venv) pip install -r requirements.txt
```

## 🔨 Runs

```shell
# 개발모드 실행
$ uvicorn app.main:app --reload --host=0.0.0.0
```

## ⚙️ Settings

```shell
# generate .env file from parameter store
$ aws ssm get-parameter --with-decryption --name "escapenote-api-prod-env" --query Parameter.Value | sed -e 's/^"//' -e 's/"$//' -e 's/\\n/\n/g' -e 's/\\//g' > .env
```
