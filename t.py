import json
from superblock import parse_superblock
from blockgroups import parse_blockgroup
from inode import inode
from direntry import direntry

file_name='sb.bin'
file_name='sda1.bin'

f=open(file_name,'rb') 


#====================================
#- FUNCTION: For setting up Loggers
#====================================
import logging

def setup_logger(name, log_file, level=logging.INFO, formatter=logging.Formatter('%(message)s')):
	#- To setup as many loggers as you want
	#- Ref: https://stackoverflow.com/a/11233293

	handler = logging.FileHandler(log_file,'w')
	handler.setFormatter(formatter)

	logger = logging.getLogger(name)
	logger.setLevel(level)
	logger.addHandler(handler)

	return logger

#==============================================
#- FUNCTION: Get list of Dir Entry blocks
#==============================================
def get_block_list(buf,block_num,fp):
		d={}
		global block_list
		#- Just read 60 bytes from buffer, enough to validate/process an extent tree
		etree=buf[:60] 

		d=obj_i.parse_extent_tree(etree)

		#- Is it an Extent Header?
		if(d['eh_magic']!='INVALID'):
			print(f"Extent Tree at {block_num}")
			#print(json.dumps(d,indent=4))
			for x in d['blocks']:
				y=x.split('-')
				start_block=int(y[0])
				end_block=int(y[1])
				#print(start_block,"-",end_block)
				for z in range(start_block,end_block+1):
					fp.seek(z*ACTUAL_BLOCK_SIZE)
					buf=fp.read(60)
					block_num=z
					get_block_list(buf,block_num,fp)
		else:
			block_list.append(block_num)

		return block_list


#====================================
#- Initializing variables used here
#====================================
#- Logging related
sb_logger = setup_logger('sb_logger', 'logs/superblock.json')
bg_logger = setup_logger('bg_logger', 'logs/blockgroups.json')
inode_logger = setup_logger('inode_logger', 'logs/inodes.json')
de_logger = setup_logger('de_logger', 'logs/direntries.json')


#- Objects for inode and directory entry
obj_i=inode()
obj_d=direntry()

#- List of blocks (For extent tree processing)
block_list=[]


#==========================
#- Reading Superblock
#==========================
f.seek(1024)
buf=f.read(1024)
#print(buf)
d=parse_superblock(buf)
sb_logger.info(json.dumps(d))


#- TODO: Superblock validation

ACTUAL_BLOCK_SIZE=2**(10+d['s_log_block_size'])
x=d['s_blocks_count']/d['s_blocks_per_group']
NUM_GDT_ENTRIES=int(x) + bool(x%1)
TOTAL_INODES=d['s_inodes_count']
INODES_PER_GROUP=d['s_inodes_per_group']
INODE_SIZE=d['s_inode_size']

#print(f"Actual Block Size: {ACTUAL_BLOCK_SIZE}")
#print(f"Number of Block Groups: {NUM_GDT_ENTRIES}")

#==========================
#- Reading GDT entries
#==========================
bg_l=[]
f.seek(ACTUAL_BLOCK_SIZE)
for x in range(NUM_GDT_ENTRIES):
	buf=f.read(64)
	bg_parsed=parse_blockgroup(buf)
	#print(json.dumps(bg_parsed,indent=4))
	bg_logger.info(json.dumps(bg_parsed))
	bg_l.append(bg_parsed)

#================================
#- Reading inode table entries
#================================
last_bg=len(bg_l)-1
for bg_num,x in enumerate(bg_l):
	#print(json.dumps(x,indent=4))
	inode_table_offset=x['bg_inode_table']*ACTUAL_BLOCK_SIZE
	used_inodes=INODES_PER_GROUP-x['bg_free_inodes_count']
	#print(f"Block Group {bg_num} has {INODES_PER_GROUP} inodes of which {used_inodes} are used and {x['bg_free_inodes_count']} inodes are free.")
	f.seek(inode_table_offset)
	curr_inode=1
	#read from 1 till you reach used_inodes
	for i in range(1,used_inodes+1):
		pos=inode_table_offset+(i-1)*INODE_SIZE
		f.seek(pos)
		buf=f.read(INODE_SIZE)
		inode=obj_i.parse_inode(buf)
		inode['_bgroup']=bg_num
		inode['_inum']=i+(bg_num*INODES_PER_GROUP)
		inode_logger.info(json.dumps(inode))
		#- Directory that is not deleted. TODO: Maybe include deleted ones?
		if(inode['_type']=='DIRECTORY' and inode['i_dtime']==0):
			if 'blocks' in inode['i_block']:
				for block_range in inode['i_block']['blocks']:
					x=block_range.split('-')
					start_block=int(x[0])
					end_block=int(x[1])

					for y in range(start_block,end_block+1):
						f.seek(ACTUAL_BLOCK_SIZE*y)
						#print(f"Processing block {y}")
						buf=f.read(60)

						#- Function to get final list of blocks (after walking through the indirect blocks)
						#print("Input is ", y)
						block_list=[]
						b=get_block_list(buf,y,f)
						#print("Output from recursive function :", b)
						#print("----------")

						#- Read the damn block
						for z in b:
								f.seek(ACTUAL_BLOCK_SIZE*y)
								#print(f"Processing block {z}")
								buf=f.read(ACTUAL_BLOCK_SIZE)
								for de in obj_d.parse_de_block(buf):
									#- Adding validations:
									#- record length should not exceed the block size. 
									#- inode number should not exceed total inodes defined in the superblock
									if(de['rec_len']<ACTUAL_BLOCK_SIZE and de['inode']<TOTAL_INODES):
											#print(de)
											de_logger.info(json.dumps(de))

'''
					exit()
		
'''
