from smbclient import listdir, mkdir, open_file, register_session, scandir, stat
from smbclient.path import isdir

# share = r'\\B800fsA.local\b800fsav1'
# share = r'\\100.91.67.68\b800fsav1'

# register_session('100.91.67.68', username='Guest', password="")
# register_session('100.91.67.68',auth_protocol='ntlm')
# register_session('192.168.0.120')
# register_session('B800fsA.local')
register_session("vada.local", auth_protocol="ntlm")

# for filename in listdir(share):
#     print(filename)
