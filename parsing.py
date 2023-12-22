from jinja2 import Template
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerEmpty

from config import phone, api_id, api_hash



client = TelegramClient(phone, api_id, api_hash)

client.start()

chats = []
last_date = None
size_chats = 1000
groups = []

result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=size_chats,
    hash=0
))
chats.extend(result.chats)

for chat in chats:
    try:
        if chat.megagroup:
            groups.append(chat)
    except Exception as e:
        continue

print("Выберите из списка номер группы: ")

i = 0
for group in groups:
    print(str(i) + " - " + group.title)
    i += 1

group_index = int(input("Введите нужную цифру: "))
target_group = groups[group_index]

print("Считываем пользователей...")
full_name_participants = []
all_participants = client.get_participants(target_group)

for user in all_participants:
    if user.username:
        username = user.username
    else:
        username = ""
    if user.first_name:
        first_name = user.first_name
    else:
        first_name = ""
    if user.last_name:
        last_name = user.last_name
    else:
        last_name = ""
    name = (first_name + " " + last_name).strip()
    full_name_participants.append([username, name, target_group.title])

print("Записываем данные в файл...")

template = Template(
    """
    <table style="border:2px black solid">
        <tr>
            {% for name in full_name_participants %}
                <td>{{ name }}</td>          
        </tr>
            {% endfor %}        
    </table>
    """
)

with open("participants.html", "w", encoding="utf-8") as f:
    f.write(template.render(full_name_participants=full_name_participants))

print("Парсинг участников группы выполнен успешно.")

all_messages = []
offset_id = 0
limit = 1000
total_messages = 0
total_count_limit = 0

while True:
    history = client(GetHistoryRequest(
        peer=target_group,
        offset_id=offset_id,
        offset_date=None,
        add_offset=0,
        limit=limit,
        max_id=0,
        min_id=0,
        hash=0
    ))
    if not history.messages:
        break
    messages = history.messages

    for message in messages:
        all_messages.append(message.message)

    offset_id = messages[len(messages) - 1].id
    total_messages = len(all_messages)
    if total_count_limit != 0 and total_messages >= total_count_limit:
        break

print("Сохраняем данные в файл...")

template = Template(
    """
    <table style="border:2px black solid">
        <tr>
            {% for message in all_messages %}
                <td>{{ message }}</td>                
        </tr>        
            {% endfor %}
        <br>
    </table>
    """
)

with open("chats.html", "w", encoding="utf-8") as f:
    f.write(template.render(all_messages=all_messages))

print("Парсинг сообщений группы выполнен успешно.")


