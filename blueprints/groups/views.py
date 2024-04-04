from flask import Blueprint, render_template, redirect, flash, url_for
from flask_login import login_required, current_user
from database.tables import db, GroupMembers, Users, Lists, GroupInvites, Tasks
from forms.add_group_member import AddGroupMemberForm
from datetime import datetime
from active_invites import get_amount_invites

groups_bp = Blueprint("groups", __name__, template_folder="templates")


@groups_bp.route("/<int:list_id>/group/add_member", methods=["GET", "POST"])
@login_required
def add_group_member(list_id):
    form = AddGroupMemberForm()
    list = db.session.get(Lists, list_id)
    active_invites = get_amount_invites()

    if form.validate_on_submit():
        recipient = Users.query.filter_by(username=form.username.data).first()
        if recipient:
            if GroupMembers.query.filter_by(
                user_id=recipient.id, group_id=list.group_id
            ).first():
                flash("This user is already a member of the group!", "danger")
            elif GroupInvites.query.filter_by(
                recipient_id=recipient.id, list_id=list_id
            ).first():
                flash("This user is already has an invite to this group!", "danger")
            else:
                new_invite = GroupInvites(
                    sender_id=current_user.id,
                    recipient_id=recipient.id,
                    list_id=list_id,
                )
                db.session.add(new_invite)
                db.session.commit()

                form.username.data = ""
                flash("Invite sent successfully!", "success")
        else:
            flash("User not found!", "danger")
    return render_template(
        "add_member.html", form=form, list_id=list_id, active_invites=active_invites
    )


@groups_bp.route("/invites/<int:list_id>/accept")
@login_required
def accept_invite(list_id):
    # See if invite exists
    invite = GroupInvites.query.filter_by(
        list_id=list_id, recipient_id=current_user.id
    ).first()

    if invite:
        # join group of the list
        list = db.session.get(Lists, list_id)
        new_group_member = GroupMembers(group_id=list.group_id, user_id=current_user.id)
        db.session.add(new_group_member)
        db.session.commit()
        # remove invite
        db.session.delete(invite)
        db.session.commit()
        flash("Invite Accepted!")

    return redirect(url_for("groups.group_invites"))


@groups_bp.route("/invites/<int:list_id>/deny")
@login_required
def deny_invite(list_id):
    # See if invite exists
    invite = GroupInvites.query.filter_by(
        list_id=list_id, recipient_id=current_user.id
    ).first()

    if invite:
        # remove invite
        db.session.delete(invite)
        db.session.commit()
        flash("Invite Denied!")

    return redirect(url_for("groups.group_invites"))


@groups_bp.route("/invites")
@login_required
def group_invites():
    active_page = "invites"
    invites = GroupInvites.query.filter_by(recipient_id=current_user.id).all()
    all_lists = []
    active_invites = get_amount_invites()
    if invites:
        for invite in invites:
            list = db.session.get(Lists, invite.list_id)
            list_name = list.list_name
            list_id = list.list_id
            user = db.session.get(Users, list.list_owner_id)
            sender_name = user.full_name
            all_lists.append(
                {"list_name": list_name, "sender_name": sender_name, "list_id": list_id}
            )
    return render_template(
        "invites.html",
        active_page=active_page,
        all_lists=all_lists,
        active_invites=active_invites,
    )


@groups_bp.route("/<int:list_id>/leave")
@login_required
def leave_group(list_id):
    list = db.session.get(Lists, list_id)
    member_leaving = GroupMembers.query.filter_by(
        user_id=current_user.id, group_id=list.group_id
    ).first()
    try:
        db.session.delete(member_leaving)
        db.session.commit()
        flash("Succesfully Left Group!!")
        return redirect(url_for("lists.shared_lists"))
    except:
        flash("There was an error leaving the group, try again!!")
        return redirect(url_for("lists.view_list"))


@groups_bp.route(
    "/<int:list_id>/<int:new_owner_id>/transfer_ownership", methods=["GET", "POST"]
)
@login_required
def transfer_list_ownership(list_id, new_owner_id):
    list_to_transfer = Lists.query.get_or_404(list_id)

    # Ensure the current user is the owner of the list
    if current_user.id == list_to_transfer.list_owner_id:
        # Transfer ownership by updating the list's owner ID
        list_to_transfer.list_owner_id = new_owner_id
        db.session.commit()
        flash("Ownership of the list has been transferred successfully!")
    else:
        flash("You don't have permission to transfer ownership of this list.")

    return redirect(url_for("groups.view_list_group", list_id=list_id))


@groups_bp.route("/<int:list_id>/group/remove_member/<int:user_id>")
@login_required
def remove_member(list_id, user_id):
    list = db.session.get(Lists, list_id)
    group = GroupMembers.query.filter_by(group_id=list.group_id)
    group_members = []
    for member in group:
        user_info = db.session.get(Users, member.user_id)
        group_members.append(user_info)

    user_to_remove = GroupMembers.query.filter_by(
        user_id=user_id, group_id=list.group_id
    ).first()

    try:
        db.session.delete(user_to_remove)
        db.session.commit()
        flash("User Removed Successfully!!")
        return redirect(url_for("groups.view_list_group", list_id=list.list_id))
    except:
        flash("Error! Looks like there was a problem.... Try Again!")
        return redirect(url_for("groups.view_list_group", list_id=list.list_id))


@groups_bp.route("/<int:list_id>")
@login_required
def view_list_group(list_id):
    list = db.session.get(Lists, list_id)
    group = GroupMembers.query.filter_by(group_id=list.group_id)
    group_members = []
    for member in group:
        user_info = db.session.get(Users, member.user_id)
        group_members.append(user_info)
    active_invites = get_amount_invites()
    return render_template(
        "view_list_group.html",
        group_members=group_members,
        list_id=list_id,
        list=list,
        active_invites=active_invites,
    )
