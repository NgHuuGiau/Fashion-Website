import os
os.chdir('D:/Project/Fashion-Website')

# Read the part 2 YAML content
with open('ci_part2.yml', 'r') as f:
    ci_content = f.read()

# Append to the CI workflow
with open('.github/workflows/ci.yml', 'a') as f:
    f.write(ci_content)

print('Part 2 appended')