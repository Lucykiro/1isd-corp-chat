import socket
import threading
import json
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(text='Messenger', font_size='30sp', size_hint_y=0.3)
        layout.add_widget(title)
        
        self.server_ip = TextInput(
            hint_text='IP сервера',
            text='192.168.1.1',  # Замените на IP вашего сервера
            multiline=False,
            size_hint_y=0.1
        )
        layout.add_widget(self.server_ip)
        
        self.username_input = TextInput(
            hint_text='Ваше имя',
            multiline=False,
            size_hint_y=0.1
        )
        layout.add_widget(self.username_input)
        
        login_btn = Button(
            text='Войти',
            size_hint_y=0.2,
            background_color=(0.2, 0.6, 1, 1)
        )
        login_btn.bind(on_press=self.login)
        layout.add_widget(login_btn)
        
        self.add_widget(layout)
    
    def login(self, instance):
        username = self.username_input.text.strip()
        server_ip = self.server_ip.text.strip()
        
        if username and server_ip:
            app = App.get_running_app()
            app.username = username
            app.server_ip = server_ip
            app.connect_to_server()
            self.manager.current = 'main'

class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        
        # Верхняя панель
        top_panel = BoxLayout(size_hint_y=0.1)
        self.chat_title = Label(text='Выберите чат')
        top_panel.add_widget(self.chat_title)
        
        add_btn = Button(text='+', size_hint_x=0.2)
        add_btn.bind(on_press=self.show_add_menu)
        top_panel.add_widget(add_btn)
        
        back_btn = Button(text='Назад', size_hint_x=0.2)
        back_btn.bind(on_press=self.go_back)
        top_panel.add_widget(back_btn)
        
        self.layout.add_widget(top_panel)
        
        # Основная область с вкладками
        self.main_area = BoxLayout(orientation='horizontal')
        
        # Список чатов
        chats_scroll = ScrollView(size_hint_x=0.4)
        self.chats_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.chats_layout.bind(minimum_height=self.chats_layout.setter('height'))
        chats_scroll.add_widget(self.chats_layout)
        self.main_area.add_widget(chats_scroll)
        
        # Область сообщений
        messages_area = BoxLayout(orientation='vertical', size_hint_x=0.6)
        
        messages_scroll = ScrollView()
        self.messages_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.messages_layout.bind(minimum_height=self.messages_layout.setter('height'))
        messages_scroll.add_widget(self.messages_layout)
        messages_area.add_widget(messages_scroll)
        
        # Панель ввода
        input_panel = BoxLayout(size_hint_y=0.15)
        self.message_input = TextInput(
            hint_text='Введите сообщение...',
            multiline=False,
            size_hint_x=0.7
        )
        self.message_input.bind(on_text_validate=self.send_message)
        input_panel.add_widget(self.message_input)
        
        send_btn = Button(text='Отпр', size_hint_x=0.3)
        send_btn.bind(on_press=self.send_message)
        input_panel.add_widget(send_btn)
        
        messages_area.add_widget(input_panel)
        self.main_area.add_widget(messages_area)
        
        self.layout.add_widget(self.main_area)
        self.add_widget(self.layout)
        
        self.current_chat = None
        self.current_chat_type = None
    
    def show_add_menu(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        
        private_btn = Button(text='Личный чат', size_hint_y=0.3)
        private_btn.bind(on_press=self.add_private_chat)
        content.add_widget(private_btn)
        
        create_group_btn = Button(text='Создать группу', size_hint_y=0.3)
        create_group_btn.bind(on_press=self.create_group)
        content.add_widget(create_group_btn)
        
        join_group_btn = Button(text='Вступить в группу', size_hint_y=0.3)
        join_group_btn.bind(on_press=self.join_group)
        content.add_widget(join_group_btn)
        
        close_btn = Button(text='Закрыть', size_hint_y=0.1)
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Добавить чат',
            content=content,
            size_hint=(0.8, 0.6)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def add_private_chat(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        
        username_input = TextInput(hint_text='Имя пользователя', size_hint_y=0.3)
        content.add_widget(username_input)
        
        btn_layout = BoxLayout(size_hint_y=0.3)
        add_btn = Button(text='Добавить')
        cancel_btn = Button(text='Отмена')
        btn_layout.add_widget(add_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Добавить личный чат',
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        def add_chat(btn):
            username = username_input.text.strip()
            if username:
                app = App.get_running_app()
                app.add_private_chat(username)
                popup.dismiss()
        
        add_btn.bind(on_press=add_chat)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def create_group(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        
        group_input = TextInput(hint_text='Название группы', size_hint_y=0.3)
        content.add_widget(group_input)
        
        btn_layout = BoxLayout(size_hint_y=0.3)
        create_btn = Button(text='Создать')
        cancel_btn = Button(text='Отмена')
        btn_layout.add_widget(create_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Создать группу',
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        def create_group(btn):
            group_name = group_input.text.strip()
            if group_name:
                app = App.get_running_app()
                app.create_group(group_name)
                popup.dismiss()
        
        create_btn.bind(on_press=create_group)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def join_group(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        
        group_input = TextInput(hint_text='Название группы', size_hint_y=0.3)
        content.add_widget(group_input)
        
        btn_layout = BoxLayout(size_hint_y=0.3)
        join_btn = Button(text='Вступить')
        cancel_btn = Button(text='Отмена')
        btn_layout.add_widget(join_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Вступить в группу',
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        def join_group(btn):
            group_name = group_input.text.strip()
            if group_name:
                app = App.get_running_app()
                app.join_group(group_name)
                popup.dismiss()
        
        join_btn.bind(on_press=join_group)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def go_back(self, instance):
        App.get_running_app().stop()
    
    def send_message(self, instance):
        app = App.get_running_app()
        message = self.message_input.text.strip()
        if message and app.current_chat and app.current_chat_type:
            app.send_message(message)
            self.message_input.text = ''
    
    def update_chats_list(self, private_chats, group_chats):
        self.chats_layout.clear_widgets()
        
        # Добавляем личные чаты
        for chat in private_chats:
            btn = Button(
                text=f"👤 {chat['user']}",
                size_hint_y=None,
                height=60
            )
            btn.bind(on_press=lambda x, user=chat['user']: self.select_chat('private', user))
            self.chats_layout.add_widget(btn)
        
        # Добавляем группы
        for chat in group_chats:
            btn = Button(
                text=f"👥 {chat['group_name']}",
                size_hint_y=None,
                height=60
            )
            btn.bind(on_press=lambda x, group=chat['group_name']: self.select_chat('group', group))
            self.chats_layout.add_widget(btn)
    
    def select_chat(self, chat_type, chat_id):
        app = App.get_running_app()
        app.select_chat(chat_type, chat_id)
        
        if chat_type == 'private':
            self.chat_title.text = f"👤 {chat_id}"
        else:
            self.chat_title.text = f"👥 {chat_id}"
    
    def update_messages(self, messages):
        self.messages_layout.clear_widgets()
        
        for msg in messages:
            timestamp = datetime.fromisoformat(msg['timestamp']).strftime("%H:%M")
            sender = msg['from']
            text = msg['text']
            
            message_text = f"[{timestamp}] {sender}: {text}"
            label = Label(
                text=message_text,
                size_hint_y=None,
                height=40,
                text_size=(Window.width * 0.5, None),
                halign='left',
                valign='middle'
            )
            label.bind(texture_size=label.setter('size'))
            self.messages_layout.add_widget(label)
        
        # Прокручиваем к последнему сообщению
        if self.messages_layout.height > self.messages_layout.parent.height:
            self.messages_layout.parent.scroll_y = 0
    
    def add_message(self, message):
        timestamp = datetime.fromisoformat(message['timestamp']).strftime("%H:%M")
        sender = message['from']
        text = message['text']
        
        message_text = f"[{timestamp}] {sender}: {text}"
        label = Label(
            text=message_text,
            size_hint_y=None,
            height=40,
            text_size=(Window.width * 0.5, None),
            halign='left',
            valign='middle'
        )
        label.bind(texture_size=label.setter('size'))
        self.messages_layout.add_widget(label)

class MessengerMobileApp(App):
    def __init__(self):
        super().__init__()
        self.socket = None
        self.username = None
        self.server_ip = None
        self.private_chats = []
        self.group_chats = []
        self.current_chat = None
        self.current_chat_type = None
        self.chat_history = {}
    
    def build(self):
        self.sm = ScreenManager()
        self.login_screen = LoginScreen(name='login')
        self.chat_screen = ChatScreen(name='main')
        self.sm.add_widget(self.login_screen)
        self.sm.add_widget(self.chat_screen)
        return self.sm
    
    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_ip, 5000))
            
            # Регистрируем пользователя
            register_msg = {
                'type': 'register',
                'username': self.username
            }
            self.socket.send(json.dumps(register_msg).encode('utf-8'))
            
            # Запускаем поток для приема сообщений
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except Exception as e:
            self.show_error(f"Ошибка подключения: {e}")
            return False
    
    def receive_messages(self):
        while True:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                message = json.loads(data)
                msg_type = message.get('type')
                
                if msg_type == 'chats_update':
                    self.private_chats = message.get('private_chats', [])
                    self.group_chats = message.get('group_chats', [])
                    Clock.schedule_once(lambda dt: self.update_ui())
                
                elif msg_type == 'private_message':
                    sender = message['from']
                    text = message['text']
                    timestamp = message.get('timestamp')
                    
                    # Сохраняем в историю
                    chat_key = f"private_{sender}"
                    if chat_key not in self.chat_history:
                        self.chat_history[chat_key] = []
                    
                    self.chat_history[chat_key].append(message)
                    
                    # Если это текущий чат, обновляем UI
                    if (self.current_chat_type == 'private' and 
                        self.current_chat == sender):
                        Clock.schedule_once(lambda dt: self.chat_screen.add_message(message))
                
                elif msg_type == 'group_message':
                    group = message['group']
                    text = message['text']
                    timestamp = message.get('timestamp')
                    
                    # Сохраняем в историю
                    chat_key = f"group_{group}"
                    if chat_key not in self.chat_history:
                        self.chat_history[chat_key] = []
                    
                    self.chat_history[chat_key].append(message)
                    
                    # Если это текущая группа, обновляем UI
                    if (self.current_chat_type == 'group' and 
                        self.current_chat == group):
                        Clock.schedule_once(lambda dt: self.chat_screen.add_message(message))
                
                elif msg_type == 'chat_history':
                    chat_type = message['chat_type']
                    chat_id = message['chat_id']
                    history = message['history']
                    
                    chat_key = f"{chat_type}_{chat_id}"
                    self.chat_history[chat_key] = history
                    
                    # Если это текущий чат, обновляем сообщения
                    if ((chat_type == 'private' and self.current_chat_type == 'private' and self.current_chat == chat_id) or
                        (chat_type == 'group' and self.current_chat_type == 'group' and self.current_chat == chat_id)):
                        Clock.schedule_once(lambda dt: self.chat_screen.update_messages(history))
                
            except Exception as e:
                print(f"Ошибка получения сообщения: {e}")
                break
    
    def update_ui(self):
        self.chat_screen.update_chats_list(self.private_chats, self.group_chats)
    
    def add_private_chat(self, username):
        chat_name = f"Личный: {username}"
        message = {
            'type': 'private_message',
            'from': self.username,
            'to': username,
            'text': 'Привет!'
        }
        self.socket.send(json.dumps(message, ensure_ascii=False).encode('utf-8'))
    
    def create_group(self, group_name):
        message = {
            'type': 'create_group',
            'group_name': group_name,
            'creator': self.username
        }
        self.socket.send(json.dumps(message).encode('utf-8'))
    
    def join_group(self, group_name):
        message = {
            'type': 'join_group',
            'group_name': group_name,
            'username': self.username
        }
        self.socket.send(json.dumps(message).encode('utf-8'))
    
    def select_chat(self, chat_type, chat_id):
        self.current_chat_type = chat_type
        self.current_chat = chat_id
        
        # Запрашиваем историю чата
        message = {
            'type': 'get_chat_history',
            'chat_type': chat_type,
            'chat_id': chat_id,
            'username': self.username
        }
        self.socket.send(json.dumps(message).encode('utf-8'))
    
    def send_message(self, text):
        if self.current_chat_type == 'private':
            message = {
                'type': 'private_message',
                'from': self.username,
                'to': self.current_chat,
                'text': text
            }
        else:
            message = {
                'type': 'group_message',
                'from': self.username,
                'group': self.current_chat,
                'text': text
            }
        
        try:
            self.socket.send(json.dumps(message, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.show_error(f"Ошибка отправки: {e}")
    
    def show_error(self, message):
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text=message))
        close_btn = Button(text='OK', size_hint_y=0.3)
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Ошибка',
            content=content,
            size_hint=(0.7, 0.4)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    MessengerMobileApp().run()