from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class TaleApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.input = TextInput(hint_text='Enter your input here')
        self.output = Label(text='Output will appear here')
        self.button = Button(text='Generate Tale')
        self.button.bind(on_press=self.generate_tale)

        self.add_widget(self.input)
        self.add_widget(self.button)
        self.add_widget(self.output)

    def generate_tale(self, instance):
        user_input = self.input.text
        # Replace this with your actual processing logic
        result = f"Tale based on: {user_input}"
        self.output.text = result

class TaleAppMain(App):
    def build(self):
        return TaleApp()

if __name__ == '__main__':
    TaleAppMain().run()
