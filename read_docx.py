import docx

def extract_docx(file_path, output_path):
    doc = docx.Document(file_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        for p in doc.paragraphs:
            if p.text.strip():
                f.write(p.text + '\n')
                
extract_docx(r'C:\Users\Udai Ratinam G\Downloads\QML Project\Sample Project Report_ Research Based Project.docx', 'sample_report_utf8.txt')
extract_docx(r'C:\Users\Udai Ratinam G\Downloads\QML Project\Table of Contents - Product Based.docx', 'toc_product.txt')
extract_docx(r'C:\Users\Udai Ratinam G\Downloads\QML Project\Table of Contents_ Research Project.docx', 'toc_research.txt')
extract_docx(r'C:\Users\Udai Ratinam G\Downloads\QML Project\B657.docx', 'b657_report.txt')
