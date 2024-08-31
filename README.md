# Wordle Website

### Information
    Note: Wordle is a copyrighted game owned by The New York Times Company. This project was created for educational purposes only, and I have no intention of distributing or monetizing the website.

    Disclaimer: This project is not affiliated with or endorsed by The New York Times Company.

    Enhancements: This project includes additional utility over the original Wordle by incorporating backend functionality and creating API hooks for bots or agents to play the game. I am also exploring multiplayer functionality to further extend the website’s capabilities.

## To Run

1. Navigate to the project directory:
    ```bash
    cd C:\Users\leebe\Desktop\Wordle_Website
    ```

2. Activate the virtual environment by running the activation script, located in the Scripts folder within your virtual environment directory:
    ```bash
    wordle-env\Scripts\activate
    ```

3. Run the main Flask application module:
    ```bash
    flask run --debugger --reload
    ```


## Build Requirements
To update the list of required packages/libraries for the project, make sure the virtual environment is active, then run:
```bash
pip freeze > requirements.txt
```

## Database Migration
Updating the database when models are altered, while not breaking existing data.
Allows for movement forwards and backwards in time between different versions.

This command creates a script where the upgrade and downgrade methods can be filled out:
```bash
flask db revision
```
However, you can also use this command:
```bash
flask db migrate
```
What do we use? 'migrate' compares the updated Model classes with the current state of the database, so it sometimes doesn't work. That is when we use 'revision'.
```bash
flask db upgrade
* applies that scripts to the database to bring it up to date.
flask db downgrade
*  rolls the changes back.
```
