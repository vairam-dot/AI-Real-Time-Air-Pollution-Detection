# fix_config.py
import os

config_path = 'app/config.py'

if os.path.exists(config_path):
    with open(config_path, 'r') as file:
        content = file.read()
    
    # Fix the typo
    if 'osgetenv' in content:
        fixed_content = content.replace('osgetenv', 'os.getenv')
        
        with open(config_path, 'w') as file:
            file.write(fixed_content)
        
        print("✅ Fixed typo: changed 'osgetenv' to 'os.getenv'")
    else:
        print("✅ No typo found in config.py")
else:
    print(f"❌ Could not find {config_path}")

print("\n📁 Your config.py should now work!")