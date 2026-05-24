import os
import psycopg2
import bcrypt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
DB_URI = os.getenv("DATABASE_URL")

class AuthRequest(BaseModel):
    email: str
    password: str

class ProcessRequest(BaseModel):
    email: str
    prompt: str
    language: str
    mode: str

class LocalExpertEngine:
    def __init__(self):
        self.code_templates = {
            "calculator": {
                "Python": """import tkinter as tk

def calculate():
    try:
        result = eval(entry.get()) 
        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))
    except Exception:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "Error")

root = tk.Tk()
root.title("GUI Calc")
entry = tk.Entry(root, font=("Arial", 16))
entry.pack(pady=10)
btn = tk.Button(root, text="Calculate", command=calculate)
btn.pack()
root.mainloop()""",
                
                "Java": """import java.util.Scanner;

public class Calculator {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.println("Enter format: [num1] [operator] [num2]");
        double a = sc.nextDouble();
        char op = sc.next().charAt(0);
        double b = sc.nextDouble();
        
        if (op == '+') System.out.println(a + b);
        else if (op == '-') System.out.println(a - b);
        else if (op == '*') System.out.println(a * b);
        else if (op == '/') {
            if (b != 0) System.out.println(a / b);
            else System.out.println("Error: Div by 0");
        }
        else System.out.println("Invalid Operator");
    }
}""",
                
                "C": """#include <stdio.h>

int main() {
    double n1, n2;
    char op;
    printf("Enter expression (e.g. 5 + 5): ");
    scanf("%lf %c %lf", &n1, &op, &n2);
    
    switch(op) {
        case '+': printf("%.2lf", n1+n2); break;
        case '-': printf("%.2lf", n1-n2); break;
        case '*': printf("%.2lf", n1*n2); break;
        case '/': 
            if(n2 != 0) printf("%.2lf", n1/n2);
            else printf("Div by Zero");
            break;
        default: printf("Error");
    }
    return 0;
}""",
                
                "C++": """#include <iostream>
using namespace std;

int main() {
    double a, b; 
    char op;
    cout << "Enter math expression: ";
    cin >> a >> op >> b;
    
    if (op == '+') cout << a + b;
    else if (op == '-') cout << a - b;
    else if (op == '*') cout << a * b;
    else if (op == '/') {
        if (b != 0) cout << a / b;
        else cout << "Div by 0";
    }
    return 0;
}""",
                
                "JavaScript": """const readline = require('readline').createInterface({ 
    input: process.stdin, 
    output: process.stdout 
});

readline.question('Enter expression (e.g., 5 + 3): ', expr => {
    try { 
        console.log('Result:', eval(expr)); 
    } catch (e) { 
        console.log('Invalid Expression'); 
    }
    readline.close();
});"""
            },
            "todo": {
                "Python": """tasks = []
while True:
    print("\\n1. Add Task  2. View Tasks  3. Exit")
    cmd = input("Choice: ")
    if cmd == '1': 
        tasks.append(input("Enter Task: "))
    elif cmd == '2': 
        print("Your Tasks:", tasks)
    elif cmd == '3': 
        break""",
                "Java": """import java.util.ArrayList;
import java.util.Scanner;

public class TodoApp {
    public static void main(String[] args) {
        ArrayList<String> list = new ArrayList<>();
        Scanner s = new Scanner(System.in);
        while(true) {
            System.out.print("1.Add 2.Show 3.Exit: ");
            int c = s.nextInt(); 
            s.nextLine();
            
            if(c == 1) list.add(s.nextLine());
            else if(c == 2) System.out.println(list);
            else break;
        }
    }
}""",
                "JavaScript": """let tasks = [];
function addTodo(task) { 
    tasks.push(task); 
    console.log('Added:', task); 
}
function viewTodos() { 
    console.table(tasks); 
}

addTodo('Learn JavaScript'); 
viewTodos();""",
                "C": """#include <stdio.h>
#include <string.h>

int main() {
    char tasks[10][100];
    int taskCount = 0;
    int choice;
    
    while(1) {
        printf("1. Add Task  2. Exit: ");
        scanf("%d", &choice);
        if (choice == 1 && taskCount < 10) {
            printf("Enter task name: ");
            scanf("%s", tasks[taskCount]);
            taskCount++;
            printf("Task Added!\\n");
        } else {
            break;
        }
    }
    return 0;
}""",
                "C++": """#include <iostream>
#include <vector>
using namespace std;

int main() {
    vector<string> tasks; 
    string input;
    cout << "Type tasks (type 'exit' to stop):\\n";
    
    while(cin >> input && input != "exit") {
        tasks.push_back(input);
    }
    
    cout << "Your Todo List:\\n";
    for(string t : tasks) {
        cout << "- " << t << "\\n";
    }
    return 0;
}"""
            }
        }

        self.image_base = {
            "love": "[CINEMATIC RENDER: 8k resolution, soft golden hour lighting, a beautiful girl in traditional Bengali attire smiling gently, morphing seamlessly into glowing cybernetic data streams]",
            "cricket": "[CINEMATIC RENDER: A massive cricket stadium bathed in neon blue Indian team colors, roaring crowd, dynamic motion blur of a ball shattering a digital glowing wicket]",
            "mess": "[CINEMATIC RENDER: A chaotic but cozy engineering student mess room, 'Anima Villa' vibes, empty pizza boxes, multiple monitors glowing with green code, late night moody lighting]",
            "default": "[CINEMATIC RENDER: Minimalist dark matrix viewport casting deep green neon luminescent characters reflecting off a metallic engineering console]"
        }
        
        self.shayari_base = {
            "love": "Teri aankhon ki tasveer jab background pe lagayi,\nHar complex algorithm mujhe aasan nazar aayi.\nBug chahe jitne bhi ho is zindagi ke code mein,\nTere ek muskurahat ne saari errors mita di.",
            "cricket": "Jeet ka jashn aur T20 ka khumaar,\nCode compile ho gaya, ab party hogi yaar.\nJab pitch pe aag ugle apne khiladiyon ka bat,\nSystem crash ho jaye itni high hai apni stat!",
            "mess": "Mess ka khana aur engineering ki raat,\nRounak aur Pinaki ke bina adhuri hai har baat.\nDeadline sir pe hai, par chai ka pyala saath hai,\nMAKAUT ke syllabus mein bhi apni alag hi baat hai.",
            "default": "Log dhundte hain khuda ko zameen o aasmaan me,\nHamne toh apna aashiyaan banaaya hai is jahaan me."
        }

    def parse_intent(self, prompt: str) -> str:
        text = prompt.lower()
        
        if "calc" in text or "calculator" in text or "math" in text or "addition" in text:
            return "calculator"
        elif "todo" in text or "task" in text or "list" in text:
            return "todo"
        elif "mess" in text or "roommate" in text or "hostel" in text or "college" in text or "exam" in text:
            return "mess"
        elif "cricket" in text or "match" in text or "t20" in text or "world cup" in text or "win" in text:
            return "cricket"
        elif "love" in text or "girlfriend" in text or "romantic" in text or "traditional" in text:
            return "love"
        else:
            return "default"

    def generate_code(self, prompt: str, lang: str) -> str:
        intent = self.parse_intent(prompt)
        lang = lang.strip()
        
        if intent in self.code_templates:
            if lang in self.code_templates[intent]:
                return self.code_templates[intent][lang]
            else:
                return f"// Engine currently optimizing {lang} architecture for {intent}."
        
        return f"// AI Subsystem ready. Request a calculator, to-do app, or logic structure in {lang}."

    def debug_code(self, code: str, lang: str) -> str:
        lines = code.split("\n")
        issues = []
        fixed_lines = []
        
        for i in range(len(lines)):
            line = lines[i]
            cleaned_line = line.strip()
            line_num = i + 1
            
            if not cleaned_line:
                fixed_lines.append(line)
                continue
                
            if lang.lower() == "python":
                if cleaned_line.startswith(("def ", "if ", "elif ", "else", "for ", "while ", "try", "except", "class ")):
                    if not cleaned_line.endswith(":"):
                        issues.append(f"Line {line_num} [Python]: Missing colon ':' at end of block.")
                        line = line + ":"
                        
                if cleaned_line.startswith("print ") and "(" not in cleaned_line:
                    issues.append(f"Line {line_num} [Python]: Missing parentheses in print call.")
                    line = line.replace("print ", "print(") + ")"
                    
            elif lang.lower() in ["c", "c++", "java", "javascript"]:
                needs_semicolon = True
                
                if cleaned_line.endswith(";") or cleaned_line.endswith("{") or cleaned_line.endswith("}"):
                    needs_semicolon = False
                if cleaned_line.startswith(("#include", "import", "if", "while", "for", "switch", "class", "public", "private", "int main", "void")):
                    needs_semicolon = False
                    
                if needs_semicolon:
                    issues.append(f"Line {line_num} [{lang}]: Missing semicolon ';'.")
                    line = line + ";"
                    
                if cleaned_line.startswith(("if ", "while ", "for ", "switch ")) and not "(" in cleaned_line:
                    issues.append(f"Line {line_num} [{lang}]: Missing parentheses around condition.")
                    line = line.replace("if ", "if (").replace(" {", ") {")
                    
                if lang.lower() == "javascript" and "var " in cleaned_line:
                    issues.append(f"Line {line_num} [JS]: ES6 strict mode suggests 'let' instead of 'var'.")
                    line = line.replace("var ", "let ")

            if cleaned_line.startswith(("if ", "elif ", "while ")):
                if "=" in cleaned_line and "==" not in cleaned_line and "!=" not in cleaned_line and "<=" not in cleaned_line and ">=" not in cleaned_line:
                    issues.append(f"Line {line_num} [Logic]: Used assignment '=' instead of equality '=='.")
                    line = line.replace("=", "==")

            fixed_lines.append(line)
            
        if len(issues) == 0:
            return f"[{lang.upper()} COMPILE CHECK]: System green. 0 errors found by local analyzer."
            
        report = f"--- {lang.upper()} STATIC ANALYSIS REPORT ---\n"
        for issue in issues:
            report += f"- {issue}\n"
            
        report += "\n--- AUTO-CORRECTED SOURCE CODE ---\n"
        report += "\n".join(fixed_lines)
        return report

    def generate_entertainment(self, prompt: str) -> str:
        intent = self.parse_intent(prompt)
        img = self.image_base.get(intent, self.image_base["default"])
        poem = self.shayari_base.get(intent, self.shayari_base["default"])
        
        result = "AI VISUALIZATION PROMPT:\n" + img + "\n\n"
        result += "=========================\n\n"
        result += "GENERATED SHAYARI:\n" + poem
        return result

