import os
import shutil

src_dir = r"c:\Users\venka\Desktop\trail iitm\mentiscope-processing-speed-live-integration"
backend_dir = os.path.join(src_dir, "backend")
src_folder = os.path.join(src_dir, "src")

# Create Backend directories
backend_dirs = [
    backend_dir,
    os.path.join(backend_dir, "modules"),
    os.path.join(backend_dir, "modules", "processing_speed"),
    os.path.join(backend_dir, "modules", "processing_speed", "api"),
    os.path.join(backend_dir, "modules", "processing_speed", "calibration"),
    os.path.join(backend_dir, "modules", "processing_speed", "engine"),
    os.path.join(backend_dir, "modules", "processing_speed", "models"),
    os.path.join(backend_dir, "modules", "processing_speed", "repositories"),
    os.path.join(backend_dir, "modules", "processing_speed", "schemas"),
    os.path.join(backend_dir, "modules", "processing_speed", "services"),
    os.path.join(backend_dir, "modules", "processing_speed", "utils"),
]

for d in backend_dirs:
    os.makedirs(d, exist_ok=True)

# Helper to write files safely
def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# Recreate all __init__.py files
write_file(os.path.join(backend_dir, "__init__.py"), '"""Mentiscope FastAPI application package."""\n')
write_file(os.path.join(backend_dir, "modules", "__init__.py"), '"""Independent Mentiscope assessment modules."""\n')
write_file(os.path.join(backend_dir, "modules", "processing_speed", "__init__.py"), '"""Processing Speed (Gs) assessment module."""\n')
write_file(os.path.join(backend_dir, "modules", "processing_speed", "api", "__init__.py"), '"""HTTP adapter for the Processing Speed module."""\n')
write_file(os.path.join(backend_dir, "modules", "processing_speed", "calibration", "__init__.py"), '"""Reserved for versioned module calibration data."""\n')

write_file(os.path.join(backend_dir, "modules", "processing_speed", "engine", "__init__.py"), 
'''from .perceptual_speed import generate_trial

__all__ = ["generate_trial"]
''')

write_file(os.path.join(backend_dir, "modules", "processing_speed", "models", "__init__.py"), 
'"""The module reuses Mentiscope\'s shared session, response, event, result and analytics models."""\n')

write_file(os.path.join(backend_dir, "modules", "processing_speed", "repositories", "__init__.py"), 
'''from .assessment_repository import ProcessingSpeedRepository

__all__ = ["ProcessingSpeedRepository"]
''')

write_file(os.path.join(backend_dir, "modules", "processing_speed", "schemas", "__init__.py"), 
'''from .assessment import AnswerRequest, FinishRequest, StartRequest

__all__ = ["AnswerRequest", "FinishRequest", "StartRequest"]
''')

write_file(os.path.join(backend_dir, "modules", "processing_speed", "services", "__init__.py"), 
'''from .assessment_service import ProcessingSpeedAssessmentService

__all__ = ["ProcessingSpeedAssessmentService"]
''')

write_file(os.path.join(backend_dir, "modules", "processing_speed", "utils", "__init__.py"), 
'"""Processing Speed module utilities namespace."""\n')

# Copy Backend module files (checking if they exist first)
files_to_copy = [
    ("main.py", os.path.join(backend_dir, "main.py")),
    ("database.py", os.path.join(backend_dir, "database.py")),
    ("core_models.py", os.path.join(backend_dir, "core_models.py")),
    ("requirements.txt", os.path.join(backend_dir, "requirements.txt")),
    ("router.py", os.path.join(backend_dir, "modules", "processing_speed", "api", "router.py")),
    ("perceptual_speed.py", os.path.join(backend_dir, "modules", "processing_speed", "engine", "perceptual_speed.py")),
    ("assessment_repository.py", os.path.join(backend_dir, "modules", "processing_speed", "repositories", "assessment_repository.py")),
    ("assessment.py", os.path.join(backend_dir, "modules", "processing_speed", "schemas", "assessment.py")),
    ("assessment_service.py", os.path.join(backend_dir, "modules", "processing_speed", "services", "assessment_service.py")),
]

for src_name, dest_path in files_to_copy:
    src_path = os.path.join(src_dir, src_name)
    if os.path.exists(src_path):
        shutil.copy(src_path, dest_path)

