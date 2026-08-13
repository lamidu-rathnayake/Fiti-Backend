import os

files_to_update = [
    "schema.sql",
    "tests/test_api.py",
    "app/api/schemas/rbac_schema.py",
    "app/domain/repositories/profile_repository.py",
    "app/domain/entities/user.py",
    "PROJECT_STRUCTURE.md",
    "Dev-Manual/nearby_shops_function_report.md",
    "Dev-Manual/login_system_report.md",
    "Dev-Manual/clean_architecture_report.md"
]

for file in files_to_update:
    path = os.path.join(r"d:\university\academics\Project Management\Assignments\MiniProject\Fiti-Backend", file)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        content = content.replace("seller", "tailor")
        content = content.replace("Seller", "Tailor")
        content = content.replace("SELLER", "TAILOR")
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
