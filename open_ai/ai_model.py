import openai
import tempfile
import os
import subprocess
import re

openai.api_key = ''

def analyze_code_with_ai(code, language='python'):
    if language == 'python':
        execution_feedback, error_count = run_python_execution(code)
        fixed_code = get_gpt_suggestions(code, language)
        fixed_code = extract_code_block(fixed_code)
        fixed_code_feedback, fixed_error_count = run_python_execution(fixed_code)
        score = 100 - error_count
        fixed_score = 100 - fixed_error_count
        return {
            'execution_feedback': execution_feedback,
            'fixed_code': fixed_code,
            'fixed_code_feedback': fixed_code_feedback,
            'score': score,
            'fixed_score': fixed_score
        }
    elif language == 'javascript':
        execution_feedback, error_count = run_javascript_execution(code)
        fixed_code = get_gpt_suggestions(code, language)
        fixed_code = extract_code_block(fixed_code)
        fixed_code_feedback, fixed_error_count = run_javascript_execution(fixed_code)
        score = 100 - error_count
        fixed_score = 100 - fixed_error_count
        return {
            'execution_feedback': execution_feedback,
            'fixed_code': fixed_code,
            'fixed_code_feedback': fixed_code_feedback,
            'score': score,
            'fixed_score': fixed_score
        }
    elif language == 'java':
        execution_feedback, error_count = run_java_execution(code)
        fixed_code = get_gpt_suggestions(code, language)
        fixed_code = extract_code_block(fixed_code)
        fixed_code = ensure_main_class_name(fixed_code)  # 클래스 이름을 Main으로 변경
        fixed_code_feedback, fixed_error_count = run_java_execution(fixed_code)
        score = 100 - error_count
        fixed_score = 100 - fixed_error_count
        return {
            'execution_feedback': execution_feedback,
            'fixed_code': fixed_code,
            'fixed_code_feedback': fixed_code_feedback,
            'score': score,
            'fixed_score': fixed_score
        }
    else:
        return {'error': f'Unsupported language: {language}'}

def run_python_execution(code):
    temp_code_file = None
    error_count = 0
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w', encoding='utf-8') as temp_code_file:
            temp_code_file.write(code)
            temp_code_file.flush()
        process = subprocess.Popen(
            ['python', temp_code_file.name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8',
            errors='ignore'
        )
        stdout, stderr = process.communicate()
        error_count = stderr.count('\n') if stderr else 0
        if process.returncode == 0:
            feedback = f"코드가 성공적으로 작성되었습니다.\n\n결과:\n\n{stdout or 'No output'}"
        else:
            feedback = f"코드에 오류가 있습니다.\n\nError:\n\n{stderr or 'No error message'}"
        return feedback, error_count
    except Exception as e:
        return str(e), error_count
    finally:
        if temp_code_file:
            os.remove(temp_code_file.name)

def run_javascript_execution(code):
    temp_code_file = None
    error_count = 0
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".js", mode='w', encoding='utf-8') as temp_code_file:
            temp_code_file.write(code)
            temp_code_file.flush()
        process = subprocess.Popen(
            ['node', temp_code_file.name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8',
            errors='ignore'
        )
        stdout, stderr = process.communicate()
        error_count = stderr.count('\n') if stderr else 0
        if process.returncode == 0:
            feedback = f"코드가 성공적으로 작성되었습니다.\n\n결과:\n\n{stdout or 'No output'}"
        else:
            feedback = f"코드에 오류가 있습니다.\n\nError:\n\n{stderr or 'No error message'}"
        return feedback, error_count
    except Exception as e:
        return str(e), error_count
    finally:
        if temp_code_file:
            os.remove(temp_code_file.name)

def run_java_execution(code):
    temp_code_file = None
    error_count = 0
    try:
        temp_code_file = './temp/Main.java'
        with open(temp_code_file, 'w', encoding='utf-8') as f:
            f.write(code)
        compile_result = subprocess.run(
            ['javac', '-encoding', 'UTF-8', temp_code_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        error_count = compile_result.stderr.count('\n') if compile_result.stderr else 0
        if compile_result.returncode != 0:
            return f"코드 컴파일에 실패했습니다.\nError:\n{compile_result.stderr or 'Unknown compilation error'}", error_count
        process = subprocess.Popen(
            ['java', '-Dfile.encoding=UTF-8', '-cp', './temp', 'Main'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore',
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        error_count += stderr.count('\n') if stderr else 0
        if process.returncode == 0:
            feedback = f"코드가 성공적으로 작성되었습니다.\n\n결과:\n\n{stdout or 'Code executed without output'}"
        else:
            feedback = f"코드에 오류가 있습니다.\n\nError:\n\n{stderr or 'Unknown execution error'}"
        return feedback, error_count
    except Exception as e:
        return str(e), error_count
    finally:
        if temp_code_file and os.path.exists(temp_code_file):
            os.remove(temp_code_file)
        class_file = temp_code_file.replace('.java', '.class')
        if os.path.exists(class_file):
            os.remove(class_file)

def get_gpt_suggestions(code, language):
    try:
        prompt = f"Here is some {language} code that needs improvements:\n\n{code}\n\nCan you suggest improvements and provide the modified code?"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )
        suggestions = response.choices[0].message['content'].strip()
        return suggestions
    except Exception as e:
        return f"Error getting suggestions from GPT-3.5: {e}"

def extract_code_block(text):
    code_block = re.search(r'```(?:java|python|javascript)?\n(.*?)```', text, re.DOTALL)
    if code_block:
        return code_block.group(1)
    return text

def ensure_main_class_name(code):
    # 클래스 이름을 Main으로 변경
    return re.sub(r'\bpublic\s+class\s+\w+', 'public class Main', code)
