from .. import index
from flask import abort, redirect, render_template, request, url_for
from flask_login import login_required
from ...decorators import permission_required
from ...models import Permissions
from ...services import CommentService


@index.route("/moderate/comments")
@permission_required(Permissions.MODERATE)
def moderate_comments():
    page = request.args.get("page", 1, type=int)
    pagination, comments = CommentService.get_comments(page)
    return render_template(
        "moderate-comments.html", pagination=pagination, comments=comments
    )


@index.route("/moderate/comments/enable/<int:id>")
@permission_required(Permissions.MODERATE)
def enable_comment(id):
    comment = CommentService.get(id=id)
    if not comment:
        abort(404)
    CommentService(comment).enable_comment()
    return redirect(url_for(".moderate_comments"))


@index.route("/moderate/comments/disable/<int:id>")
@permission_required(Permissions.MODERATE)
def disable_comment(id):
    comment = CommentService.get(id=id)
    if not comment:
        abort(404)
    CommentService(comment).disable_comment()
    return redirect(url_for(".moderate_comments"))
