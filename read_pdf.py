import openai
import pdfplumber
import os
openai.api_base = "https://api.chatanywhere.com.cn/v1"
def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

openai.api_key = 'sk-VijoLt7xC9eL5VGJCEXDq47s8BUUt3K4xR3nEOv5yKMhGc9t'

def analyze_document(document):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "请给我提供对于这段代码中功能的测试用例，包含输入和预期的输出结果，要求语句覆盖率分支覆盖率和MC/DC覆盖率达到100%,去除重复的测试用例"},
            {"role": "user", "content": document}
        ],
        max_tokens=4096,
        n=1,
        stop=None,
        temperature=0.7
    )
    analysis = response.choices[0].message['content']
    return analysis

# 读取PDF文档内容
pdf_file = "D:\pythonspace\chatgpt\is_val_in_range.pdf"
document_text = extract_text_from_pdf(pdf_file)

# 将文档内容分段
document_segments = [document_text[i:i+4096] for i in range(0, len(document_text), 4096)]

# 分别分析每个文档段落
analysis_results = []
for segment in document_segments:
    analysis_result = analyze_document(segment)
    analysis_results.append(analysis_result)

# 解析分析结果，获取功能模块
functional_modules = ""
for result in analysis_results:
    functional_modules += result + "\n"

# print("功能模块:")
# print(functional_modules)

# 保存分析结果到txt文件
output_file = "D:/pythonspace/chatgpt/output.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(functional_modules)

print("分析结果已保存到文件:", output_file)

