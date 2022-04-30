# European Factor Stockpicking / Stockscreener
This project provides an automatization of stockscreening of international stocks and helps the individual investor to construct her/his portfolio, based on common Fama French Asset-Pricing Factors.

I decided to deploy my results as an Dash-App on Heroku. This allows users to access my results and my research without having a proper background in programming and git.
Furthermore, I plan to publish it to contribute back to the people that helped me learn to code but also to manage my own finances. Therefore, I wanted to have a shiny application rather than a folder of .csv files :) 

#### The final result can be seen here: https://stockpickingapp.herokuapp.com

The code that is used for this App is the same as you can find in this repo in the folder src/Dashboard since I cannot publish the repository that is deployed on Heroku. You can therefore also locally run the Dash-App, but you can also just check it out at https://stockpickingapp.herokuapp.com.
## Documentation and Idea
Since I was determined to deploy the project as a Dash-App, I decided to move part of it on the web. This repo just contains the [documentation](https://github.com/JonathanWillnow/european_factor_stockpicking_screener/blob/master/project_documentation.pdf) of the functions, while the motivation and idea behind this project can be found at https://stockpickingapp.herokuapp.com/documentation, but also partly in the [research paper](https://github.com/JonathanWillnow/european_factor_stockpicking_screener/blob/master/src/paper/research_paper.pdf) of this project.

## Requirements

The file *environment.yml* contains all requirements to run all functions. This includes running all the different scrapers and a local version of the Dash App.

If you want to try the scraping you should expect some problems with some paths to extensions that I used tailored to my machine for secure scraping. Also, keep in mind that it will take several hours / days to scrape all the stocks and at least hours to scrape the corresponding metrics and numbers (Took me arround 20h to scrape all NASDAQ stocks). Also, you might run into problems since some files like geckodriver need to be installed on your machine to execute all the scraping, but once you have fixed this, the scrapers are running.

*Installing all the  the requirements can be done with* `conda env create -f environment.yml`.

*Do not forget to use* `conda develop .` *before you try to run anything once the requirements are satisfied.*

*As mentioned, task_get_stockinfo will fail unless you have a firefox browser and a geckodriver.log file*

*You can run a local version of the Dash.App via* `python app.py`. 

## Usage of pytask
Throughout the project I will make use of pytask. I even used pytask for scraping and showed that it works, but I also implemented all functionality in the form of scripts as explained in the next section. For the sake of clarity, I commented out some pytasks functions that involve Web-scraping (/data_management/task_get_stockinfo.py)
### Why didnt I used pytask more?
The longterm idea for this is that the project runs continously on a seperat machine like a Raspberry PI and scrapes the stocks, for instance every weekend or every two weeks at a fixed time. Therefore, I want to use the functionality of crontab, which is a demon on unix to start processes timely. Since I did not figure out how to use crontab together with pytask, I designed the project such that I can simply call the *.py files. This might be subject to change in the future since I more and more enjoy the possibilities and functionality that pytask provides.

## Work in progress
This project is not finished and work in progress. After I started it for the course Effective Programming Practices for Economists, I became aware of all the possible extensions that I could develop and implement. As outlined in the beginning, I want to make it Open Source and find contributers after the grading for EPP is done. More possible extensions are listed https://stockpickingapp.herokuapp.com/documentation but also in the [research paper](https://github.com/JonathanWillnow/european_factor_stockpicking_screener/blob/master/src/paper/research_paper.pdf)



