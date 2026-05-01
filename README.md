# Digital Twin

Taken from AI in production course [here](https://github.com/ed-donner/production/blob/main/week2/day4.md#day-4-infrastructure-as-code-with-terraform).

## Update CV PDF

Make changes to [cv.md](./backend/data/cv.md) as desired. Then run:

```bash
uv run backend/generate_cv_pdf.py
```

## Local Testing

### Backend

In a terminal run:

```bash
cd backend
uv sync
uv run uvicorn server:app --reload
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

## Deploy to AWS using local script

The following script (the same script that is run in the Github Action - see below) will deploy the app to a `dev` and `prod` environments.

```bash
./scripts/deploy.sh dev
./scripts/deploy.sh prod
```

- **Dev**  ✅ Deployment complete! https://drrvcr35hhd5x.cloudfront.net
- **Prod** ✅ Deployment complete! https://d3h2dpeuy9vy75.cloudfront.net

## Deploy to AWS using Github Actions 

Navigate to the Github Actions page [here](https://github.com/reanblock/ai-saas-twin/actions) and select the "Deploy Digital Twin" workflow.

**NOTE**: If you push a commit to the `main` branch then it will trigger the deploy Github Action which is deployed to `dev` environment by default: [.github/workflows/deploy.yml](.github/workflows/deploy.yml).

## Destroy AWS deployment

Either use the local `./scripts/destroy.sh` script or the Github Action.