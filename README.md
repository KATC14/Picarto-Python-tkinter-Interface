# Picarto-Python-tkinter-Interface
Python tkinter Interface for followed streams on Picarto.tv
<br><br>
## dependencies
- python [pillow](https://pypi.org/project/Pillow/)
- custom library [Hoverinfo](https://github.com/KATC14/python-custom-library)
- custom library [utilities](https://github.com/KATC14/python-custom-library)
- streamlink [cli](https://streamlink.github.io)<br><br>

#
oauth url `https://oauth.picarto.tv/authorize?response_type=token&client_id=&redirect_uri=&scope=readpub%20readpriv%20sudo%20write`

you must make a token using the oauth url

first make a client [here](https://oauth.picarto.tv/client) and take its Client ID and put it after client_id=

the redirec uri can just be your picarto channel it goes under redirect_uri=

copy the oauth token and place it in self.auth inside the file

you will get a link back that looks like this https://picarto.tv/YOUR_CHANNEL#access_token=TOKEN_HERE&token_type=Bearer&expires_in=1296000

the token will expire every 15 days and need to be refreshed

#
variable MissingNames: for channels that have deactivated their account (unknown if it still works)

variable StandoutNames: for channels you want to stand out

when switching pages the picarto api acts strange and gives overlapping channels overlapped channels are shown in cyan
