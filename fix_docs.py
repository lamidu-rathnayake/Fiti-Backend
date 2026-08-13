import os

f = "API_DOCUMENTATION.md"
if os.path.exists(f):
    with open(f,"r",encoding="utf-8") as file: 
        content = file.read()
    content = content.replace("seller","tailor").replace("Seller","Tailor").replace("SELLER","TAILOR")
    with open(f,"w",encoding="utf-8") as file: 
        file.write(content)
