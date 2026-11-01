import asyncio
import json
from pathlib import Path

import flet as ft

USERS_FILE = Path(__file__).parent.parent / "assets" / "data" / "users.json"


def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"users": []}


def save_users(data):
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def register_page(page: ft.Page) -> ft.View:
    page.title = "Registration Page"

    def field(hint, secret=False):
        return ft.TextField(
            hint_text=hint,
            width=340,
            password=secret,
            can_reveal_password=secret,
            border_color="#0084a8",
            focused_border_color="#0084a8",
            border=ft.OutlineInputBorder(border_radius=10),
        )

    username = field("Username")
    fullname = field("Enter your fullname")
    password = field("Password", True)
    confirm = field("Confirm Password", True)
    terms = ft.Checkbox(label="I agree to the Terms & Conditions")
    error_message = ft.Text("", color="#ff0000", weight=ft.FontWeight.BOLD, visible=False)

    def go_login(e):
        asyncio.create_task(page.push_route("/login"))

    def register_click(e):
        error_message.visible = True
        if not (username.value and fullname.value and password.value):
            error_message.value = "Please fill in all fields"
        elif password.value != confirm.value:
            error_message.value = "Passwords do not match"
        elif not terms.value:
            error_message.value = "You must accept the terms"
        else:
            data = load_users()
            if any(u["username"].lower() == username.value.lower() for u in data["users"]):
                error_message.value = "Username already taken"
            else:
                data["users"].append({
                    "id": f"usr_{len(data['users']) + 1:03}",
                    "name": fullname.value,
                    "username": username.value,
                    "password": password.value,
                })
                save_users(data)
                go_login(e)
                return
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
                ft.Text("Register", size=40, weight=ft.FontWeight.BOLD, color="#00789e"),
                username, fullname, password, confirm, terms,
                error_message,
                ft.Button("Register", width=260, height=50, on_click=register_click),
                ft.TextButton("Back to login", on_click=go_login),
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

    return ft.View(route="/register", padding=0, controls=[body])