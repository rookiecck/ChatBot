import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import pdfplumber
import docx
import openai
import datetime
import os

# 设置OpenAI API密钥
openai.api_base = "https://api.chatanywhere.com.cn/v1"
openai.api_key = 'OPENAI_API_KEY'

file_path = ""
output_path = ""
# 获取当前时间
current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# massage_log的保存路径
log_dir = './log'
# 从PDF文件中提取文本
def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# 从Word文档中提取文本
def extract_text_from_word(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

# 从代码文件中提取文本
def extract_text_from_code(file_path):
    with open(file_path, "r") as f:
        text = f.read()
    return text
# 从txt文档中提取文本
def extract_text_from_txt(file_path):
    with open(file_path, "r") as f:
        text = f.read()
    return text

# 函数向OpenAI模型发送消息并返回其响应
def send_message(message_log):
    # 调用ChatGPT的API接口
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # 选择模型
        messages=message_log,   # 输入的问题
        n=1,    # 产生结果的个数
        stop=None,  # 最多4个序列，API将停止生成更多tokens
        temperature=0.7,    # 数字0~2之间;数字越大，答案越随机，开放，比如1.8;数字越小，答案越固定，聚焦，比如0.2
        max_tokens=4096,    # 结果最大能产生的tokens数，默认可以返回 4096-输入tokens
    )

    # 从响应内容中找到包含文本的第一个响应(有些响应可能没有文本)
    for choice in response.choices:
        if "text" in choice:
            return choice.text

    # 如果没有找到带文本的响应，则返回第一个响应的内容(可能为空)
    return response.choices[0].message.content

# 将选择的输入文件的内容发送给ChatGPT
def perform_analysis():
    global file_path, output_path, message_log, functional_modules, handle_user_input_called, log_file

    # # 清空message_log
    # message_log = []

    # 当再次调用开始分析功能时将返回结果作为第一次输出结果
    handle_user_input_called = False
    # 判断是否选择了输入和输出文件
    if not file_path or not output_path:
        messagebox.showerror("错误", "请选择输入文件和输出路径")
        return

    # 根据扩展名确定文件类型
    file_extension = file_path.split(".")[-1].lower()

    if file_extension == "pdf":
        document_text = extract_text_from_pdf(file_path)
    elif file_extension in ["docx", "doc"]:
        document_text = extract_text_from_word(file_path)
    elif file_extension in ["c", "cpp"]:
        document_text = extract_text_from_code(file_path)
    elif file_extension == "txt":
        document_text = extract_text_from_txt(file_path)
    else:
        messagebox.showerror("错误", "不支持的文件类型")
        return
    # 将文本内容切割为长度为4096的片段
    document_segments = [document_text[i:i+4096] for i in range(0, len(document_text), 4096)]

    analysis_results = []
    # 调用API对输入文本进行分析并将结果保存到analysis_results中
    for segment in document_segments:
        message_log = [
            {"role": "system", "content": system_message_entry.get()},
            {"role": "user", "content": segment},
            {"role": "user", "content": message_entry.get()}
        ]
        response = send_message(message_log)  # 将自定义消息作为参数传递
        message_log.append({"role": "assistant", "content": response})
        log_file.append(message_log)    #将内容添加到日志
        analysis_result = response
        analysis_results.append(analysis_result)
    # 清空窗口内容
    chat_log.config(state=tk.NORMAL)
    chat_log.delete('1.0', tk.END)
    chat_log.config(state=tk.DISABLED)
    # 在窗口中显示生成的结果
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, f"ChatBot:\n {response}\n")
    chat_log.config(state=tk.DISABLED)
    # 将第一次分析的结果保存到functional_modules中等待被保存到文件
    functional_modules = "\n".join(analysis_results)
    return functional_modules

# 将最后一次的结果保存到输出文件中
def save_response():
    global handle_user_input_called
    # 判断是否为第一次分析的结果
    if handle_user_input_called == False:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(functional_modules)
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(last_response)
    messagebox.showinfo("保存成功", "最后一次分析结果已保存到文件:\n" + output_path)

