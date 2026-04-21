# Digital Twin

Taken from AI in production course [here](https://github.com/ed-donner/production/blob/main/week2/day4.md#day-4-infrastructure-as-code-with-terraform).

## Local Testing

### Backend

In a terminal run:

```bash
cd backend
uv sync
uv run uvicorn server:app --reload --port 8000
```

Check the API health endpoint [here](http://localhost:8000/health).


### Frontend

In a terminal run:

```bash
cd frontend
npm i
npm run dev
```

Then open the application on localhost [here](http://localhost:3000).

## Build and deploy to AWS

NOTE: If you push to `main` branch then it will trigger the deploy Github Action which deployes to `dev` environment by default: [.github/workflows/deploy.yml](.github/workflows/deploy.yml)

Alternatively, the following script (the same script that is run in the Github Action) will also deploy the app to a `dev` environment.

```bash
./scripts/deploy.sh dev
```

**Dev**  ✅ Deployment complete! https://drrvcr35hhd5x.cloudfront.net
**Prod** ✅ Deployment complete! https://d3h2dpeuy9vy75.cloudfront.net

## Tear down services in AWS

```bash
./scripts/destroy.sh dev
```