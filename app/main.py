from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import (
    ServerError,
    UserExistError,
    UserNotFoundError,
    UsersNotFoundError,
    UserNotSignedUpError,
    PasswordError,
    PostNotFoundError,
    PostsNotFoundError,
    create_exception_handler,
    InvalidImageUrlError
)
from app.routers.v1.users import user_router_v1
from app.routers.v1.posts import post_router_v1

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.DESCRIPTION,
    version=settings.API_VERSION_1,
)

app.include_router(user_router_v1, prefix=settings.API_VERSION_1_PREFIX, tags=["Users"])
app.include_router(post_router_v1, prefix=settings.API_VERSION_1_PREFIX, tags=["Posts"])


@app.exception_handler(500)
async def internal_server_error(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error_code": "Server error", "message": "Oops! Something went wrong"},
    )


app.add_exception_handler(
    exc_class_or_status_code=ServerError,
    handler=create_exception_handler(
        status_code=500,
        initial_detail={
            "error_code": "Server error",
            "message": "Oops! Something went wrong",
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=InvalidImageUrlError,
    handler=create_exception_handler(
        status_code=400,
        initial_detail={
            "error_code": "Inavlid URL",
            "message": "No Image exist with the provided image url for the post",
             "resolution": """Check that the provided url maatches with the post""",
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=PasswordError,
    handler=create_exception_handler(
        status_code=400,
        initial_detail={
            "error_code": "Invalid password",
            "message": "Check the provided password to confirm its validity",
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=UserExistError,
    handler=create_exception_handler(
        status_code=400,
        initial_detail={
            "error_code": "User Exist",
            "message": "User provided an existing email",
            "resolution": """Check the provided email to confirm if does not exist already""",
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=UsersNotFoundError,
    handler=create_exception_handler(
        status_code=404,
        initial_detail={
            "error_code": "Users not found",
            "message": "No users at the moment. Check back later!",
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=UserNotFoundError,
    handler=create_exception_handler(
        status_code=404,
        initial_detail={
            "error_code": "User not found",
            "message": "User not found with the provided id",
            "resolution": "Confirm that the sent id matches the user id",
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=UserNotSignedUpError,
    handler=create_exception_handler(
        status_code=404,
        initial_detail={
            "error_code": "User not signed up",
            "message": "User account does not exist",
            "resolution": "User should create an account before creating a post",
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=PostsNotFoundError,
    handler=create_exception_handler(
        status_code=404,
        initial_detail={
            "error_code": "Posts not found",
            "message": "No posts at the moment. Check back later!",
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=PostNotFoundError,
    handler=create_exception_handler(
        status_code=404,
        initial_detail={
            "error_code": "Post not found",
            "message": "post not found with the provided id",
            "resolution": "Confirm that the provided id matches the post's id",
        },
    ),
)
