from datetime import datetime, timezone

class ext4Enums:
	def epoch_to_date(self,ts_epoch,date_fmt='%d-%b-%y %H:%M:%S'):
		if(ts_epoch==0):
			return 0
		else:
			return datetime.fromtimestamp(ts_epoch, timezone.utc).strftime(date_fmt)

	def enum_inode_type(self,i):
		if(i & 0x1000):
			 ret_str = 'FIFO'
		elif(i & 0x2000):
			 ret_str = 'CHARACTER_DEVICE'
		elif(i & 0x4000):
			 ret_str = 'DIRECTORY'
		elif(i & 0x6000):
			 ret_str = 'BLOCK_DEVICE'
		elif(i & 0x8000):
			 ret_str = 'REGULAR_FILE'
		elif(i & 0xA000):
			 ret_str = 'SOFT_LINK'
		elif(i & 0xC000):
			 ret_str = 'SOCKET'
		else:
			ret_str='UNKNOWN'

		return ret_str


	def octal_to_string(self,octal):
		permission = ["---", "--x", "-w-", "-wx", "r--", "r-x", "rw-", "rwx"]
		result = ""
		# Iterate over each of the digits in octal
		for ___ in [int(n) for n in str(octal)]:
			result += permission[___]
		return result

	def enum_file_type(self,i):
		if(i == 0x0):
			 ret_str = 'UNKNOWN'
		elif(i == 0x1):
			 ret_str = 'REGULAR_FILE'
		elif(i == 0x2):
			 ret_str = 'DIRECTORY'
		elif(i == 0x3):
			 ret_str = 'CHARACTER_DEVICE'
		elif(i == 0x4):
			 ret_str = 'BLOCK_DEVICE'
		elif(i == 0x5):
			 ret_str = 'FIFO'
		elif(i == 0x6):
			 ret_str = 'SOCKET'
		elif(i == 0x7):
			ret_str = 'SOFT_LINK'
		elif(i == 0xDE):
			ret_str = 'DIR_TAIL_ENTRY'
		else:
			ret_str='UNKNOWN'

		return ret_str