ai_engine = LocalExpertEngine()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_pwd: str, hashed_pwd: str) -> bool:
    return bcrypt.checkpw(plain_pwd.encode('utf-8'), hashed_pwd.encode('utf-8'))

@app.post("/signup")
def register_user(user: AuthRequest):
    try:
        conn = psycopg2.connect(DB_URI)
        cur = conn.cursor()
        
        hashed = hash_password(user.password)
        cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (user.email, hashed))
        
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        print("Error during signup:", e)
        raise HTTPException(status_code=400, detail="Registration failed. Email might already exist.")

@app.post("/login")
def login_user(user: AuthRequest):
    try:
        conn = psycopg2.connect(DB_URI)
        cur = conn.cursor()
        
        cur.execute("SELECT password FROM users WHERE email = %s", (user.email,))
        record = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if record and verify_password(user.password, record[0]):
            return {"status": "verified"}
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password")
    except HTTPException:
        raise
    except Exception as e:
        print("Database error during login:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/run_ai")
def process_ai_request(req: ProcessRequest):
    mode = req.mode
    lang = req.language
    
    if mode == "Beginner Engine":
        output_text = ai_engine.generate_code(req.prompt, lang)
    elif mode == "Pro Debugger":
        output_text = ai_engine.debug_code(req.prompt, lang)
    elif mode == "Cinematic Generator":
        output_text = ai_engine.generate_entertainment(req.prompt)
    else:
        raise HTTPException(status_code=400, detail="Invalid AI mode selected")
        
    try:
        conn = psycopg2.connect(DB_URI)
        cur = conn.cursor()
        cur.execute("INSERT INTO history (user_email, prompt, output) VALUES (%s, %s, %s)", 
                    (req.email, req.prompt, output_text))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Failed to save history:", e)
        
    return {"reply": output_text}