from kivy.app import App
from kivy.uix.boxlayout import BoxLayout


class IndexPage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TestApp(App):
    def build(self):
        return IndexPage()


if __name__ == "__main__":
    TestApp().run()
