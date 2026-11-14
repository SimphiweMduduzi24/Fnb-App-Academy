import flet as ft
import httpx

API_BASE_URL = "http://127.0.0.1:8000"


# =====================================================================
# Page setup
# =====================================================================
def configure_page(page: ft.Page) -> None:
    page.title = "Local Events"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 450
    page.window.height = 700
    page.window.resizable = False


# =====================================================================
# Connect to the backend
# =====================================================================
async def api_request(method: str, path: str, **kwargs):
    url = f"{API_BASE_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.request(method, url, **kwargs)

    except httpx.ConnectError as exc:
        raise Exception("Could not connect to the backend") from exc
    except httpx.TimeoutException as exc:
        raise Exception("The backend took too long to respond") from exc
    except httpx.RequestError as exc:
        raise Exception(f"Network error calling {url}: {exc}") from exc

    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        # FastAPI validation errors come back as a list
        if isinstance(detail, list):
            detail = "Please check your email and password (password needs 6+ characters)."
        raise Exception(str(detail))

    return response.json()


async def api_login(email: str, password: str) -> str:
    data = await api_request(
        "POST",
        "/auth/login",
        json={"email": email, "password": password},
    )
    return data["email"]


async def api_register(email: str, password: str) -> str:
    data = await api_request(
        "POST",
        "/auth/register",
        json={"email": email, "password": password},
    )
    return data["email"]


async def api_get_events(category: str | None = None, saved_only: bool = False) -> list:
    params = {}
    if category:
        params["category"] = category
    if saved_only:
        params["saved"] = "true"
    return await api_request("GET", "/events", params=params)


async def api_save_event(event_id: str) -> dict:
    return await api_request("POST", f"/events/{event_id}/save")


async def api_unsave_event(event_id: str) -> dict:
    return await api_request("DELETE", f"/events/{event_id}/save")


# =====================================================================
# Navigating between screens
# =====================================================================
def set_content(page: ft.Page, control: ft.Control) -> None:
    page.controls.clear()
    page.add(control)
    page.update()


def show_login(page: ft.Page, state: dict) -> None:
    state["user_email"] = None
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    set_content(page, build_login_view(page, state))


def show_signup(page: ft.Page, state: dict) -> None:
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    set_content(page, build_signup_view(page, state))


# =====================================================================
# Shared look
# =====================================================================
def card_shadow() -> ft.BoxShadow:
    return ft.BoxShadow(
        blur_radius=12,
        color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
        offset=ft.Offset(0, 3),
    )


def info_row(icon_name: str, text: str, size: int = 14) -> ft.Control:
    return ft.Row(
        controls=[
            ft.Icon(icon_name, size=size + 3, color=ft.Colors.GREY_600),
            ft.Text(text, size=size, color=ft.Colors.GREY_800),
        ],
        spacing=8,
    )


# =====================================================================
# Login screen
# =====================================================================
def build_login_view(page: ft.Page, state: dict) -> ft.Control:
    email_input = ft.TextField(
        label="Email Address",
        hint_text="example@gmail.com",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_radius=10,
        width=300,
    )

    password_input = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINED,
        border_radius=10,
        width=300,
    )

    error_text = ft.Text(
        value="",
        color=ft.Colors.RED_ACCENT_400,
        size=12,
        visible=False,
    )

    def show_error(message: str) -> None:
        error_text.value = message
        error_text.visible = True
        page.update()

    login_button = ft.Button(
        content="Log In",
        width=300,
        height=50,
        elevation=2,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_900,
        ),
        on_click=lambda e: page.run_task(handle_login_click, e),
    )

    async def handle_login_click(e: ft.ControlEvent) -> None:
        email = (email_input.value or "").strip()
        password = password_input.value or ""

        if not email or not password:
            show_error("Please fill in all the fields.")
            return

        if "@" not in email or "." not in email.split("@")[-1]:
            show_error("Please enter a valid email address.")
            return

        error_text.visible = False
        login_button.disabled = True
        page.update()

        try:
            confirmed_email = await api_login(email, password)
        except Exception as ex:
            login_button.disabled = False
            show_error(str(ex))
            return

        state["user_email"] = confirmed_email
        await show_events(page, state)

    return ft.Container(
        width=360,
        padding=30,
        border_radius=16,
        bgcolor=ft.Colors.WHITE,
        shadow=card_shadow(),
        content=ft.Column(
            tight=True,
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Welcome Back", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ft.Text("Sign in to see local events", size=14, color=ft.Colors.GREY_600),
                ft.Container(height=6),
                email_input,
                password_input,
                error_text,
                login_button,
                ft.TextButton(
                    content=ft.Text("Don't have an account? Sign Up"),
                    on_click=lambda e: show_signup(page, state),
                ),
            ],
        ),
    )


