"""
Dev-only seed script — populates a fresh database with one canteen,
its menu, and one test user per role.

Idempotent: if a canteen already exists, it does nothing (won't create
duplicates or crash on unique-constraint violations if run twice).

Run from campusbites-backend/, with the venv active and .env configured:
    python -m scripts.seed
"""

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import Canteen, MenuItem, User, UserRole


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(Canteen).first() is not None:
            print("Seed data already exists — skipping. Delete rows manually to reseed.")
            return

        canteen = Canteen(name="Main Canteen", location="Block A")
        db.add(canteen)
        db.flush()  # assigns canteen.id without committing yet

        menu_items = [
            MenuItem(canteen_id=canteen.id, name="French Fries", description="Crispy golden fries with ketchup", price=30, category="snacks"),
            MenuItem(canteen_id=canteen.id, name="Veg Sandwich", description="Fresh veggies with toasted bread", price=40, category="snacks"),
            MenuItem(canteen_id=canteen.id, name="Mini Pizza", description="Cheesy mini pizza with tomato sauce", price=35, category="snacks"),
            MenuItem(canteen_id=canteen.id, name="Veg Thali", description="Rice, dal, sabzi, roti and pickle", price=80, category="meals"),
            MenuItem(canteen_id=canteen.id, name="Chicken Biryani", description="Aromatic basmati rice with chicken", price=120, category="meals"),
            MenuItem(canteen_id=canteen.id, name="Veg Noodles", description="Stir fried noodles with vegetables", price=60, category="meals"),
            MenuItem(canteen_id=canteen.id, name="Tea", description="Hot masala chai", price=10, category="drinks"),
            MenuItem(canteen_id=canteen.id, name="Cold Coffee", description="Chilled coffee with milk and ice", price=40, category="drinks"),
            MenuItem(canteen_id=canteen.id, name="Juice", description="Fresh seasonal fruit juice", price=30, category="drinks"),
        ]
        db.add_all(menu_items)

        test_users = [
            User(
                full_name="Test Student", username="student1", email="student1@campusbites.test",
                password_hash=hash_password("Student@123"), role=UserRole.student,
            ),
            User(
                full_name="Test Staff", username="staff1", email="staff1@campusbites.test",
                password_hash=hash_password("Staff@123"), role=UserRole.staff,
            ),
            User(
                full_name="Test Admin", username="admin1", email="admin1@campusbites.test",
                password_hash=hash_password("Admin@123"), role=UserRole.admin,
            ),
        ]
        db.add_all(test_users)

        db.commit()
        print(f"Seeded 1 canteen, {len(menu_items)} menu items, {len(test_users)} users.")
        print("Test logins:")
        print("  student1 / Student@123")
        print("  staff1   / Staff@123")
        print("  admin1   / Admin@123")
    finally:
        db.close()


if __name__ == "__main__":
    seed()