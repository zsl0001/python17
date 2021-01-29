from kivy.app import App
from kivy.uix.floatlayout import FloatLayout


class AddcanvasApp(App):
    def build(self):
        return ButtonFloatLayout()


class ButtonFloatLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from kivy.uix.button import Button
        bt = Button(text='点击', font_size=60, on_release=self.release_button, on_press=self.press_button)

        self.add_widget(bt)

    def press_button(self, arg):
        print('press_button is running')

    def release_button(self, arg):
        print('release_button is running')


if __name__ == '__main__':
    AddcanvasApp().run()
