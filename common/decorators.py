from django.contrib.auth.decorators import login_required, user_passes_test

def admin_required(view_func):
    return login_required(
        user_passes_test(lambda u: u.is_superuser or u.role == "admin")(view_func)
    )
