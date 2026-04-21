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

The following will deploy the app to a `dev` environment.

```bash
./scripts/deploy.sh dev
```

**Dev** ✅ Deployment complete! https://drrvcr35hhd5x.cloudfront.net

## Tear down services in AWS

```bash
./scripts/destroy.sh dev
```