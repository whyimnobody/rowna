# Vatglobal Developer Assignment

## Task

Create a Django based API using the Django REST Framework to allow a user to upload a data file for processing, and to retrieve a list of processed rows.

The application should expose the two following endpoints:

### processFile – POST

- Accepts a CSV file
- For each row, validate each of the cell values (date, country, purchase or sale, currency, net and input amounts) so that they are of the correct datatype and format.
- Store the results of each row in an appropriate data structure. Each cell value should be converted such that the data can be queried in a consistent manner. Be sure to select appropriate data types for each cell value type.
- Only rows for the year of 2020 should be stored.

### retrieveRows – GET

- Takes three query parameters
  - country (ISO 3166 code)
  - date (YYYY/MM/DD)
  - currency (optional) (ISO 4217 code)
- Returns a JSON response containing the rows based on the correct country and date. If the currency is passed in, convert the stored currency to the requested currency by fetching the required rate(s) (if available) from the European Central Bank [https://sdw-wsrest.ecb.europa.eu/help/](https://sdw-wsrest.ecb.europa.eu/help/)
- Please design this endpoint to scale as gently as possible with the bank API. Please document steps taken towards this goal in the repositories’ README file.
  Use query parameters as follows to perform a query:

```
/retrieveRows?country=DE&date=2020/08/05&currency=GBP
```

### Test data

Use the sample transactions in the test-data folder to validate your solution.

### Scalability

The test data set only includes around 1000 transactions. How would you go about scaling your solution to millions of records?

In the README file, briefly describe how you would build a scalable solution for ingesting very large data sets to ensure reliable and timely processing of the data. Please mention any limitations to your solution.

### Other considerations:

- Use Python 3.9 and Django 4 for this exercise
- Use your choice of dependency management.
- Implement unit tests and comments where appropriate.
- Provide any information needed to run locally in the README file of the repository and a .env file location if we need to run migrations etc.
- Please send us a way to view the code: GitHub, Bitbucket, etc.
- Please complete this task within a week of receiving. If you need more time, please let us know.

### First run

Setup and activate the virtualenv:

`pipenv install`

`pipenv shell`

Perform migrations:

`python manage.py migrate`

Create the cache table:

`python manage.py createcachetable`

Run the development server:

`python manage.py runserver`

### Scalable Solution

As with all things, it depends.

My go-to solution assumes the number of transactions would be out of this world crazy amounts, and that dealing with that amount of those transactions would involve DevOps and all the time and maintenance that goes with it.

I would use serverless functions to avoid having to deal with dynamic scaling of the application instance itself, and avoid pandas killing the application instance by clogging memory. Serverless functions, if written well, will also alleviate the headache of making sure ingestion happens while allowing other requests aren't blocked by workers. It also means I can worry about software instead of how expensive my EC2 instance is getting because of the memory it needs.

### Easy On The API

In order to be gentle to the ECB API, I'd use one of the many packages available for querying, such as [https://github.com/alexprengere/currencyconverter](), which will allow the caching of current and historic rates as well as allow the API to only be hit when updating rates, as required, be it once an hour, or once a day. This can be created as a scheduled task and monitored.

An alternative to this would be caching based on the most popular requests, based on time, location, user or any other variable that may group end-users. On a production system with cache, this will minimise database queries, and be speedy, for cached exchange rates.

### Things I just didn't do

- Use cookiecutter-django
  - Just thought it would be easier to do a small from-scratch project, instead of the massive cookiecutter template. I was wrong, my Django basics were old and outdated. They're now a little better.
- Stuff that's been done
  - I tried to rely on the framework and packages to do things instead of doing it myself - less to maintain and more time to make what I want instead of the bits that go into it
- Use envs for local dev
  - No containers, and no testing or production deployments means there's no immediate incentive, and having mentioned I usually use cookiecutter-django for projects, my general intention would be clear.
- Flesh out the OpenAPI docs
  - Wanted to try implementing drf-spectacular myself, and I kind of did, but not really
- Implement semver and changelog generation
  - Wouldn't have been useless with my single-massive commit
- Implement pre-commit hooks

  - Largely for automatic formatting and commit linting

- Hook up the currency exchange request for the GET request.
  - I just don't get the API well enough to hook it up and call myself a responsible adult
- Ask for more time
  - There's no need? Anything bigger would largely be more to review with less return on your impression of my work. I'm pretty sure I've written about anything important. And if I haven't, we'll be able to chat about it during the unpacking of the assessment.

### Things I wanted to do but didn't

- Try out the production settings
  - I just didn't do it, what's there is a loose collection of thoughts and ideas
- Implement better functions
  - I swapped my due dates for tech assessments in my calendar, the extra day I thought I had, I didn't. So the ones that are good enough, are good enough.
- Implement a task queue
  - cookiecutter-django comes with celery but huey is dirt simple to setup so I wanted to do that. I didn't.
- Have the project reviewed
  - Having someone else look at the project would have been awesome, but as per the previous bullet point, I had to work within the time I had.
- Spend less time
  - At some point i went into auto-pilot and started fiddling with things that had nothing to do with the endpoints, and just wasted some time reading the ECB API thing and it's packages...
  - Ended up spending about **eight hours** redoing, reading, testing and sprinkling in some actual code
- Add API key auth
  - Seems only logical since there aren't any user accounts