# =====================================================================
# Sign up screen
# =====================================================================
def build_signup_view(page: ft.Page, state: dict) -> ft.Control:
    email_input = ft.TextField(
        label="Email Address",
        hint_text="example@gmail.com",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_radius=10,
        width=300,
    )

    password_input = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINED,
        border_radius=10,
        hint_text="at least 6 characters",
        width=300,
    )

    confirm_password_input = ft.TextField(
        label="Confirm Password",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINED,
        border_radius=10,
        width=300,
    )

    error_text = ft.Text(
        value="",
        color=ft.Colors.RED_ACCENT_400,
        size=12,
        visible=False,
    )

    def show_error(message: str) -> None:
        error_text.value = message
        error_text.visible = True
        page.update()

    signup_button = ft.Button(
        content="Create Account",
        width=300,
        height=50,
        elevation=2,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_900,
        ),
        on_click=lambda e: page.run_task(handle_sign_up_click, e),
    )

    async def handle_sign_up_click(e: ft.ControlEvent) -> None:
        email = (email_input.value or "").strip()
        password = password_input.value or ""
        confirm_password = confirm_password_input.value or ""

        if not email or not password or not confirm_password:
            show_error("Please fill in all the fields.")
            return

        if "@" not in email or "." not in email.split("@")[-1]:
            show_error("Please enter a valid email address.")
            return

        if len(password) < 6:
            show_error("Password must be at least 6 characters long.")
            return

        if password != confirm_password:
            show_error("Passwords do not match.")
            return

        error_text.visible = False
        signup_button.disabled = True
        page.update()

        try:
            confirmed_email = await api_register(email, password)
        except Exception as ex:
            signup_button.disabled = False
            show_error(str(ex))
            return

        state["user_email"] = confirmed_email
        await show_events(page, state)

    return ft.Container(
        width=360,
        padding=30,
        border_radius=16,
        bgcolor=ft.Colors.WHITE,
        shadow=card_shadow(),
        content=ft.Column(
            tight=True,
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Create Account", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ft.Text("Sign up to see local events", size=14, color=ft.Colors.GREY_600),
                ft.Container(height=6),
                email_input,
                password_input,
                confirm_password_input,
                error_text,
                signup_button,
                ft.TextButton(
                    content=ft.Text("Already have an account? Log In"),
                    on_click=lambda e: show_login(page, state),
                ),
            ],
        ),
    )


# =====================================================================
# Events list screen
# =====================================================================
CATEGORIES = ["All", "Music", "Markets", "Sports", "Community", "Saved"]

CATEGORY_STYLE = {
    "Music": (ft.Icons.MUSIC_NOTE_ROUNDED, ft.Colors.PURPLE_400),
    "Markets": (ft.Icons.STOREFRONT_ROUNDED, ft.Colors.ORANGE_700),
    "Sports": (ft.Icons.SPORTS_SOCCER_ROUNDED, ft.Colors.GREEN_400),
    "Community": (ft.Icons.GROUPS_ROUNDED, ft.Colors.BLUE_400),
}
DEFAULT_ICON = ft.Icons.EVENT_ROUNDED
DEFAULT_COLOR = ft.Colors.GREY_600


