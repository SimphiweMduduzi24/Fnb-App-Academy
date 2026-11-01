import asyncio
import json
from pathlib import Path
import flet as ft
from components.password_reset import reset_password

USERS_FILE = Path(__file__).parent.parent / "assets" / "data" / "users.json"


def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)["users"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return []


def login_page(page: ft.Page) -> ft.View:
    page.title = "Login Page"

    def on_forgot_password(e):
        page.show_dialog(reset_password(page))

    def on_signup(e):
        asyncio.create_task(page.push_route("/register"))

    def label(icon, text):
        return ft.Row(
            spacing=10,
            controls=[
                ft.Icon(icon, color="#00789e", size=22),
                ft.Text(text, size=16, weight=ft.FontWeight.BOLD, color="#00789e"),
            ],
        )

    username = ft.TextField(hint_text="Username", width=340, border_radius=30)
    password = ft.TextField(
        hint_text="Password",
        password=True,
        can_reveal_password=True,
        width=340,
        border_radius=30,
    )

    error_message = ft.Text(
        "Invalid username or password",
        size=15,
        weight=ft.FontWeight.BOLD,
        color="#ff0000",
        visible=False,
    )

    def login_click(e):
        error_message.visible = False
        ok = True

        if not username.value:
            username.error = "Username cannot be left empty"
            ok = False
        else:
            username.error = None

        if not password.value:
            password.error = "Password cannot be left empty"
            ok = False
        else:
            password.error = None

        if ok:
            found = False
            for u in load_users():
                if (
                    u["username"].lower() == username.value.lower()
                    and u["password"] == password.value
                ):
                    found = True
                    break

            if found:
                asyncio.create_task(page.push_route("/home"))
            else:
                error_message.visible = True

        page.update()

    card = ft.Container(
        width=420,
        padding=30,
        bgcolor="#FFFFFF",
        border_radius=20,
        content=ft.Column(
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
            controls=[
                ft.Text("Login", size=40, weight=ft.FontWeight.BOLD, color="#00789e"),
                ft.Container(width=340, content=label(ft.Icons.PERSON, "Username:")),
                username,
                ft.Container(width=340, content=label(ft.Icons.LOCK, "Password:")),
                password,
                ft.Row(
                    width=340,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Checkbox(label="Keep me logged in"),
                        ft.GestureDetector(
                            content=ft.Text("Forgot password", color="#00789e"),
                            on_tap=on_forgot_password,
                        ),
                    ],
                ),
                ft.Button("Login", width=260, height=50, on_click=login_click),
                error_message,
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=0,
                    controls=[
                        ft.Text("Don't have an account?", size=14),
                        ft.TextButton("Sign up", on_click=on_signup),
                    ],
                ),
            ],
        ),
    )

    body = ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=["#003a4d", "#0086b3"],
        ),
        content=card,
    )
    return ft.View(route="/login", padding=0, controls=[body])