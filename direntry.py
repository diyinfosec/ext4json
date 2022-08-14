#https://github.com/scorelab/OpenDF/blob/2664307a9a4924c47f487d2c62b603a5fa449923/sleuthkit/tsk/fs/tsk_ext2fs.h#L439
#((len + 8 + 3) & ~(3))
from ext4Enums import ext4Enums

class direntry:
	def is_valid_dentry(self,de):
		#print(de)
		#- Tail entry. TODO: More conditions? name_len=0 and _actual_len=8 and file_name=""
		if(de['inode']==0 and de['file_type']=='DIR_TAIL_ENTRY' and de['rec_len']==12):
			return True

		#- File name cannot be negative or more than 255 chars
		if(de['name_len']<=0 or de['name_len']>255):
			return False

		#- Record length will always be multiple of 4.
		if(de['rec_len']%4 !=0):
			return False

		#- File name cannot be empty
		try:
				if(de['file_name']==''):
					return False
		except KeyError:
				if(de['file_name_hex']==''):
					return False

		#- inode cannot be 0 or negative. 
		if(de['inode']<=0): 
			return False

		#- TODO: For now this validation needs to be done by caller:
		#- inode exceeds total inodes in superblock
		#- rec_len exceeds size of block


		return True

	def parse_de_block(self,de_block):
		curr_offset=0
		deletedEntry=False
		while True:
			buf=de_block[curr_offset:curr_offset+263]
			if not buf:
				break

			de={}
			e=ext4Enums()
			de['inode']=int.from_bytes(buf[0:4],byteorder='little')
			de['rec_len']=int.from_bytes(buf[4:6],byteorder='little')
			de['name_len']=int.from_bytes(buf[6:7],byteorder='little')
			de['file_type']=e.enum_file_type(int.from_bytes(buf[7:8],byteorder='little'))
			try:
					de['file_name']=buf[8:8+de['name_len']].decode()
			except UnicodeDecodeError:
					de['file_name_hex']=buf[8:8+de['name_len']].hex()
			de['_actual_len']=(de['name_len'] + 8 + 3) & ~(3)

			if(de['_actual_len'] != de['rec_len']):
				deletedEntry=True

			if(deletedEntry and de['file_type']!='DIR_TAIL_ENTRY'):
				de['_del_flg']='Y'

			curr_offset=curr_offset+de['_actual_len']
			if(self.is_valid_dentry(de)): 
					yield de
