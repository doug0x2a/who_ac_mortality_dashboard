# WHO All Cause Mortality Dashboard

This dashboard was created using data provided by the [WHO Mortality Database](https://www.who.int/data/data-collection-tools/who-mortality-database).  When these files were processed, they were listed as being updated in February 2022.  The finished dashboard is deployed on [Heroku](https://who-all-cause-mortality.herokuapp.com/).  This repository includes the following files:

* `process_who_mortality_files.ipynb` is the Jupyter notebook used to process WHO Database files into csv files used by the dashboard.
* `who_ac_deaths_per_1000.csv`, `who_all_cause_deaths.csv`, and  `who_population.csv` are the processed csv files used by the dashboard application.  These are included in the repository for deployment to the Heroku application.
* `app.py`: the dash application used to run the dashboard.
* `runtime.txt`, `requirements.txt`, and `Procfile` are files used to to allow the the application to run on Heroku.
* `assets/favicon.ico` is the icon used on the web browser tab.
* `README.md` is this file.