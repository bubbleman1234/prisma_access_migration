# prisma_access_migration

## Prerequisites
- Python >= 3.9.13
- Libraries listed in `requirements.txt`

## Installation
1. Clone or Download the repository
2. Open PowerShell on Windows and cd to the directory.
3. Create file name `.env` in the directory and fill the information with the format below.
    `PRISMA_CLIENT_ID=<User Access Prisma Access Tenant>`
    `PRISMA_SECRET_KEY=<Secre Key>`
    `PRISMA_TSG_ID=<Tenant ID>`
3. Create a virtual environment (venv) with the following command.
    `python -m venv venv`
4. Activate the virtual environment
    `.\.venv\Scripts\Activate.ps1`
5. Installing Required Libraries
    Once you have activated the virtual environment, install the required libraries by running:
        `pip install -r requirements.txt`

## Usage
1. After activating the virtual environment, navigate to the project directory containing main.py.
2. Run the script using Python.
    `python main.py`