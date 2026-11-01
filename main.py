import traceback
import flet as ft


def build(page: ft.Page):
    page.title = "Login App"
    page.padding = 0
    page.bgcolor = "#00789e"

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

    user = {"username": "user1", "password": "pass1"}

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
            if username.value == user["username"] and password.value == user["password"]:
                print("Welcome Back Sir!")
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
                        ft.TextButton("Forgot password"),
                    ],
                ),
                ft.Button("Login", width=260, height=50, on_click=login_click),
                error_message,
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=0,
                    controls=[
                        ft.Text("Don't have an account?", size=14),
                        ft.TextButton("Sign up"),
                    ],
                ),
            ],
        ),
    )

    page.add(
        ft.Row(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[card],
        )
    )


def main(page: ft.Page):
    try:
        build(page)
    except Exception:
        page.add(ft.Text(traceback.format_exc(), color="red", selectable=True))
        page.update()


ft.run(main)