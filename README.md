# NewsFlash

NewsFlash is a web app that shows the latest headlines from major news publishers and allows users to save them to a database.



## Live App

[https://news-flash-dh4x.onrender.com/](https://news-flash-dh4x.onrender.com/)



## Repository

[https://github.com/benhannafin/newsflash](https://github.com/benhannafin/newsflash)



## Team

* Ben Hannafin (124375573)
* Finn Lennon (124408656)
* Cillian Dobbyn (124376021)
* Conan Day (124341683)

## Team Contribution

Work was divided across implementation, deployment, testing, and documentation. 
Contribution levels varied across the project, but all components were completed to deliver the project.


## What the app does

* Gets top headlines from NewsAPI
* Displays them on a webpage
* Lets you save headlines to a database (Supabase)
* Lets you view saved headlines later



## Stack used

* Python (Flask)
* NewsAPI (external API)
* Supabase (PostgreSQL database)
* Docker
* GitHub Actions (CI)
* Render (deployment)



## Endpoints

* `/` → main page
* `/headlines` → get live headlines
* `/save-headlines` → save headlines to DB
* `/saved-headlines` → get saved headlines
* `/health` → check if app is running
* `/status` → check API + DB connection

## CI/CD Overview

The project uses GitHub Actions for CI and Render for automatic deployment.  
When changes are pushed to the main branch, the application is rebuilt and redeployed.



## Running with Docker

Build:

```bash
docker build -t newsflash .
```

Run:

```bash
docker run -p 5000:5000 --env-file .env newsflash
```



## Running locally

```bash
pip install -r requirements.txt
python app.py
```

Then go to:

[http://localhost:5000](http://localhost:5000)



## Environment variables

Create a `.env` file:

```env
NEWS_API_KEY=your_api_key
DATABASE_URL=your_database_url
```
A `.env.example` file is included to show required variables.



## CI

GitHub Actions is used to:

* install dependencies
* run tests (pytest)
* run linting (flake8)
* build the Docker image

Runs on every push and pull request.



## Deployment

The app is deployed on Render using Docker.

It automatically updates when changes are pushed to the `main` branch.



## Testing the app

1. Open the live app
2. Click “Load Headlines”
3. Click “Save Headlines”
4. Click “Load Saved Headlines”

## Testing

Basic tests are included using pytest to verify key endpoints.

Run tests locally:

bash
pytest

## Notes

* Duplicate headlines are avoided using the URL as a unique field
* Basic logging and error handling are included
* The app uses environment variables for configuration
