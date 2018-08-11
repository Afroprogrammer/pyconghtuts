from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.textfields import MDTextField
from kivymd.theming import ThemeManager
import pyjokes
from plyer import vibrator,notification
from kivymd.list import MDList
from kivymd.spinner import MDSpinner
from kivy.uix.modalview import ModalView
import thread
import time
from kivy.animation import Clock
from kivy.uix.image import AsyncImage
from kivy.lib import osc
# from plyer.platforms.android import activity
# from jnius import autoclass
from kivymd.list import ILeftBody, IRightBodyTouch,OneLineAvatarIconListItem
from kivymd.button import MDIconButton
from kivy.properties import StringProperty
from peewee import *
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform

settings = JsonStore("settings.json")
db = SqliteDatabase('todo.sqlite')


class TodoItem(OneLineAvatarIconListItem):
    def __init_(self,**kwargs):
        super(TodoItem,self).__init__(**kwargs)

    def on_press(self):
        print("yead",self.text)
        content = MDLabel(text=self.text)
        ReadPopup(title=self.text,size_hint=(0.8, 0.2),content= content,background= "./assets/rss_back.png").open()


class IconRightSampleWidget(IRightBodyTouch, MDIconButton):
    id = StringProperty(None)
    name = StringProperty(None)

    def on_press(self):
        print("yeah on icon",self.id)
        # Todo.get(id=self.id).delete_instance()
        "use this to show them how to transverse the widget tree"
        # interface = Interface()
        global interface
        print(interface)
        # interface.ids.spinner.active=True
        interface.ids.todo_list.remove_widget(self.parent.parent)
        # print(self.parent.parent.parent.remove_widget(self.parent.parent))


class AvatarSampleWidget(ILeftBody, AsyncImage):
    pass


class Todo(Model):
    name = CharField()
    class Meta:
        database = db


class MD(MDDialog):
    def __init__(self,**kwargs):
        super(MD,self).__init__(**kwargs)


class Interface(BoxLayout):
    spinner = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Interface, self).__init__(**kwargs)

    def get_joke(self):
        joke = pyjokes.get_joke()
        self.ids.get_a_joke_text.text = joke
        vibrator.vibrate(.1)
        notification.notify(title='test',message='well')
        print("getting a joke")

    def share(self):
        # print(self.ids.get_a_joke_text.text)
        from jnius import autoclass
        PythonActivity = autoclass('org.renpy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        String = autoclass('java.lang.String')
        intent = Intent()
        intent.setAction(Intent.ACTION_SEND)
        subject = 'PyPod Daily Jokes from Pyjokes'
        intent.putExtra(Intent.EXTRA_SUBJECT, subject)
        joke = self.ids.get_a_joke_text.text
        intent.putExtra(Intent.EXTRA_TEXT, String('{}'.format(joke)))
        intent.setType('text/plain')
        chooser = Intent.createChooser(intent, String('Share...'))
        PythonActivity.mActivity.startActivity(chooser)


    def my_callback(self,dt):
        self.ids.spinner.active = True
        self.ids.todo_list.clear_widgets()
        for todo in Todo.select():
            item = TodoItem(text=todo.name)
            item.add_widget(AvatarSampleWidget(source="./assets/avatar.png"))
            item.add_widget(IconRightSampleWidget(icon="delete-sweep", id=str(todo.id), name=todo.name))
            self.ids.todo_list.add_widget(item)
            time.sleep(1)
        self.ids.spinner.active = False

    def refresh(self):
        # Clock.schedule_once(self.my_callback,1)
        thread.start_new_thread(self.my_callback,("pycon",))
        # self.ids.spinner.active = True
        # self.ids.todo_list.clear_widgets()
        # for todo in Todo.select():
        #     item = TodoItem(text=todo.name)
        #     item.add_widget(AvatarSampleWidget(source="./assets/avatar.png"))
        #     item.add_widget(IconRightSampleWidget(icon="delete-sweep",id=str(todo.id),name=todo.name))
        #     self.ids.todo_list.add_widget(item)
        # self.ids.spinner.active = False
        # kwargs = {'title': "pycon todo", 'message': "new item added"}
        # notification.notify(**kwargs)


    def add(self,text):
        print("adding a new text")
        print(text)
        Todo(name=text).save()
        print("saved todo item")
        # button = Button(text="hi man")
        # self.ids.todo_list.add_widget(button)
        # printter-alert(interface.ids['todo_list'].add_widget(button))


    def open_modal(self):
        LoadDialog().open()

    def close(self):
        self.ids.spinner.active = False


class LoadDialog(Popup,FloatLayout):
    def __init__(self, **kwargs):
        super(LoadDialog, self).__init__(**kwargs)

    # interface = ObjectProperty(None)
    def add(self):
        int = Interface()
        int.add(self.ids.add_new_note.text)
        self.dismiss()

        # _thread.start_new_thread(self.shiemor, ('dbb',))
        # print("saved to db")

    def shiermor_thread(self):
        thread.start_new_thread(self.shiemor, ('dbb',))

    def shiemor(self, dbb):
        int = Interface()
        int.add(self.ids.add_new_note.text)
        self.dismiss()


class ReadPopup(Popup):
    def __init__(self, **kwargs):
        super(ReadPopup, self).__init__(**kwargs)






class Pycon(App):
    theme_cls = ThemeManager()
    title = "Pycon GH"
    
    #from kivy.core.window import Window
    #Window.size = (370, 600)

    def build(self):
        self.service = None
        #self.start_service()
        global interface
        osc.init()
        oscid = osc.listen(port=3002)
        Clock.schedule_interval(lambda *x: osc.readQueue(oscid), 0)
        
        if settings.exists("db"):
            pass
        else:
            settings.put("db",created=True)
            db.create_table(Todo)
        interface = Interface()
        return interface
        # return Interface()
    def start_service(self):
        if platform == 'android':
            from android import AndroidService
            service = AndroidService()
            service.start('pycon')
            self.service = service
    def add(self):
        interface = Interface()
        interface.ids.spinner.active = False


if __name__ == "__main__":
    Pycon().run()