# Create Frontend directories
frontend_dirs = [
    src_folder,
    os.path.join(src_folder, "types"),
    os.path.join(src_folder, "config"),
    os.path.join(src_folder, "components"),
    os.path.join(src_folder, "pages"),
    os.path.join(src_folder, "services"),
    os.path.join(src_folder, "services", "auth"),
    os.path.join(src_folder, "services", "assessment"),
    os.path.join(src_folder, "services", "report"),
    os.path.join(src_folder, "services", "analytics"),
    os.path.join(src_folder, "services", "modules"),
]

for d in frontend_dirs:
    os.makedirs(d, exist_ok=True)

# Copy Frontend files
frontend_files = [
    ("main.tsx", os.path.join(src_folder, "main.tsx")),
    ("App.tsx", os.path.join(src_folder, "App.tsx")),
    ("index.css", os.path.join(src_folder, "index.css")),
    ("index.ts", os.path.join(src_folder, "types", "index.ts")),
    ("moduleConfig.ts", os.path.join(src_folder, "config", "moduleConfig.ts")),
    ("questionsData.ts", os.path.join(src_folder, "config", "questionsData.ts")),
    ("Navbar.tsx", os.path.join(src_folder, "components", "Navbar.tsx")),
    ("Footer.tsx", os.path.join(src_folder, "components", "Footer.tsx")),
    ("Charts.tsx", os.path.join(src_folder, "components", "Charts.tsx")),
    ("LandingPage.tsx", os.path.join(src_folder, "pages", "LandingPage.tsx")),
    ("AuthPage.tsx", os.path.join(src_folder, "pages", "AuthPage.tsx")),
    ("StudentDashboard.tsx", os.path.join(src_folder, "pages", "StudentDashboard.tsx")),
    ("AssessmentRunner.tsx", os.path.join(src_folder, "pages", "AssessmentRunner.tsx")),
    ("ReportPage.tsx", os.path.join(src_folder, "pages", "ReportPage.tsx")),
    ("InternDashboard.tsx", os.path.join(src_folder, "pages", "InternDashboard.tsx")),
    ("SuperAdminDashboard.tsx", os.path.join(src_folder, "pages", "SuperAdminDashboard.tsx")),
    ("AuthService.ts", os.path.join(src_folder, "services", "auth", "AuthService.ts")),
    ("AssessmentService.ts", os.path.join(src_folder, "services", "assessment", "AssessmentService.ts")),
    ("ReportService.ts", os.path.join(src_folder, "services", "report", "ReportService.ts")),
    ("AnalyticsService.ts", os.path.join(src_folder, "services", "analytics", "AnalyticsService.ts")),
    ("attention.ts", os.path.join(src_folder, "services", "modules", "attention.ts")),
    ("executive.ts", os.path.join(src_folder, "services", "modules", "executive.ts")),
    ("gf.ts", os.path.join(src_folder, "services", "modules", "gf.ts")),
    ("gq.ts", os.path.join(src_folder, "services", "modules", "gq.ts")),
    ("gsm.ts", os.path.join(src_folder, "services", "modules", "gsm.ts")),
    ("language.ts", os.path.join(src_folder, "services", "modules", "language.ts")),
    ("processingSpeed.ts", os.path.join(src_folder, "services", "modules", "processingSpeed.ts")),
]

for src_name, dest_path in frontend_files:
    src_path = os.path.join(src_dir, src_name)
    if os.path.exists(src_path):
        shutil.copy(src_path, dest_path)

# Delete flat files in root
files_to_delete = [
    "__init__.py", "__init__ (2).py", "__init__ (3).py", "__init__ (4).py", "__init__ (5).py",
    "__init__ (6).py", "__init__ (7).py", "__init__ (8).py", "__init__ (9).py", "__init__ (10).py", "__init__ (11).py",
    "main.py", "database.py", "core_models.py", "router.py", "perceptual_speed.py",
    "assessment_repository.py", "assessment.py", "assessment_service.py",
    "main.tsx", "App.tsx", "index.css", "index.ts", "moduleConfig.ts", "questionsData.ts",
    "Navbar.tsx", "Footer.tsx", "Charts.tsx", "LandingPage.tsx", "AuthPage.tsx",
    "StudentDashboard.tsx", "AssessmentRunner.tsx", "ReportPage.tsx", "InternDashboard.tsx",
    "SuperAdminDashboard.tsx", "AuthService.ts", "AssessmentService.ts", "ReportService.ts",
    "AnalyticsService.ts", "attention.ts", "executive.ts", "gf.ts", "gq.ts", "gsm.ts",
    "language.ts", "processingSpeed.ts"
]

for filename in files_to_delete:
    filepath = os.path.join(src_dir, filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"Error deleting {filename}: {e}")

print("Restoration complete!")
