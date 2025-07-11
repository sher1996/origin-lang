import sys, re
for line in open(sys.argv[1]):
    m = re.match(r'\s*say\s+"(.+?)"', line)
    if m:
        print(m.group(1)) 