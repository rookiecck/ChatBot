import tkinter as tk
from tkinter import filedialog, messagebox
import openai
import pdfplumber
import docx

# Set your OpenAI API key
openai.api_base = "https://api.chatanywhere.com.cn/v1"
openai.api_key = 'sk-VijoLt7xC9eL5VGJCEXDq47s8BUUt3K4xR3nEOv5yKMhGc9t'

file_path = ""
output_path = ""

# Function to extract text from a PDF file
def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to extract text from a Word document
def extract_text_from_word(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

# Function to extract text from a code file
def extract_text_from_code(file_path):
    with open(file_path, "r") as f:
        text = f.read()
    return text

def extract_text_from_txt(file_path):
    with open(file_path, "r") as f:
        text = f.read()
    return text

# Function to analyze document using OpenAI Chat API
#"请给我提供对于这段代码中功能的测试用例，包含输入和预期的输出结果，要求语句覆盖率分支覆盖率和MC/DC覆盖率达到100%,去除重复的测试用例"
def analyze_document(system_message, document, custom_message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": document},
            {"role": "user", "content": custom_message}  # Add the custom message as a user role message
        ],
        max_tokens=4096,
        n=1,
        stop=None,
        temperature=0.7
    )
    analysis = response.choices[0].message['content']
    return analysis

# Function to perform analysis and save results to a file
def perform_analysis():
    global file_path, output_path

    if not file_path or not output_path:
        messagebox.showerror("错误", "请选择输入文件和输出路径")
        return

        # Determine the file type based on the extension
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
    document_segments = [document_text[i:i+4096] for i in range(0, len(document_text), 4096)]

    analysis_results = []
    for segment in document_segments:
        response = analyze_document(system_message_entry.get(), segment, message_entry.get())  # Pass the custom message as an argument
        analysis_result = response
        analysis_results.append(analysis_result)

    functional_modules = "\n".join(analysis_results)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(functional_modules)

    messagebox.showinfo("分析完成", "分析结果已保存到文件:\n" + output_path)

# Function to handle GUI button click event for selecting PDF file
def select_file():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Word documents", "*.docx *.doc"), ("Code files", "*.c *.cpp"), ("Text files", "*.txt")])
    if file_path:
        messagebox.showinfo("选择成功", "已选择输入文件:\n" + file_path)

# Function to handle GUI button click event for selecting output text file
def select_output_file():
    global output_path
    output_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if output_path:
        messagebox.showinfo("选择成功", "已选择输出文件:\n" + output_path)

# Create the main GUI window
root = tk.Tk()
root.title("PDF Analysis Tool")

# Create and place GUI widgets
pdf_button = tk.Button(root, text="选择文件", command=select_file)
pdf_button.pack(pady=10)

output_button = tk.Button(root, text="选择输出文件", command=select_output_file)
output_button.pack(pady=10)

system_message_label = tk.Label(root, text="自定义系统消息:")
system_message_label.pack()

system_message_entry = tk.Entry(root, width=50)
system_message_entry.pack(pady=10)

message_label = tk.Label(root, text="自定义消息:")
message_label.pack()

message_entry = tk.Entry(root, width=50)
message_entry.pack(pady=10)

start_button = tk.Button(root, text="开始分析", command=perform_analysis)
start_button.pack(pady=20)

exit_button = tk.Button(root, text="退出", command=root.quit)
exit_button.pack()

# Start the GUI event loop
root.mainloop()