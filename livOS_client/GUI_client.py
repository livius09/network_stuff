from nicegui import ui

def lama():
    print("balls")

ui.button('Click me!', on_click=lambda: ui.notify('You clicked me!'))

ui.run()