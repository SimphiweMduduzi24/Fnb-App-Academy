import flet as ft
from pages.login import login_page
from pages.register import register_page
from pages.home import home_page


def main(page: ft.Page):
    page.title = "FNB App"
    page.padding = 0

    def route_change(e=None):
        page.views.clear()
        if page.route == "/register":
            page.views.append(register_page(page))
        elif page.route == "/home":
            page.views.append(home_page(page))
        else:
            page.views.append(login_page(page))
        page.update()

    async def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    route_change()


ft.run(main)