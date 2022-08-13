def parse_blockgroup(bg):
	d={}
	bg_block_bitmap_lo=int.from_bytes(bg[0:4],byteorder='little')
	bg_inode_bitmap_lo=int.from_bytes(bg[4:8],byteorder='little')
	bg_inode_table_lo=int.from_bytes(bg[8:12],byteorder='little')
	
	#- 16-bit fields
	bg_free_blocks_count_lo=int.from_bytes(bg[12:14],byteorder='little')
	bg_free_inodes_count_lo=int.from_bytes(bg[14:16],byteorder='little')
	bg_used_dirs_count_lo=int.from_bytes(bg[16:18],byteorder='little')

	d['bg_flags']=int.from_bytes(bg[18:20],byteorder='little')
	bg_exclude_bitmap_lo=int.from_bytes(bg[20:24],byteorder='little')

	#- 16-bit fields
	bg_block_bitmap_csum_lo=int.from_bytes(bg[24:26],byteorder='little')
	bg_inode_bitmap_csum_lo=int.from_bytes(bg[26:28],byteorder='little')
	bg_itable_unused_lo=int.from_bytes(bg[28:30],byteorder='little')

	d['bg_checksum']=int.from_bytes(bg[30:32],byteorder='little')
	bg_block_bitmap_hi=int.from_bytes(bg[32:36],byteorder='little')
	bg_inode_bitmap_hi=int.from_bytes(bg[36:40],byteorder='little')
	bg_inode_table_hi=int.from_bytes(bg[40:44],byteorder='little')

	#- 16-bit fields
	bg_free_blocks_count_hi=int.from_bytes(bg[44:46],byteorder='little')
	bg_free_inodes_count_hi=int.from_bytes(bg[46:48],byteorder='little')
	bg_used_dirs_count_hi=int.from_bytes(bg[48:50],byteorder='little')
	bg_itable_unused_hi=int.from_bytes(bg[50:52],byteorder='little')

	bg_exclude_bitmap_hi=int.from_bytes(bg[52:56],byteorder='little')

	#- 16-bit fields
	bg_block_bitmap_csum_hi=int.from_bytes(bg[56:58],byteorder='little')
	bg_inode_bitmap_csum_hi=int.from_bytes(bg[58:60],byteorder='little')

	d['bg_reserved']=int.from_bytes(bg[60:64],byteorder='little')

	#- Combining _hi and _lo fields, 32-bit fields
	d['bg_block_bitmap'] = (bg_block_bitmap_hi<<32) + bg_block_bitmap_lo
	d['bg_inode_bitmap'] = (bg_inode_bitmap_hi<<32) + bg_inode_bitmap_lo
	d['bg_inode_table'] = (bg_inode_table_hi<<32) + bg_inode_table_lo
	d['bg_exclude_bitmap'] = (bg_exclude_bitmap_hi<<32) + bg_exclude_bitmap_lo

	#- Combining _hi and _lo fields, 16-bit fields
	#- TODO: Review this. How to combine two 16-bit fields?
	d['bg_free_blocks_count'] = (bg_free_blocks_count_hi<<16) + bg_free_blocks_count_lo
	d['bg_free_inodes_count'] = (bg_free_inodes_count_hi<<16) + bg_free_inodes_count_lo
	d['bg_used_dirs_count'] = (bg_used_dirs_count_hi<<16) + bg_used_dirs_count_lo
	d['bg_exclude_bitmap'] = (bg_exclude_bitmap_hi<<16) + bg_exclude_bitmap_lo
	d['bg_block_bitmap_csum'] = (bg_block_bitmap_csum_hi<<16) + bg_block_bitmap_csum_lo
	d['bg_inode_bitmap_csum'] = (bg_inode_bitmap_csum_hi<<16) + bg_inode_bitmap_csum_lo
	d['bg_itable_unused'] = (bg_itable_unused_hi<<16) + bg_itable_unused_lo

	return d
