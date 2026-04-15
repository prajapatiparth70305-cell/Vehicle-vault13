# Vehicle Vault

Vehicle Vault is a Django-based car marketplace and purchase management application. It allows users to browse cars, compare vehicles, complete purchases, manage EMI plans, buy insurance, book test drives, and view purchase history with invoices and notifications.

---

## Project Flow

1. User Authentication
   - Signup with email and password
   - OTP-based email verification on signup
   - Login and logout
   - Forgot password and reset password flow

2. Browse and Compare Cars
   - View the home page and list of available cars
   - Search cars by name from the car listing page
   - Open detailed car pages for full specifications
   - Compare two cars side-by-side

3. Purchase Car
   - Add a car to the cart
   - View cart contents and total price
   - Complete car purchase using Razorpay
   - View payment success confirmation and generated invoice
   - Check purchase history and delete old purchases

4. EMI Management
   - Select EMI option for a car and view EMI details
   - Complete EMI payment via Razorpay
   - Track EMI history and next due EMI payments
   - View single EMI transaction history and delete entries

5. Insurance Management
   - Choose insurance plan for a purchased car
   - Pay for insurance using Razorpay
   - Receive email confirmation and success page
   - View insurance history, expiry status, and invoice
   - Download insurance invoice as PDF

6. Test Drive Booking
   - Schedule a test drive for available cars
   - Specify pickup location, date, and time
   - Receive email confirmation for the booking

7. User Dashboard
   - View counts for purchased cars, active insurance, and EMI summary
   - See unread notifications
   - Manage profile details and update personal information

---

## Key Features

- User registration with email verification
- Car browsing, search, and compare
- Cart system for car purchases
- Razorpay payment integration for car purchases, EMI, and insurance
- Purchase and insurance history tracking
- EMI payment and due date tracking
- Test drive booking with email confirmation
- Notification system for purchase and insurance events
- Invoice generation and PDF download
- Profile edit and account management

---

## Tech Stack

- Backend: Django 6.0
- Frontend: HTML, CSS, JavaScript
- Database: SQLite3 (default) / PostgreSQL-ready
- Payments: Razorpay
- Email: Django email backend
- PDF generation: ReportLab

---

## Project Structure

- `core/`  main Django app for models, views, forms, and business logic
- `templates/`  HTML templates and app-specific templates
- `static/`  CSS and static assets
- `media/`  car image uploads
- `vehiclevault/`  Django project settings and URL configuration
- `manage.py`  Django management utility
- `db.sqlite3`  local SQLite database file

---

## Installation

1. Clone the repository

```bash
git clone https://github.com/your-username/vehiclevault.git
cd vehiclevault
```

2. Create and activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Apply database migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Run the development server

```bash
python manage.py runserver
```

---

## Configuration

### Razorpay

Add your Razorpay credentials to `vehiclevault/settings.py` or your environment configuration:

```python
RAZORPAY_KEY = "your_key"
RAZORPAY_SECRET = "your_secret"
```

### Email Settings

Configure email settings in `vehiclevault/settings.py` for OTP verification and notifications.

---

## User Journey

- Register and verify email with OTP
- Login and access the dashboard
- Browse cars and view details
- Add car to cart or choose EMI/insurance
- Complete payment via Razorpay
- Track purchase history, EMI history, and insurance status
- Book a test drive and receive confirmation

---

## Important URLs

- `/core/`  main app
- `/core/signup/`  user signup
- `/core/login/`  user login
- `/core/dashboard/`  dashboard
- `/core/cars/`  car listing
- `/core/car/<id>/`  car detail
- `/core/cart/`  cart
- `/core/insurance/<car_id>/`  insurance page
- `/core/emi`  EMI page
- `/core/test-drive/`  test drive booking

---

## Contributing

Contributions are welcome! Please fork the repository, make improvements, and submit a pull request.

---

## Contact

For questions or suggestions, contact:

- Email: xxyz33301@gmail.com

---

## Author

Parth Prajapati
