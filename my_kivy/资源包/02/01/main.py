from kivy.app import App
from kivy.uix.floatlayout import FloatLayout

class SizeFloat(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class SizeApp(App):
    def build(self):
        return SizeFloat()

if __name__ == '__main__':
    SizeApp().run()
