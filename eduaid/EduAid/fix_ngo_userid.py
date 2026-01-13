from app import app, db, NGO, User

with app.app_context():
    db.create_all()  # Creates all missing tables


def fix_ngo_user_ids():
    with app.app_context():  # ✅ This gives you the context
        for ngo in NGO.query.all():
            user = User.query.filter_by(email=ngo.email).first()
            if user:
                ngo.user_id = user.id
        db.session.commit()
        print("NGO user_ids fixed!")

if __name__ == "__main__":
    fix_ngo_user_ids()