def style_for(category: str) -> tuple:
    return CATEGORY_STYLE.get(category, (DEFAULT_ICON, DEFAULT_COLOR))


def build_category_chips(page: ft.Page, state: dict, active_category: str) -> ft.Row:
    chips = []
    for category in CATEGORIES:
        chips.append(
            ft.Chip(
                label=ft.Text(category),
                selected=(category == active_category),
                leading=ft.Icon(ft.Icons.BOOKMARK_ROUNDED, size=15) if category == "Saved" else None,
                on_click=lambda e, c=category: page.run_task(show_events, page, state, c),
            )
        )
    return ft.Row(controls=chips, wrap=True, spacing=8, run_spacing=8)


def build_loading_state() -> ft.Control:
    return ft.Column(
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[ft.ProgressRing(), ft.Text("Loading events...", color=ft.Colors.GREY_600)],
    )


def build_empty_state() -> ft.Control:
    return ft.Column(
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Icon(ft.Icons.EVENT_BUSY_ROUNDED, size=48, color=ft.Colors.GREY_500),
            ft.Text("No events found", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("Try another category.", color=ft.Colors.GREY_600),
        ],
    )


def build_error_state(page: ft.Page, state: dict, message: str, active_category: str) -> ft.Control:
    return ft.Column(
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, size=48, color=ft.Colors.RED_ACCENT_400),
            ft.Text(message, color=ft.Colors.RED_ACCENT_400, text_align=ft.TextAlign.CENTER),
            ft.Button(
                content="Try again",
                on_click=lambda e: page.run_task(show_events, page, state, active_category),
            ),
        ],
    )


def build_events_shell(state: dict, chips: ft.Control, content_area: ft.Control, on_logout) -> ft.Control:
    return ft.Container(
        expand=True,
        padding=ft.Padding(left=18, right=18, top=16, bottom=10),
        content=ft.Column(
            expand=True,
            spacing=12,
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(
                            expand=True,
                            spacing=0,
                            controls=[
                                ft.Text("Local Events", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                                ft.Text(state.get("user_email") or "", size=12, color=ft.Colors.GREY_600),
                            ],
                        ),
                        ft.IconButton(icon=ft.Icons.LOGOUT_ROUNDED, tooltip="Log out", on_click=on_logout),
                    ],
                ),
                chips,
                content_area,
            ],
        ),
    )


def build_event_card(page: ft.Page, state: dict, event: dict, active_category: str) -> ft.Control:
    icon, color = style_for(event["category"])
    return ft.Container(
        padding=14,
        border_radius=12,
        bgcolor=ft.Colors.WHITE,
        shadow=card_shadow(),
        on_click=lambda e: show_event_detail(page, state, event, active_category),
        content=ft.Row(
            spacing=12,
            controls=[
                ft.Container(
                    content=ft.Icon(icon, color=color, size=24),
                    bgcolor=ft.Colors.with_opacity(0.12, color),
                    border_radius=10,
                    padding=10,
                ),
                ft.Column(
                    expand=True,
                    spacing=2,
                    controls=[
                        ft.Text(event["title"], size=15, weight=ft.FontWeight.BOLD),
                        info_row(ft.Icons.CALENDAR_TODAY_ROUNDED, event["date"], size=12),
                        info_row(ft.Icons.LOCATION_ON_OUTLINED, event["location"], size=12),
                    ],
                ),
                ft.Icon(
                    ft.Icons.BOOKMARK_ROUNDED if event["saved"] else ft.Icons.BOOKMARK_BORDER_ROUNDED,
                    color=ft.Colors.BLUE_900 if event["saved"] else ft.Colors.GREY_500,
                    size=22,
                ),
            ],
        ),
    )


