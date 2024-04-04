from database.tables import GroupInvites
from flask_login import current_user


def get_amount_invites():
    return GroupInvites.query.filter_by(recipient_id=current_user.id).count()