# 当关闭窗口时自动保存日志
def on_closing():
    if messagebox.askokcancel("退出", "确定要退出吗?"):
        if not os.path.exists(log_dir):  # 如果不存在路径，则创建这个路径
            os.makedirs(log_dir)
        log_path = log_dir + '/' + current_time + 'message_log.txt'
        # 将消息日志保存
        with open(log_path, "w", encoding="utf-8") as f:
            log_file_str = "\n".join(str(entry) for entry in log_file)
            f.write(log_file_str)
        window.destroy()

# 在对话窗口中与ChatGPT继续提问
def handle_user_input():
    global last_response, handle_user_input_called, log_file
    user_input = user_entry.get()
    user_entry.delete(0, tk.END)
    # 将判断handle_user_input函数是否被调用的标志变量置为true
    handle_user_input_called = True
    # 将用户提问内容和回答保存到message_log中并输出在会话窗口中
    message_log.append({"role": "user", "content": user_input})
    response = send_message(message_log)
    message_log.append({"role": "assistant", "content": response})
    last_response = response
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, f"用户: {user_input}\n")
    chat_log.insert(tk.END, f"ChatBot:\n {response}\n")
    chat_log.config(state=tk.DISABLED)
    # 将内容添加到日志中
    log_file.append({"role": "user", "content": user_input})
    log_file.append({"role": "assistant", "content": response})
# 处理选择输入文件时GUI按钮单击事件的功能
def select_file():
    global file_path
    # file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Word documents", "*.docx *.doc"), ("Code files", "*.c *.cpp"), ("Text files", "*.txt")])
    file_path = filedialog.askopenfilename()
    if file_path:
        messagebox.showinfo("选择成功", "已选择输入文件:\n" + file_path)

# 处理选择输出文件时GUI按钮单击事件的功能
def select_output_file():
    global output_path
    output_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if output_path:
        messagebox.showinfo("选择成功", "已选择输出文件:\n" + output_path)
# 创建主窗口
window = tk.Tk()
window.title("ChatBot By changkai.chen")

# 创建和放置GUI小组件
# 输入文件按钮
input_button = tk.Button(window, text="选择输入文件", command=select_file)
input_button.grid(row=0, column=0, columnspan=4, pady=10)
# 输出文件按钮
output_button = tk.Button(window, text="选择输出文件", command=select_output_file)
output_button.grid(row=1, column=0, columnspan=4, pady=10)

# 自定义系统消息提示文本
system_message_label = tk.Label(window, text="自定义系统信息:")
system_message_label.grid(row=3, column=0, sticky=tk.E)
# 自定义系统消息文本框
system_message_entry = tk.Entry(window, width=50)
system_message_entry.grid(row=3, column=1, pady=10)

# 自定义消息提示文本
message_label = tk.Label(window, text="自定义用户信息:")
message_label.grid(row=4, column=0, sticky=tk.E)
# 自定义消息文本框
message_entry = tk.Entry(window, width=50)
message_entry.grid(row=4, column=1, pady=10)

# 开始分析按钮
start_button = tk.Button(window, text="开始分析", command=perform_analysis)
start_button.grid(row=3, column=3, rowspan=2, padx=20, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

# 输出最后一次回答按钮
outputToFile_button = tk.Button(window, text="输出本次回答", command=save_response)
outputToFile_button.grid(row=7, columnspan=4, pady=10)

# 创建一个滚动文本窗口来显示对话日志
chat_log = scrolledtext.ScrolledText(window, state=tk.DISABLED)
chat_log.grid(row=5, column=0, columnspan=4, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

# 为用户输入创建一个输入框
user_entry = tk.Entry(window)
user_entry.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

# 创建一个按钮来发送用户输入
send_button = tk.Button(window, text="发送", command=handle_user_input)
send_button.grid(row=6, column=3, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)


# 窗口关闭事件与on_closing函数关联
window.protocol("WM_DELETE_WINDOW", on_closing)
#判断handle_user_input函数是否被调用
handle_user_input_called = False
#log日志内容
log_file = []

# 启动Tkinter事件循环
window.mainloop()