# =====================================================================
# Events detail screen
# =====================================================================
def build_event_detail_view(page: ft.Page, state: dict, event: dict, active_category: str = "All") -> ft.Control:
    icon, color = style_for(event["category"])

    save_button = ft.IconButton(
        icon=ft.Icons.BOOKMARK_ROUNDED if event["saved"] else ft.Icons.BOOKMARK_BORDER_ROUNDED,
        icon_color=ft.Colors.BLUE_900 if event["saved"] else ft.Colors.GREY_500,
        tooltip="Remove from saved" if event["saved"] else "Save event",
    )

    async def handle_toggle_save(e: ft.ControlEvent) -> None:
        save_button.disabled = True
        page.update()

        try:
            if event["saved"]:
                updated = await api_unsave_event(event["id"])
            else:
                updated = await api_save_event(event["id"])
        except Exception as ex:
            page.show_dialog(ft.SnackBar(ft.Text(f"Couldn't update save status: {ex}")))
            save_button.disabled = False
            page.update()
            return

        event["saved"] = updated["saved"]
        save_button.icon = ft.Icons.BOOKMARK_ROUNDED if event["saved"] else ft.Icons.BOOKMARK_BORDER_ROUNDED
        save_button.icon_color = ft.Colors.BLUE_900 if event["saved"] else ft.Colors.GREY_500
        save_button.tooltip = "Remove from saved" if event["saved"] else "Save event"
        save_button.disabled = False
        page.update()

    save_button.on_click = lambda e: page.run_task(handle_toggle_save, e)

    return ft.Container(
        expand=True,
        padding=ft.Padding(left=18, right=18, top=20, bottom=10),
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_ROUNDED,
                            on_click=lambda e: page.run_task(show_events, page, state, active_category),
                        ),
                        ft.Container(expand=True),
                        save_button,
                    ],
                ),
                ft.Container(
                    content=ft.Icon(icon, color=color, size=40),
                    bgcolor=ft.Colors.with_opacity(0.12, color),
                    border_radius=14,
                    padding=16,
                ),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Text(event["category"], size=12, weight=ft.FontWeight.BOLD, color=color),
                    bgcolor=ft.Colors.with_opacity(0.12, color),
                    border_radius=20,
                    padding=ft.Padding(left=12, right=12, top=4, bottom=4),
                ),
                ft.Container(height=8),
                ft.Text(event["title"], size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=6),
                info_row(ft.Icons.CALENDAR_TODAY_ROUNDED, event["date"]),
                info_row(ft.Icons.ACCESS_TIME_ROUNDED, event["time"]),
                info_row(ft.Icons.LOCATION_ON_OUTLINED, event["location"]),
                ft.Divider(height=28),
                ft.Text("About this event", size=15, weight=ft.FontWeight.BOLD),
                ft.Container(height=4),
                ft.Text(event["description"], size=14, color=ft.Colors.GREY_800),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
    )


# =====================================================================
# Wire up events screens
# =====================================================================
async def show_events(page: ft.Page, state: dict, active_category: str = "All") -> None:
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

    content_area = ft.Container(expand=True, content=build_loading_state())
    chips = build_category_chips(page, state, active_category)
    set_content(
        page,
        build_events_shell(state, chips, content_area, on_logout=lambda e: show_login(page, state)),
    )

    category = None if active_category in ("All", "Saved") else active_category
    saved_only = active_category == "Saved"

    try:
        events = await api_get_events(category=category, saved_only=saved_only)
    except Exception as ex:
        content_area.content = build_error_state(page, state, str(ex), active_category)
        page.update()
        return

    if not events:
        content_area.content = build_empty_state()
    else:
        content_area.content = ft.ListView(
            controls=[build_event_card(page, state, event, active_category) for event in events],
            spacing=10,
            expand=True,
            padding=ft.Padding.only(top=6),
        )
    page.update()


def show_event_detail(page: ft.Page, state: dict, event: dict, active_category: str = "All") -> None:
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    set_content(page, build_event_detail_view(page, state, event, active_category))


# =====================================================================
# Entry point
# =====================================================================
def main(page: ft.Page) -> None:
    configure_page(page)
    state = {"user_email": None}
    show_login(page, state)


if __name__ == "__main__":
    ft.run(main)
