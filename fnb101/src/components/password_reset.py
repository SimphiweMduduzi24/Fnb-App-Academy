import json
import os
from pathlib import Path

import flet as ft


def get_assets_dir() -> Path:
    default_assets_dir = Path(__file__).parent / "assets"   # fallback for local runs
    return Path(os.environ.get("FLET_ASSETS_DIR", str(default_assets_dir))).resolve()


def load_users():
    default_path = get_assets_dir()

    with open(f"{default_path}/data/users.json", "r") as f:
        return json.load(f)


USERS = load_users()


def update_users(user):
    # update global user
    for i, existing in enumerate(USERS["users"]):
        if existing["username"] == user["username"]:
            USERS["users"][i] = user
            break

    # update file in folder
    default_path = get_assets_dir()

    with open(f"{default_path}/data/users.json", "w") as f:
        json.dump(USERS, f, indent=2)


def check_username(username):
    for user in USERS["users"]:
        if user["username"].lower() == username.lower():
            return user
    return None


def reset_password(page: ft.Page):

    username = ft.TextField(
        label="Username",
        border_color="#0084a8",
        focused_border_color="#0084a8",
        border=ft.OutlineInputBorder(border_radius=10),
    )

    password = ft.TextField(
        hint_text="New password",
        password=True,
        helper_style=ft.TextStyle(color=ft.Colors.RED),
        border_radius=ft.BorderRadius.all(10),
    )

    confirm_password = ft.TextField(
        hint_text="Confirm password",
        password=True,
        helper_style=ft.TextStyle(color=ft.Colors.RED),
        border_radius=ft.BorderRadius.all(10),
    )

    error_message = ft.Text(
        "Username not found",
        size=15,
        weight=ft.FontWeight.BOLD,
        color="#ff0000",
        visible=False,
    )

    def on_cancel(e):
        page.pop_dialog()

    def on_save(e):
     if password.value !=confirm_password.value:
         error_message.visible=True,
         error_message.value="Passwords do not match"
         error_message.update()
         return
     else:
         error_message.visible=False
         error_message.update()
         user=page.session.store.get("user")

         #update password
         user["password"]=password.value

         #update global and database
         update_users(user)
         page.session.store.set("user", user)

         page.pop_dialog()

             
         
     

    def on_next(e):
        if not username.value:
            username.helper = "Username cannot be left empty"
            username.update()
            return
        else:
            username.helper = None
            username.update()

        # check against database
        user = check_username(username.value)

        # tell user that they are not found
        if not user:
            error_message.visible = True
            error_message.update()
            return
        else:
            error_message.visible = False
            error_message.update()

        page.session.store.set("user", user)
            

        #prepare dialogue and modal
        modal.title="update password"
        modal.content=ft.Column(
            tight=True,
            controls=[password,
                      confirm_password,
                      error_message

            ]
        )

        modal.actions=[
            ft.Button(
                content="Cancel",
                on_click=on_cancel
            ),
            ft.Button(
                content="Save",
                on_click=on_save
            )
        ]
        page.update()

    modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm username"),
        content=ft.Column(
            tight=True,
            controls=[
                username,
                error_message,
            ],
        ),
        actions=[
            ft.Button(content="Cancel", on_click=on_cancel),
            ft.Button(content="Next", on_click=on_next),
        ],
    )

    return modal