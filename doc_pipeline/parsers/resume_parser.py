import re
from typing import List, Dict, Any

RESUME_FIELDS = [
    "FullName",
    "Email",
    "PhoneNumber",
    "Skills",
    "WorkExperience",
    "Education"
]

def fast_regex_resume_parse(text: str) -> Dict[str, Any]:
    """
    Try to extract resume fields using regex and simple heuristics.
    """
    result = {
        "FullName": None,
        "Email": None,
        "PhoneNumber": None,
        "Skills": [],
        "WorkExperience": [],
        "Education": []
    }
    # Email
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    if email_match:
        result["Email"] = email_match.group(0)
    # Phone
    phone_match = re.search(r"(\+?\d[\d\s\-\(\)]{7,}\d)", text)
    if phone_match:
        result["PhoneNumber"] = phone_match.group(0)
    # Name (very naive: first line, if not email/phone)
    lines = text.splitlines()
    for line in lines:
        if line.strip() and not re.search(r"@|\d", line):
            result["FullName"] = line.strip()
            break
    # Skills (look for 'Skills' section)
    skills = []
    skills_section = re.search(r"Skills[:\s\n]+([\w\s,\-\.;]+)", text, re.IGNORECASE)
    if skills_section:
        skills = [s.strip() for s in re.split(r",|;|\n", skills_section.group(1)) if s.strip()]
    result["Skills"] = skills
    # Education (look for 'Education' section)
    education = []
    edu_section = re.search(r"Education[:\s\n]+([\w\s,\-\.;\(\)\d]+)", text, re.IGNORECASE)
    if edu_section:
        edu_items = [e.strip() for e in re.split(r"\n|;", edu_section.group(1)) if e.strip()]
        for item in edu_items:
            # Simple parsing - could be enhanced
            education.append({
                "Institution": item,
                "Degree": None,
                "GraduationYear": None
            })
    result["Education"] = education
    # Work Experience (look for 'Experience' section)
    experience = []
    exp_section = re.search(r"Experience[:\s\n]+([\w\s,\-\.;\(\)\d]+)", text, re.IGNORECASE)
    if exp_section:
        exp_items = [e.strip() for e in re.split(r"\n|;", exp_section.group(1)) if e.strip()]
        for item in exp_items:
            # Simple parsing - could be enhanced
            experience.append({
                "Company": item,
                "Role": None,
                "Dates": None
            })
    result["WorkExperience"] = experience
    return result

# Fallback to Gemini (to be implemented in extractor) 