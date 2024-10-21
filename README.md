# Django Expenses Project

This Django-based web application allows users to manage and split daily expenses among friends or groups.

## Project Structure

```
expenses_project/
├── .env
├── expenses/
│   ├── __pycache__/
│   ├── migrations/
│   ├── templates/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   └── views.py
├── expenses_project/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── .gitignore
├── db.sqlite3
├── manage.py
└── requirements.txt
```

## Setup and Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd expenses_project
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a new migration for database setup:
   ```
   python manage.py makemigrations
   ```

5. Apply the migration:
   ```
   python manage.py migrate
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Open your browser and navigate to `http://127.0.0.1:8000/` to view the application.

## Usage

### User Management
- Create a new user by providing email, name, and mobile number.
- Retrieve user details using the appropriate API endpoint.

### Expense Management
Users can add expenses and split them using three different methods:

1. **Equal Split**: 
   - The expense is divided equally among all participants.
   - Example: For a bill of 3000 split among 4 friends, each owes 750.

2. **Exact Split**: 
   - Specify the exact amount each participant owes.
   - Example: For a total expense of 4299, you might split it as:
     - Friend 1: 799
     - Friend 2: 2000
     - You: 1500

3. **Percentage Split**: 
   - Specify the percentage each participant owes (must add up to 100%).
   - Example: For an expense split among 4 people:
     - You: 50%
     - Friend 1: 25%
     - Friend 2: 25%

### Adding an Expense
To add an expense, use the appropriate API endpoint and provide:
- Total amount
- Split method (equal, exact, or percentage)
- Participants
- Split details (if using exact or percentage methods)

### Viewing Expenses
- Retrieve individual user expenses
- View overall expenses for all users

### Balance Sheet
- Access the balance sheet showing individual and overall expenses
- Download the balance sheet for record-keeping

## API Endpoints

### User Endpoints
- `POST /users/`: Create a new user
- `GET users/{user_id}/details`: Retrieve user details

### Expense Endpoints
- `POST /expenses/`: Add a new expense
- `GET /expenses/user/{user_id}/`: Retrieve individual user expenses
- `GET /expenses/user/{user_id}/`: Retrieve overall expenses of a user
- `GET /expenses/{expense_id}/balance_sheet/`: Download balance sheet of a particular expense
- `GET /balances/download/`: Download balance sheet of all the users combined

## Data Validation
- The application validates user inputs for all operations
- For percentage splits, the system ensures that the total percentages add up to 100%

## Running Tests

To run the tests for this project:

```
python manage.py test expenses
```


