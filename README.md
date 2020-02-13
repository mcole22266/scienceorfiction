# Science or Fiction

## Description
This repository contains a Flask web app that will present the up-to-date stats of the rogues from the Science or Fiction segment of The Skeptic's Guide to the Universe podcast. In its current form, random dummy data is generated upon app initialization while development is still in progess.

## How to 
1) Create a `secrets.env` file in the root of the project (same level as `scienceorfiction.env`)
2) Define both `GMAIL_USERNAME` and `GMAIL_PASSWORD` 
3) In `scienceorfiction.env`, change FLASK_DEBUG=1 to FLASK_DEBUG=0
4) `docker-compose up --build` will run the app (first startup will take a few minutes)
5) Navigate to `localhost:5000`
6) For admins, navigate to `localhost:5000/admin`

### Contributors
- Michael Cole <mcole042891@gmail.com>: App owner and developer
