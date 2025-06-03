import tkinter as tk
from tkinter import scrolledtext

import openai

# Set up OpenAI API key
openai.api_base = "https://api.chatanywhere.com.cn/v1"
openai.api_key = 'OPENAI_API_KEY'


# Function to send a message to the OpenAI chatbot model and return its response
def send_message(message_log):
    # Use OpenAI's ChatCompletion API to get the chatbot's response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_log,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Find the first response from the chatbot that has text in it (some responses may not have text)
    for choice in response.choices:
        if "text" in choice:
            return choice.text

    # If no response with text is found, return the first response's content (which may be empty)
    return response.choices[0].message.content

    

# Function to handle user input and update the conversation log
def handle_user_input():
    user_input = user_entry.get()
    user_entry.delete(0, tk.END)

    if user_input.lower() == "关掉吧":
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, "下次使用时，叫我的名字就可以把我唤醒，再见!\n")
        chat_log.config(state=tk.DISABLED)
        user_entry.config(state=tk.DISABLED)
        send_button.config(state=tk.DISABLED)
        return

    message_log.append({"role": "user", "content": user_input})
    response = send_message(message_log)
    message_log.append({"role": "assistant", "content": response})

    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, f"用户: {user_input}\n")
    chat_log.insert(tk.END, f"Neko: {response}\n")
    chat_log.config(state=tk.DISABLED)


# Create the main window
window = tk.Tk()
window.title("Chatbot")

# Create a scrolled text widget to display the conversation log
chat_log = scrolledtext.ScrolledText(window, state=tk.DISABLED)
chat_log.pack(fill=tk.BOTH, expand=True)

# Create an entry widget for user input
user_entry = tk.Entry(window)
user_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Create a button to send user input
send_button = tk.Button(window, text="发送", command=handle_user_input)
send_button.pack(side=tk.RIGHT)

# Initialize the conversation history with a message from the chatbot
message_log = [
    {"role": "system", "content": "You are a cute boy named Neko."}
]

# Start the Tkinter event loop
window.mainloop()
