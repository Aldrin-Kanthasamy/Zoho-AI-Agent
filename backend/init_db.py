from backend import models
from backend import database


def init_db():
    # Create tables
    database.Base.metadata.create_all(bind=database.engine)

    db = database.SessionLocal()
    try:
        # Add a sample developer user if not exists
        existing = db.query(models.User).filter(models.User.email == 'dev1@example.com').first()
        if not existing:
            user = models.User(
                name='Dev1',
                email='dev1@example.com',
                role=models.UserRole.developer,
                skills='Full Stack,Backend',
                is_available=True,
            )
            db.add(user)
            db.commit()
            print('Created sample user dev1@example.com')
        else:
            print('Sample user already exists')
    finally:
        db.close()


if __name__ == '__main__':
    init_db()
    print('Database initialization complete')
