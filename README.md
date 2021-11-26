# Introduction

Wagtail is an open source CMS that sits on top of Django, the hugely popular Python based web framework. This repository contains the Web Applications Development Service's custom wagtail installation with modifications made to fit within the University of Manchester's technical infrastructure.

This guide walks through the steps required to set up your own wagtail project locally on your development machine, using this repository as a template.

For documentation on deploying the site onto a Research Virtual Machine, consult the wider documentation that can be found [here](https://github.com/UoMResearchIT/wads-wagtail-documentation/blob/main/development-documentation/tutorial/set_up_deploy_env/set_up_deploy.md).
## Requirements
### Windows

    Windows Subsystem Linux (recommended)

    OR

    Python
    virtualenv
    Git Bash
    Command Line Interface
    Python IDE / Text editor

    NOTE: All commands that use "git" are done in Git Bash. It lets you use MinGW/Linux tools with Git at the command line. Other commands can be done in Git Bash as well but you may prefer to use a different CLI.


### Linux / WSL

    Python
    virtualenv
    Git
    Command Line Interface
    Python IDE / Text editor


NOTE - Set-up instructions for Windows Subsystem Linux can be found [here](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
If you are using a managed laptop you will need access to the BIOS settings to allow virtualization. We recommend using the Ubuntu 20.04 LTS as your distro to match the VM's that will be hosting the deployed site.

## Wagtail Setup

We will be collecting files the necessary files to run our Wagtail. All projects are based on this `wads-wagtail` repository. This is a version of wagtail that has been developed to suit the needs of the research community. Many features from previous wagtail projects have been back ported. 

Another repository called [`wagtail-apps`](https://github.com/UoMResearchIT/wagtail-apps) contains web applications that have been made generic so they can be re-used on other projects.
### 1. Cloning the Repo

We want to create a new version of `wads-wagtail` to serve as the basis of your project.

There are several way to do this. 

#### a. Manual Method

Create a new repository on GitHub. Name it `wads-<new_project_name>`

On your computer -

`git clone https://github.com/UoMResearchIT/wads-wagtail.git>`

`cd wads-wagtail`

`git remote set-url origin https://github.com/UoMResearchIT/<new_project_name>.git`

`git push origin master`

Clone your new repository to your computer and work from that.

#### b. Template Method

In the `wads-wagtail` repo on Github choose the 'Use this Template' option.

Name the new repo - `wads-<new_project_name>`

Clone your new repository to your computer and work from that.

NOTE - using the template option will mean losing the version history of the `wads-wagtail` repo.

#### c. Import Method

In the top right of Github, click the '+' next to your usename and choose 'Import Directory'.

Choose the `wads-wagtail` repo as the one you want to import.

Name the new repo - `wads-<new_project_name>`

Clone your new repository to your computer and work from that.

NOTE - there can be issues using this method due to GitHub Authentication. Choose the manual method if this is the case and you want to preserve version history.

### 2. Setting up your Development Environment

Depending on how you created your project repo you may have a few stray branches. You will need a minimum of 3.

`main` - the main branch
`deploy` - the deploy branch that will be used on the sites VM
`wads-wagtail-main` - the main branch of the `wads-wagtail` repo. Used to bring any new changes or fixes that have been made in `wads-wagtail` to your project.

If you haven't got a `deploy` branch, create it with -

`git checkout main`
`git checkout -b deploy`
`git push origin deploy`

To create the upstream `wads-wagtail-main` branch - 

`git checkout -b wads-wagtail-main`
`git fetch upstream main`
`git branch --set-upstream-to=upstream/main`

then to confirm

`git remote -v`

revert to main

`git checkout main`


Now we have all the files and branches, we need to install the necessary packages; create a database, superuser, and start a development server to make sure everything is working.

#### a. Install packages

We will be creating a virtual environment to contain all the required packages. All commands that utilise python will require the virtual environment to be activated.

##### Windows

`virtualenv <virtualenv_name>`

`<virtualenv_name>\Scripts\activate`

`pip install -r requirements.00.core.txt`

`pip install -r requirements.01.dev.txt`

NOTE - the other two requirement files aren't necessary for development and may cause issues on Windows as they require specific Linux-based packages to be installed.

##### Linux / WSL

`virtualenv <virtualenv_name>`

`source <virtualenv_name>/bin/activate`

`pip install -r requirements.00.core.txt`

`pip install -r requirements.01.dev.txt`

NOTE - the other two requirements aren't necessary for development but can be installed in a Linux environment if you wish.

#### b. Create a database

##### Windows

This will create a sqlite database that can be used for development purposes.

`cd path/to/directory/containing manage.py/file`

`python manage.py migrate`

##### Linux / WSL

Ubuntu includes PostgreSQL by default. To install PostgreSQL on Ubuntu, use the apt-get (or other apt-driving) command -

`apt-get install postgresql-12`

Then to set-up the database. Take a note of the database name and password as you will need the details later - 

- `sudo -i`
- `su - postgres`
- `psql`
- `CREATE DATABASE <database_name>;`
- `CREATE USER <database_user_name> WITH PASSWORD '<password>';`
- `ALTER ROLE <database_user_name> SET client_encoding TO 'utf8';`
- `ALTER ROLE <database_user_name> SET default_transaction_isolation TO 'read committed';`
- `ALTER ROLE <database_user_name> SET timezone TO 'UTC';`
- `GRANT ALL PRIVILEGES ON DATABASE <database_name> TO <database_user_name>;`
- `\q`
- exit
- exit

After `exit`ing twice you should now be back to your normal user account.

Then -

`cd <path/to/directory/containing manage.py/file>`

`python manage.py migrate`

NOTE - the same process will be used on the VM.

#### c. Configure local.py

We now need to configure your `local.py`. You may have noticed that it doesn't exist and is included in the `.gitignore`.

To create it, make a copy of the `template_dev_local.py` and name it `local.py`. 

Fill in the details as needed such as the site name, base url, database details etc.

For the Secret Key a good tool to use is - https://miniwebtool.com/django-secret-key-generator/

NOTE - if you are on Windows you can comment out the DATABASES setting.

#### d. Create a superuser

`python manage.py createsuperuser`

Enter details when prompted. Then - 

`python manage.py migrate`

NOTE - you can do the `createsuperuser` command above before the `migrate` command if you want to cut down on number of migration files.

#### d. run the development server

`python manage.py runserver`

Go to http://127.0.0.1:8000 and you should be greeted with the default homepage. 

You can then go to http://127.0.0.1:8000/admin to access the Wagtail CMS using the superuser username and password created earlier.

NOTE - you can run the server on `localhost` as well using - `python manage.py runserver 0.0.0.0:8080`. If it throws up an error you may need to add `0.0.0.0` to the `ALLOWED_HOSTS` in your `local.py` file.

## Next Steps
### Developing for Wagtail

Now you have a development copy of wagtail ready to start building your project.

Developing for Wagtail follows a general development pipeline - 

1. develop your app or feature on a separate branch to `main`
2. if there are changes to the database run the `makemigrations` and `migrate` commands
3. test your work in the browser
4. repeat the first 3 steps until complete

When the development work is done push it to GitHub WITHOUT the migration files. The reason for this is we want to keep the migration files on the server 
as clean as possible and not contain all the tests we have done in development.

 then -

1. create a pull request to merge into `main`
2. merge `main` into `deploy`

On a clean version of the repo separate from where you have done your development work do the `./manage.py makemigrations`

1. on the VM where the site is hosted pull your changes down with `git pull`
2. do a `./manage.py migrate` to migrate the changes to the live database
3. if you have made any changes in the `static` folder you will need to also run the `./manage.py collectstatic` command.

### How To's

For help, you can check out the various 'How To's' in the main [`wads-wagtail` documentation](https://github.com/UoMResearchIT/wads-wagtail-documentation/tree/main/development-documentation/how-to).

If there are any gaps, feel free to create a pull request. We want to make the documentation as accessible as possible.
### Deploying to a RVM

A guide for deploying to a RVM can be found in the  [`wads-wagtail` documentation](https://github.com/UoMResearchIT/wads-wagtail-documentation/blob/main/development-documentation/tutorial/set_up_deploy_env/set_up_deploy.md) as well.



