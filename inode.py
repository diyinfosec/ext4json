from ext4Enums import ext4Enums
import json
class inode:
	def parse_inode(self,inode):
		e=ext4Enums()
		d={}
		d['i_mode']=int.from_bytes(inode[0:2],byteorder='little')
		d['_type']=e.enum_inode_type(d['i_mode'])
		permission_octal=int(oct(d['i_mode'])[2:][-3:].zfill(3))
		d['_permission']=e.octal_to_string(permission_octal)
		d['i_uid']=int.from_bytes(inode[2:4],byteorder='little')
		i_size_lo=int.from_bytes(inode[4:8],byteorder='little')
		d['i_atime']=e.epoch_to_date(int.from_bytes(inode[8:12],byteorder='little'))
		d['i_ctime']=e.epoch_to_date(int.from_bytes(inode[12:16],byteorder='little'))
		d['i_mtime']=e.epoch_to_date(int.from_bytes(inode[16:20],byteorder='little'))
		d['i_dtime']=e.epoch_to_date(int.from_bytes(inode[20:24],byteorder='little'))
		d['i_gid']=int.from_bytes(inode[24:26],byteorder='little')
		d['i_links_count']=int.from_bytes(inode[26:28],byteorder='little')
		d['i_blocks_lo']=int.from_bytes(inode[28:32],byteorder='little')
		d['i_flags']=int.from_bytes(inode[32:36],byteorder='little')
		d['l_i_version']=int.from_bytes(inode[36:40],byteorder='little')
		d['i_block']=self.parse_extent_tree(inode[40:100])
		d['i_generation']=int.from_bytes(inode[100:104],byteorder='little')
		d['i_file_acl_lo']=int.from_bytes(inode[104:108],byteorder='little')
		i_size_high=int.from_bytes(inode[108:112],byteorder='little')
		d['i_obso_faddr']=int.from_bytes(inode[112:116],byteorder='little')

		osd2=inode[116:128]
		d['l_i_blocks_high']=int.from_bytes(osd2[0:2],byteorder='little')
		d['l_i_file_acl_high']=int.from_bytes(osd2[2:4],byteorder='little')
		d['l_i_uid_high']=int.from_bytes(osd2[4:6],byteorder='little')
		d['l_i_gid_high']=int.from_bytes(osd2[6:8],byteorder='little')
		d['l_i_checksum_lo']=int.from_bytes(osd2[8:10],byteorder='little')
		d['l_i_reserved']=int.from_bytes(osd2[10:12],byteorder='little')

		d['i_extra_isize']=int.from_bytes(inode[128:130],byteorder='little')
		d['i_checksum_hi']=int.from_bytes(inode[130:132],byteorder='little')
		d['i_ctime_extra']=int.from_bytes(inode[132:136],byteorder='little')
		d['i_mtime_extra']=int.from_bytes(inode[136:140],byteorder='little')
		d['i_atime_extra']=int.from_bytes(inode[140:144],byteorder='little')
		d['i_crtime']=e.epoch_to_date(int.from_bytes(inode[144:148],byteorder='little'))
		d['i_crtime_extra']=int.from_bytes(inode[148:152],byteorder='little')
		d['i_version_hi']=int.from_bytes(inode[152:156],byteorder='little')
		d['i_projid']=int.from_bytes(inode[156:160],byteorder='little')

		#- Combining _hi and _lo fields, 32-bit fields
		d['i_size'] = (i_size_high<<32) + i_size_lo
		return d

	def parse_extent_tree(self,etree):
		d={}
		eh=etree[0:12]
		d['eh_magic']=int.from_bytes(eh[0:2],byteorder='little')

		#- Return if magic value is invalid
		if(d['eh_magic']!=62218):
			d['eh_magic']='INVALID'
			d['eh_magic_value']=eh[0:2].hex()
			return d
		else:
			d['eh_magic']='f30a'
			

		#- Return if there are no header entries
		d['eh_entries']=int.from_bytes(eh[2:4],byteorder='little')
		if(d['eh_entries']==0):
			return d

		d['eh_max']=int.from_bytes(eh[4:6],byteorder='little')
		d['eh_depth']=int.from_bytes(eh[6:8],byteorder='little')
		d['eh_generation']=int.from_bytes(eh[8:12],byteorder='little')
		n=12
		buf=etree[12:]
		entries = [buf[i:i+n] for i in range(0, len(buf), n)]

		out_l=[]
		blocks=[]
		for x in entries:
			#- Node dictionary
			nd={}
			#- Direct Blocks
			if d['eh_depth'] ==0:
				nd['ee_block']=int.from_bytes(x[0:4],byteorder='little')
				nd['ee_len']=int.from_bytes(x[4:6],byteorder='little')

				#- TODO: Validate approach for combining. 
				#- Ref1: https://github.com/emmanueliyan/pesaOS/blob/82136b3ee4c4164d02c68bf66ae3d2961661621f/drivers/filesystems/ext2/inc/linux/ext4_ext.h#L179
				#- Ref2: https://github.com/sleuthkit/sleuthkit/blob/e2c2570a456fb2ca5635e613bfd89d1fac9cb063/tsk/fs/ext2fs.c#L1691
				#- Ref3: Some kinda common sense?! That's what I have added here
				ee_start_hi=int.from_bytes(x[6:8],byteorder='little')
				ee_start_lo=int.from_bytes(x[8:12],byteorder='little')
				nd['ee_start']=(ee_start_hi << 32) + ee_start_lo

				#- Commented out since we have combined them into a single value.
				nd['ee_start_hi']=int.from_bytes(x[6:8],byteorder='little')
				nd['ee_start_lo']=int.from_bytes(x[8:12],byteorder='little')

				if(nd['ee_len']==0):
					break

				start_block=nd['ee_start']
				end_block=start_block+nd['ee_len']-1
				blocks.append(f"{start_block}-{end_block}")
				#print("i_mode: ", nd['i_mode'])
				#print("Blocks current: ",blocks)

			#- Indirect Blocks
			elif d['eh_depth'] > 0: 
				nd['ei_block']=int.from_bytes(x[0:4],byteorder='little')
				nd['ei_leaf_lo']=int.from_bytes(x[4:8],byteorder='little')
				nd['ei_leaf_hi']=int.from_bytes(x[8:10],byteorder='little')

				#- TODO: Validate combining logic
				ei_leaf_lo=int.from_bytes(x[4:8],byteorder='little')
				ei_leaf_hi=int.from_bytes(x[8:10],byteorder='little')

				start_block=max(ei_leaf_lo,ei_leaf_hi)
				end_block=start_block+ min(ei_leaf_lo,ei_leaf_hi)+1
				blocks.append(f"{start_block}-{end_block}")

				nd['ei_unused']=int.from_bytes(x[10:12],byteorder='little')

			out_l.append(nd)

		d['nodes']=out_l

		#- Setting direct and indirect blocks
		d['blocks']=blocks
	
		'''
		#- TODO: Maybe better approach to validate blocks as direct/indirect in code.
		if d['eh_depth'] ==0:
				d['direct_blocks']=blocks
		elif d['eh_depth'] ==0:
				d['indirect_blocks']=blocks
		'''
		return d
