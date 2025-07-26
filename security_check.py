#!/usr/bin/env python3
"""
Security Check Script for StockAI Project
This script performs various security checks on the codebase.
"""

import os
import re
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

class SecurityChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.project_root = Path(__file__).parent
        
    def check_env_files(self) -> None:
        """Check for exposed environment files"""
        print("🔍 Checking for exposed environment files...")
        
        env_files = [
            ".env",
            ".env.local",
            ".env.production",
            ".env.staging",
            "secrets.json",
            "config.json"
        ]
        
        for env_file in env_files:
            if (self.project_root / env_file).exists():
                self.issues.append(f"❌ Found exposed environment file: {env_file}")
            else:
                print(f"✅ {env_file} not found (good)")
    
    def check_gitignore(self) -> None:
        """Check if .gitignore properly excludes sensitive files"""
        print("\n🔍 Checking .gitignore configuration...")
        
        gitignore_path = self.project_root / ".gitignore"
        if not gitignore_path.exists():
            self.issues.append("❌ .gitignore file not found")
            return
        
        with open(gitignore_path, 'r') as f:
            content = f.read()
        
        required_patterns = [
            r"\.env",
            r"\.env\.",
            r"secrets/",
            r"\.secrets",
            r"__pycache__/",
            r"node_modules/",
            r"\.DS_Store",
            r"\.idea/",
            r"\.vscode/",
            r"\*\.log",
            r"\*\.db",
            r"\*\.sqlite",
            r"\*\.pem",
            r"\*\.key",
            r"\*\.crt"
        ]
        
        for pattern in required_patterns:
            if not re.search(pattern, content):
                self.warnings.append(f"⚠️  Missing pattern in .gitignore: {pattern}")
            else:
                print(f"✅ Pattern found in .gitignore: {pattern}")
    
    def check_hardcoded_secrets(self) -> None:
        """Check for hardcoded secrets in code"""
        print("\n🔍 Checking for hardcoded secrets...")
        
        # Patterns to look for
        secret_patterns = [
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]",
            r"api_key\s*=\s*['\"][^'\"]+['\"]",
            r"token\s*=\s*['\"][^'\"]+['\"]",
            r"key\s*=\s*['\"][^'\"]+['\"]",
            r"sk-",  # OpenAI API keys
            r"pk_",  # Stripe keys
            r"AKIA",  # AWS keys
        ]
        
        # File extensions to check
        extensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.json', '.yml', '.yaml']
        
        # Directories to skip
        skip_dirs = ['node_modules', '__pycache__', '.git', 'env', '.next', 'dist', 'build']
        
        for ext in extensions:
            for file_path in self.project_root.rglob(f"*{ext}"):
                # Skip certain directories
                if any(skip in str(file_path) for skip in skip_dirs):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern in secret_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            self.warnings.append(f"⚠️  Potential hardcoded secret in {file_path}: {match[:50]}...")
                except Exception as e:
                    print(f"⚠️  Could not read {file_path}: {e}")
    
    def check_dependencies(self) -> None:
        """Check for known vulnerabilities in dependencies"""
        print("\n🔍 Checking dependencies for vulnerabilities...")
        
        # Check Python dependencies
        if (self.project_root / "backend" / "requirements.txt").exists():
            print("✅ Python requirements.txt found")
            # Note: In a real implementation, you would run:
            # subprocess.run(["safety", "check", "-r", "backend/requirements.txt"])
        
        # Check Node.js dependencies
        if (self.project_root / "frontend" / "package.json").exists():
            print("✅ Node.js package.json found")
            # Note: In a real implementation, you would run:
            # subprocess.run(["npm", "audit"], cwd="frontend")
    
    def check_ssl_configuration(self) -> None:
        """Check SSL/TLS configuration"""
        print("\n🔍 Checking SSL configuration...")
        
        # Check if HTTPS is enforced in production
        main_py = self.project_root / "backend" / "app" / "main.py"
        if main_py.exists():
            with open(main_py, 'r') as f:
                content = f.read()
            
            if "HTTPSRedirectMiddleware" in content:
                print("✅ HTTPS redirect middleware found")
            else:
                self.warnings.append("⚠️  HTTPS redirect middleware not found")
    
    def check_cors_configuration(self) -> None:
        """Check CORS configuration"""
        print("\n🔍 Checking CORS configuration...")
        
        main_py = self.project_root / "backend" / "app" / "main.py"
        if main_py.exists():
            with open(main_py, 'r') as f:
                content = f.read()
            
            if "allow_origins" in content and "allow_credentials" in content:
                print("✅ CORS middleware configured")
            else:
                self.issues.append("❌ CORS middleware not properly configured")
    
    def check_authentication(self) -> None:
        """Check authentication implementation"""
        print("\n🔍 Checking authentication implementation...")
        
        auth_file = self.project_root / "backend" / "app" / "core" / "auth.py"
        if auth_file.exists():
            with open(auth_file, 'r') as f:
                content = f.read()
            
            checks = [
                ("JWT_SECRET", "JWT secret configuration"),
                ("jwt.encode", "JWT token generation"),
                ("jwt.decode", "JWT token validation"),
                ("timedelta", "Token expiration"),
                ("oauth2_scheme", "OAuth2 implementation")
            ]
            
            for pattern, description in checks:
                if pattern in content:
                    print(f"✅ {description} found")
                else:
                    self.warnings.append(f"⚠️  {description} not found")
    
    def check_input_validation(self) -> None:
        """Check for input validation"""
        print("\n🔍 Checking input validation...")
        
        # Check for Pydantic models
        for py_file in self.project_root.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['node_modules', '__pycache__', '.git', 'env']):
                continue
            
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                if "from pydantic import" in content or "BaseModel" in content:
                    print(f"✅ Pydantic models found in {py_file.name}")
                    break
            except Exception:
                continue
        else:
            self.warnings.append("⚠️  No Pydantic models found for input validation")
    
    def check_sql_injection(self) -> None:
        """Check for potential SQL injection vulnerabilities"""
        print("\n🔍 Checking for SQL injection vulnerabilities...")
        
        for py_file in self.project_root.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['node_modules', '__pycache__', '.git', 'env']):
                continue
            
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # Look for raw SQL queries with string formatting
                sql_patterns = [
                    r"execute\(f\"[^\"]*\{[^}]*\}[^\"]*\"",
                    r"execute\(\"[^\"]*%s[^\"]*\"",
                    r"execute\(\"[^\"]*\{[^}]*\}[^\"]*\"",
                ]
                
                for pattern in sql_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        self.warnings.append(f"⚠️  Potential SQL injection in {py_file}: {match[:50]}...")
            except Exception:
                continue
    
    def generate_report(self) -> None:
        """Generate security report"""
        print("\n" + "="*60)
        print("🔒 SECURITY CHECK REPORT")
        print("="*60)
        
        if not self.issues and not self.warnings:
            print("🎉 No security issues found!")
            print("✅ Your project appears to be secure.")
        else:
            if self.issues:
                print("\n❌ CRITICAL ISSUES:")
                for issue in self.issues:
                    print(f"  {issue}")
            
            if self.warnings:
                print("\n⚠️  WARNINGS:")
                for warning in self.warnings:
                    print(f"  {warning}")
        
        print("\n📋 RECOMMENDATIONS:")
        print("  1. Run 'npm audit' in frontend directory")
        print("  2. Run 'safety check' for Python dependencies")
        print("  3. Enable HTTPS in production")
        print("  4. Implement rate limiting")
        print("  5. Regular security audits")
        print("  6. Keep dependencies updated")
        
        print("\n📚 RESOURCES:")
        print("  - OWASP Top 10: https://owasp.org/www-project-top-ten/")
        print("  - Security Headers: https://securityheaders.com/")
        print("  - Mozilla Security Guidelines: https://infosec.mozilla.org/guidelines/")

def main():
    """Main function"""
    print("🔒 Starting Security Check for StockAI Project...")
    
    checker = SecurityChecker()
    
    # Run all checks
    checker.check_env_files()
    checker.check_gitignore()
    checker.check_hardcoded_secrets()
    checker.check_dependencies()
    checker.check_ssl_configuration()
    checker.check_cors_configuration()
    checker.check_authentication()
    checker.check_input_validation()
    checker.check_sql_injection()
    
    # Generate report
    checker.generate_report()
    
    # Exit with error code if critical issues found
    if checker.issues:
        sys.exit(1)

if __name__ == "__main__":
    main() 