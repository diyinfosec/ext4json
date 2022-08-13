from superblock import parse_superblock
import json
file_name='sb.bin'
f=open(file_name,'rb')
buf=f.read()
d=parse_superblock(buf)
print(json.dumps(d,indent=4))
