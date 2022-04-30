.. _introduction:


************
Introduction
************

You can find the documentation on the rationale, pytask, and more background at https://econ-project-templates.readthedocs.io/en/stable/.


.. _getting_started:

Getting started
===============

**This assumes you have completed the steps in the `Getting Started section of the documentation <https://econ-project-templates.readthedocs.io/en/stable/getting_started.html>`_ and **everything worked.**

The logic of the project template works by step of the analysis:

1. Original data / Data scraping
2. Data management
3. Final - The actual product
4. Visualisation and Presentation using a Dash-App
5. Research paper and online documentation

Requirements
===============

There are three files that list the requirements for this project:
- scraper_env.yml contains all requirements that are needed to use the scrapers.
- environment.yaml contains all reqquirements to build the output/product from the scraped data
- requirements.txt contains all requirements to run the DashApp alone

Example: Updating the environment from environment.yml to try out the scraper can be done by:

`conda activate stockpicking_screener`

`conda env update --file sraper_env.yml --prune`

Since the requirements for the Dash-App are also contained in the environment.yml, I recommend to use the environment.yml file if you just want to have a look at the tasks and processes involved in the building of the final product. If you want to try the scraping, go ahead but keep in mind that it will take several hours/ days to scrape all the stocks and at least hours to scrape the corresponding metrics and numbers.
