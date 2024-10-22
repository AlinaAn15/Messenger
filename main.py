import hashlib
from tkinter import *
from tkinter.messagebox import showinfo, showerror
import time
import re
from tkinter.simpledialog import askstring

users_file = 'users.txt'
current_user = None


class User:
    def __init__(self, username, password_hash, messages_count=0):
        self.username = username
        self.password_hash = password_hash
        self.messages_count = messages_count

    @staticmethod
    def gen_salt(password):
        def strShift(text, shiftt):
            result = []
            for char in text:
                if char.isalpha():
                    start = ord('A') if char.isupper() else ord('a')
                    result.append(chr(start + (ord(char) - start + shiftt) % 26))
                else:
                    result.append(char)
            return ''.join(result)

        shift = 3
        newstr = strShift(password, shift)
        new2str = newstr[::-1]
        mystr = "PYTHONISMYFAVOURITEOBJECT"
        return f"{new2str}_{mystr}"

    @staticmethod
    def hash_password(password):
        salt = User.gen_salt(password)
        sha1 = hashlib.sha256()
        sha1.update(salt.encode() + password.encode())
        return sha1.hexdigest()

    @staticmethod
    def load_users():
        users = {}
        try:
            with open(users_file, 'r') as file:
                for line in file:
                    if line.strip():
                        username, password_hash, messages_count = line.strip().split()
                        users[username] = User(username, password_hash, int(messages_count))
        except FileNotFoundError:
            pass
        return users

    @staticmethod
    def save_user(username, password_hash, messages_count):
        with open(users_file, 'a') as file:
            file.write(f"{username} {password_hash} {messages_count}\n")

    def check_password(self, password):
        return self.password_hash == User.hash_password(password)

    def increment_messages_count(self):
        self.messages_count += 1
        self.update_user_data()

    def update_user_data(self):
        users = User.load_users()
        users[self.username] = self

        with open(users_file, 'w') as file:
            for user in users.values():
                file.write(f"{user.username} {user.password_hash} {user.messages_count}\n")


class Post:
    def __init__(self, author, text, messenger_app, likes=0, liked_by=None):
        self.author = author
        self.time = time.strftime("%Y-%m-%d %H:%M")
        self.likes = likes
        self.text = text
        self.comments = []
        self.liked_by = liked_by if liked_by else []
        self.messenger_app = messenger_app

    def toggle_like(self, user, topic):
        if user.username in self.liked_by:
            self.likes -= 1
            self.liked_by.remove(user.username)
        else:
            self.likes += 1
            self.liked_by.append(user.username)
        self.update_likes(topic)

    def update_likes(self, topic):
        posts = self.messenger_app.load_chat_history(topic)
        for p in posts:
            if p.author == self.author and p.text == self.text and p.time == self.time:
                p.likes = self.likes
                p.liked_by = self.liked_by
                break
        self.messenger_app.save_chat_history(posts, topic)

    def display_likes(self, like_label):
        like_label.config(text=f"Likes: {self.likes}")

    def add_comment(self, comment):
        self.comments.append(comment)


class MessengerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Messenger')
        self.root.geometry('400x300')
        self.root['bg'] = "#EDC7B7"
        self.root.resizable(False, False)
        self.logUserName = StringVar()
        self.logPassword = StringVar()
        self.regUserName = StringVar()
        self.regPassword = StringVar()
        self.regPasswordCheck = StringVar()
        self.current_user = None
        self.loginScreen()

    def get_chat_file(self, topic):
        return f"{topic}_chat.txt"

    def save_message(self, post, topic):
        chat_file = self.get_chat_file(topic)
        with open(chat_file, 'a') as f:
            f.write(
                f"{post.author} ({post.time}): {post.text} | Лайки: {post.likes} | Лайкнули: {','.join(post.liked_by)}\n")

    def load_chat_history(self, topic):
        posts = []
        chat_file = self.get_chat_file(topic)
        try:
            with open(chat_file, 'r') as f:
                for line in f:
                    parts = line.strip().split(" | Лайки: ")
                    if len(parts) == 2:
                        message_part, likes_part = parts
                        if " | Лайкнули: " in likes_part:
                            text_part, liked_part = likes_part.split(" | Лайкнули: ", 1)
                        else:
                            text_part = likes_part
                            liked_part = ""

                        author_time, text = message_part.split("):", 1)
                        author, time = author_time.split("(", 1)

                        try:
                            likes = int(text_part)
                        except ValueError:
                            likes = 0

                        liked_by = liked_part.split(',') if liked_part else []
                        post = Post(author.strip(), text.strip(), self, likes, liked_by)
                        posts.append(post)
        except FileNotFoundError:
            return []
        return posts

    def save_chat_history(self, posts, topic):
        chat_file = self.get_chat_file(topic)
        with open(chat_file, 'w') as f:
            for post in posts:
                f.write(
                    f"{post.author} ({post.time}): {post.text} | Лайки: {post.likes} | Лайкнули: {','.join(post.liked_by)}\n")

    def loginScreen(self):
        self.root.geometry('500x300')
        self.root['bg'] = '#EDC7B7'
        self.clear_window()
        loglb = Label(self.root, text='Вход в систему', font=("Arial", 20, 'bold'), bg="#EDC7B7")
        loglb.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        nicklb = Label(self.root, text='Имя пользователя:', font=("Arial", 14), bg="#EDC7B7")
        nicklb.grid(row=1, column=0, padx=20, sticky=E)

        dis1 = Entry(self.root, textvariable=self.logUserName, font=("Arial", 14), width=20,
                     borderwidth=2, relief="solid")
        dis1.grid(row=1, column=1, padx=20, pady=10, sticky=W)

        pas1lb = Label(self.root, text='Пароль:', font=("Arial", 14), bg="#EDC7B7")
        pas1lb.grid(row=2, column=0, padx=20, sticky=E)

        dis2 = Entry(self.root, textvariable=self.logPassword, font=("Arial", 14), width=20,
                     borderwidth=2, relief="solid", show="*")
        dis2.grid(row=2, column=1, padx=20, pady=10, sticky=W)

        log = Button(self.root, text='Войти', font=("Arial", 14), bg="#EDC7B7", command=self.login, width=10)
        log.grid(row=3, column=0, columnspan=2, pady=20)

        reg = Button(self.root, text='Зарегистрироваться', font=("Arial", 14), bg="#EDC7B7",
                     command=self.registrationScreen,
                     fg="blue", relief="flat")
        reg.grid(row=4, column=0, columnspan=2, pady=10)

    def registrationScreen(self):
        self.root.geometry('600x400')
        self.clear_window()
        reglb = Label(self.root, text='Регистрация', font=("Arial", 20, 'bold'), bg="#EDC7B7")
        reglb.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        pass_req_label = Label(self.root,
                               text="*Пароль должен содержать минимум 6 символов,\n2 цифры и только латинские буквы.",
                               font=("Arial", 10), fg="red", bg="#EDC7B7")
        pass_req_label.grid(row=3, column=1, columnspan=2, padx=20, pady=(0, 10))

        nicklb = Label(self.root, text='Имя пользователя:', font=("Arial", 14), bg="#EDC7B7")
        nicklb.grid(row=1, column=0, padx=20, sticky=E)

        dis1 = Entry(self.root, textvariable=self.regUserName, font=("Arial", 14), width=20,
                     borderwidth=2, relief="solid")
        dis1.grid(row=1, column=1, padx=20, pady=10, sticky=W)

        pas1lb = Label(self.root, text='Пароль:', font=("Arial", 14), bg="#EDC7B7")
        pas1lb.grid(row=2, column=0, padx=20, sticky=E)

        dis2 = Entry(self.root, textvariable=self.regPassword, font=("Arial", 14), width=20,
                     borderwidth=2, relief="solid", show="*")
        dis2.grid(row=2, column=1, padx=20, pady=10, sticky=W)

        pas2lb = Label(self.root, text='Подтвердите пароль:', font=("Arial", 14), bg="#EDC7B7")
        pas2lb.grid(row=4, column=0, padx=20, sticky=E)

        dis3 = Entry(self.root, textvariable=self.regPasswordCheck, font=("Arial", 14), width=20,
                     borderwidth=2, relief="solid", show="*")
        dis3.grid(row=4, column=1, padx=20, pady=10, sticky=W)

        regbtn = Button(self.root, text='Зарегистрироваться', bg="#EDC7B7", font=("Arial", 14), command=self.register,
                        width=15)
        regbtn.grid(row=5, column=0, columnspan=2, pady=15)

        log = Button(self.root, text='Войти', font=("Arial", 14), bg="#EDC7B7", command=self.loginScreen, width=10)
        log.grid(row=6, column=0, columnspan=2)

    def display_discussion_screen(self):
        self.clear_window()
        self.root.geometry('720x700')
        self.root.resizable(False, False)
        self.root['bg'] = '#FAF0E6'

        header = Frame(self.root, bg='#EDC7B7', height=60)
        header.pack(fill="x")

        title = Label(header, text="Форум обсуждений", font=("Arial", 24, 'bold'), bg='#EDC7B7', fg='#FFFFFF')
        title.pack(pady=10, padx=20, side=LEFT)

        logout_btn = Button(header, text="Выход", font=("Arial", 12, 'bold'), bg='#FF5733', fg='black',
                            relief="solid", command=self.loginScreen)
        logout_btn.pack(pady=10, padx=20, side=RIGHT)

        content_frame = Frame(self.root, bg='#EDC7B7')
        content_frame.pack(expand=True, fill="both", padx=20, pady=20)

        disc1 = Button(content_frame, text='Фильм "Человек-паук"', font=("Arial", 16, 'bold'),
                       bg='#FAF0E6', fg='gray', relief="solid", height=3, command=lambda: self.chat_screen("Фильм 'Человек-паук'"))
        disc1.pack(fill="x", pady=15, padx=10)

        disc2 = Button(content_frame, text='Новости Питера', font=("Arial", 16, 'bold'),
                       bg='#FAF0E6', fg='gray', relief="solid", height=3, command=lambda: self.chat_screen("Новости Питера"))
        disc2.pack(fill="x", pady=15, padx=10)

        disc3 = Button(content_frame, text='IT-технологии', font=("Arial", 16, 'bold'),
                       bg='#FAF0E6', fg='gray', relief="solid", height=3, command=lambda: self.chat_screen("IT-технологии"))
        disc3.pack(fill="x", pady=15, padx=10)

        disc4 = Button(content_frame, text='Спортивные события', font=("Arial", 16, 'bold'),
                       bg='#FAF0E6', fg='gray', relief="solid", height=3, command=lambda: self.chat_screen("Спортивные события"))
        disc4.pack(fill="x", pady=15, padx=10)

        create_discussion_btn = Button(content_frame, text="Создать новое обсуждение", font=("Arial", 16, 'bold'),
                                       bg='#FFBD69', fg='blue', relief="solid", height=3,
                                       command=self.create_new_discussion)
        create_discussion_btn.pack(fill="x", pady=15, padx=10)

    def create_new_discussion(self):
        topic = askstring("Новое обсуждение", "Введите название для нового обсуждения:")
        if topic:
            self.chat_screen(topic)
        else:
            showerror("Ошибка", "Название обсуждения не может быть пустым.")

    def chat_screen(self, topic):
        self.clear_window()
        header = Frame(self.root, bg='#EDC7B7', height=60)
        header.pack(fill="x")

        title = Label(header, text=topic, font=("Arial", 24, 'bold'), bg='#EDC7B7', fg='#FFFFFF')
        title.pack(pady=10, padx=20, side=RIGHT)

        back_button = Button(header, text="←", font=("Arial", 14), command=self.display_discussion_screen)
        back_button.pack(side=LEFT, padx=10, pady=10)

        self.canvas = Canvas(self.root)
        chat_frame = Frame(self.canvas, bg='#EDC7B7')
        chat_scrollbar = Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=chat_scrollbar.set)
        self.canvas.yview_moveto(0.0)

        chat_scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=chat_frame, anchor="nw")

        chat_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        chat_history = self.load_chat_history(topic)
        if chat_history:
            for post in chat_history:
                message = f"{post.author} ({post.time}): {post.text}"
                self.disp_message(chat_frame, message, post, topic)

        dis = StringVar()
        field_frame = Frame(self.root, bg='#EDC7B7')
        field = Entry(field_frame, textvariable=dis, width=45)
        field.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        field.bind("<Return>", lambda event: self.send_message(chat_frame, field, topic))

        send_button = Button(field_frame, text="Отправить", command=lambda: self.send_message(chat_frame, field, topic),
                             font=(None, 10), width=15)
        send_button.pack(side="right")

        field_frame.pack(side="bottom", fill="x")

    def login(self):
        users = User.load_users()
        username = self.logUserName.get()
        password = self.logPassword.get()

        if username not in users:
            showerror('Ошибка входа', 'Пользователь не найден.')
            return

        user = users[username]
        if user.check_password(password):
            global current_user
            current_user = user
            self.display_discussion_screen()
        else:
            showerror('Ошибка входа', 'Неверный пароль.')

    def register(self):
        username = self.regUserName.get()
        password = self.regPassword.get()
        password_check = self.regPasswordCheck.get()

        if len(password) < 6:
            showerror('Ошибка регистрации', 'Пароль должен содержать минимум 6 символов.')

        if len(re.findall(r'\d', password)) < 2:
            showerror('Ошибка регистрации', 'Пароль должен содержать минимум 2 цифры.')
            return

        if not re.match(r'^[a-zA-Z0-9]+$', password):
            showerror('Ошибка регистрации', 'Пароль должен содержать только латинские буквы и цифры.')
            return

        if password != password_check:
            showerror('Ошибка регистрации', 'Пароли не совпадают.')
            return

        users = User.load_users()
        if username in users:
            showerror('Ошибка регистрации', 'Пользователь уже существует.')
            return

        password_hash = User.hash_password(password)
        User.save_user(username, password_hash, 0)
        showinfo('Успешная регистрация', 'Регистрация прошла успешно!')
        self.loginScreen()

    def send_message(self, chat_frame, field, topic):
        text = field.get().strip()
        if not text:
            showerror('Ошибка', 'Сообщение не может быть пустым.')
            return
        post = Post(current_user.username, text, self)

        self.disp_message(chat_frame, f"{post.author} ({post.time}): {post.text}", post)
        field.delete(0, END)

        self.save_message(post, topic)

        chat_frame.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def disp_message(self, chat_frame, message, post=None, topic=None):
        msg_frame = Frame(chat_frame, bd=2, relief="solid", padx=5, pady=5, bg='#FAF0E6')
        msg_frame.pack(fill=X, padx=10, pady=5)

        author_time, text = message.split("):", 1)
        author, time = author_time.split("(", 1)
        author, time = author.strip(), time.strip()

        user_label = Label(msg_frame, text=author, font=("Arial", 12, 'bold'), anchor="w", fg='black', bg='#FAF0E6')
        user_label.pack(anchor="nw")

        message_label = Label(msg_frame, text=text, font=("Arial", 16), anchor="w", width=55, justify="left",
                              wraplength=500, fg='black', bg='#FAF0E6')
        message_label.pack(anchor="nw", pady=(5, 0))

        time_label = Label(msg_frame, text=time, font=("Arial", 10), anchor="e", fg='black', bg='#FAF0E6')
        time_label.pack(anchor="sw", pady=(5, 0))

        like_frame = Frame(msg_frame, bg='#FAF0E6')
        like_frame.pack(anchor='e')

        if post:
            like_count_var = IntVar(value=post.likes)

            def toggle_like():
                if current_user:
                    post.toggle_like(current_user, topic)
                    like_count_var.set(post.likes)

            like_button = Button(like_frame, text="❤️", command=toggle_like, bg="#FF9999", relief="solid",
                                 font=("Arial", 12))
            like_button.pack(side=LEFT)

            like_count_label = Label(like_frame, textvariable=like_count_var, font=("Arial", 12), bg='#FAF0E6',
                                     fg='black')
            like_count_label.pack(side=LEFT, padx=(5, 0))

        chat_frame.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


root = Tk()
app = MessengerApp(root)
root.mainloop()
