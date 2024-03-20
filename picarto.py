import json
import datetime
import time
import os
import io
import base64
import tkinter
import threading
import webbrowser
import traceback
from tkinter.ttk import *
#import urllib.request

from PIL import ImageTk, Image

import custom.HoverInfo#, tkinter.GifLabel
from custom import utilities

class Picarto():
	def __init__(self):
		os.system('cls')
		print(f"Picarto Python tkinter Interface")

		self.root = tkinter.Tk()

		self.root.grid_rowconfigure(0, weight=1)
		self.root.grid_columnconfigure(0, weight=1)
		self.root.title("Picarto Python tkinter Interface")
		self.vcmd = (self.root.register(lambda *args: args[2].isdigit()), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
		self.style = Style()
		self.selvar = tkinter.IntVar()

		# https://oauth.picarto.tv/clients list clients in json
		# https://oauth.picarto.tv/client  make clients

		self.auth = ""

		self.data = self.labelold = self.url = None
		self.LiveFirst = self.onwhattab = self.FWrating = True
		self.pchbool = self.PHttp = self.Pfifo = self.hssd = False
		self.streamaugs, self.cache, self.raidolist = {}, {}, []
		self.pagenum = self.ncSwitch = 1

		self.multivalue = (50, 51, 52, 53)
		self.genaricurl = "https://api.picarto.tv/api/v1"
		self.MissingNames = ()
		self.StandoutNames = ()
		self.multi = self.multi1 = self.multi2 = self.multi3 = 'Empty'
		#self.old = []

		self.menubarStart()
		self.subsrt()
		self.start(True)
		self.root.mainloop()
		print('Program Terminated')

	def start_thread(self, event):
		aug = ''
		for i in self.streamaugs.values(): aug += f"{i} "
		if event == 0: self.thread = threading.Thread(target=lambda: self.stream(f'{aug}{self.url}'))
		if event == 1: self.thread = threading.Thread(target=lambda: self.stream(f"{aug}{self.videofile}"))
		self.thread.start()
		self.root.after(20, self.check_thread)

	def check_thread(self):
		if self.thread.is_alive():
			self.root.after(20, self.check_thread)
		else:
			self.thread.join()

	def start(self, start=False, changepage=False):
		#params = f"&filter_params[{'following'}]={31060}&filter_params[{'adult'}]={str(self.FWrating).lower()}"#&filter_params[{test}]={test}
		#f"https://ptvintern.picarto.tv/api/explore?first={40}&page={1}{params}"#https://ptvintern.picarto.tv/api/following/31060
		url = f"{self.genaricurl}/user/following?page={self.pagenum}&priority_online={str(self.LiveFirst).lower()}"#&maturecontent={}, str(self.FWrating).lower() #&adult={}

		headers = self.HeaderFormat({"auth":'bearer'})
		headers.update(utilities.generic_header({"ua":'m5'}))

		response = utilities.url_request(url, headers)
		if response.status == 200:
			self.data = json.loads(response.read())#["channels"]
			try:
				test = [i['name'] for i in self.data for x in self.old if i['name'] == x['name']]
				#test = []
				#for i in self.data:
				#	for x in self.old:
				#		if i['name'] == x['name']:
				#			test.append(i['name'])
			except Exception:
				pass
			self.old = self.data
			#print(self.data)

			self.labelF.config(text=f'Follows online "{len([1 for i in self.data if i["online"]])}"')#sum(1 for i in self.data if i["online"])

			#print(len(self.data))
			column, row = -1, 0
			for i, x in enumerate(self.data):
				column += 1
				if column >= 5:#9
					row += 1
					column = 0
				nameS = x['name']
				#f"https://ptvintern.picarto.tv/api/channel/detail/{nameS}"#url found in streamlink picarto plugin

				#self.AvatarS = self.data[i]['avatar']

				#try:
				#	exec("self.AvatarS{} = self.AvatarS".format(i))
				#except Exception:print(traceback.format_exc())

				#exec(f"self.name{i} = nameS")

				#online = x['online']
				self.style.configure(f'R{i}.TRadiobutton', foreground='green' if x['online'] else 'red')

				if   nameS.lower() in self.MissingNames:  self.style.configure(f'R{i}.TRadiobutton', foreground='purple1')
				elif nameS.lower() in self.StandoutNames: self.style.configure(f'R{i}.TRadiobutton', background='black')
				else:                                     self.style.configure(f'R{i}.TRadiobutton', background='turquoise' if changepage and nameS in test else '#F0F0F0')

				if not start:#print(self.raidolist)
					try:
						self.raidolist[i].config(text=nameS, style=f'R{i}.TRadiobutton')
					except Exception:
						rad = Radiobutton(self.RadFrame, text=nameS, style=f'R{i}.TRadiobutton', variable=self.selvar, value=i, command=self.sel)
						rad.grid(sticky='NW', column=column, row=row)
						self.raidolist.append(rad)
					#self.startbtn.config(state="normal")
					#self.Chat.config(state="normal")
					self.label2.config(foreground='black')
				else:
					rad = Radiobutton(self.RadFrame, text=nameS, style=f'R{i}.TRadiobutton', variable=self.selvar, value=i, command=self.sel)
					rad.grid(sticky='NW', column=column, row=row)
					rad.bind('<Button-2>', lambda e, rad=rad:self.chatlink(rad['text']))
					self.raidolist.append(rad)
			#if len(self.raidolist) - len(self.data) != 0:self.raidolist.reverse()
			#for i in reversed(range(len(self.raidolist) - len(self.data))):#for i in range(len(self.raidolist) - len(self.data)):
			#	self.raidolist[i].destroy()
		else:
			print(response.status)
			print()
			exitcount = 5
			while exitcount >= 0:
				os.system('cls')
				print('Picarto Python tkinter Interface')
				print(response)
				print()
				print('exiting in', exitcount)
				time.sleep(1)
				exitcount -= 1
			exit()

	def stream(self, file):
		print(file)
		who = self.name
		os.system(f'streamlink {file} best')
		print(f"{who} stopped {utilities.time_stamp('%Y-%m-%d %I:%M:%S %p')}")

	def sel(self, multi=False):
		nameindex = self.selvar.get()
		if not multi:
			#print(nameindex)
			self.name    = self.data[nameindex]['name']
			self.online  = self.data[nameindex]['online']
			self.channel = self.data[nameindex]['user_id']#['id']
		else:
			for i, x in enumerate(self.multivalue):
				#print(i, x, nameindex == x, self.multijson[i]['name'])
				if nameindex == x:
					self.name, self.channel = self.multijson[i]['name'], self.multijson[i]['user_id']
		self.style.configure(f'R{nameindex}.TRadiobutton', foreground='green' if self.online else 'red')

		if self.ncSwitch == 1:
			print(self.name)
			print(self.channel)
			self.ncSwitch = 0
		else:
			print(self.channel)
			print(self.name)
			self.ncSwitch = 1

		#url = self.genaricurl.format(self.name)
		self.url = f"https://picarto.tv/{self.name}"

		response = utilities.url_request(f"{self.genaricurl}/channel/name/{self.name}", utilities.generic_header({"ua":"m5"}))
		if response.status == 200:
			channel_url    = json.loads(response.read())
			#print(channel_url)
			self.NSFW      = channel_url['adult']
			self.title     = channel_url['title']
			self.game      = channel_url['gaming']
			avatarurl      = channel_url['avatar']
			self.view      = channel_url['viewers']
			self.online    = channel_url['online']
			self.private   = channel_url['private']
			self.lastlive  = channel_url['last_live']
			self.multijson = channel_url['multistream']
			title          = self.title.replace('"', '\\"')
			self.streamaugs['title'] = f'-t "{self.name} - {title}"'

			for i in [channel_url['thumbnails']['web'], channel_url['thumbnails']['tablet'], channel_url['thumbnails']['mobile'], channel_url['thumbnails']['web_large']]:
				response1 = utilities.url_request(i, utilities.generic_header({"ua":'m5'}))
				if response1.status == 200:
					self.thumbnaildata = response1.read()
					break
				else:
					print(response1.status)

			#response1 = utilities.url_request(channel_url['thumbnails']['tablet'], utilities.generic_header({"ua":'m5'}))
			#if response1.status == 200:
			#	self.thumbnaildata = response1.read()
			#else:
			#	print(response1.status)
			#	print('tablet thumbnail failed')
			#	print('trying web_large thumbnail instead')
			#	print()
			#	response2 = utilities.url_request(channel_url['thumbnails']['web_large'], utilities.generic_header({"ua":'m5'}))
			#	if response2.status == 200:
			#		self.thumbnaildata = response2.read()
			#	else:
			#		print(response2.status)
			#		print('web_large thumbnail failed')
			#		print('trying web thumbnail instead')
			#		print()
			#		response3 = utilities.url_request(channel_url['thumbnails']['web'], utilities.generic_header({"ua":'m5'}))
			#		if response3.status == 200:
			#			self.thumbnaildata = response3.read()
			#		else:
			#			print(response3.status)
			#			print('web thumbnail failed')
			#			print('using mobile thumbnail instead')
			#			print()
			#			response4 = utilities.url_request(channel_url['thumbnails']['mobile'], utilities.generic_header({"ua":'m5'}))
			#			if response4.status == 200:
			#				self.thumbnaildata = response4.read()

		elif response.status == 404:
			print(response.read())
			print('Account does not exist')
			print(f'{self.name} may have Disabled there Account')
			print()
		elif response.status == 523:
			print(response.read())
		#elif e.status == 522:print(e)
		else:
			print(traceback.format_exc())

		try:#print(self.cache)
			self.cache[self.name]["avatar"]
		except Exception:#print(traceback.format_exc())
			response = utilities.url_request(avatarurl, utilities.generic_header({"ua":'m5'}))
			if response.status == 200:
				self.avatardata = response.read()
			else:
				print(response.read())
			#self.cache.update({self.name:{"avatar":self.avatardata}})
			#print(avatarurl)
			#with open('image test.txt','w') as file :
			#	encodedtoken = str(avatardata)
			#	file.write(encodedtoken)
			#	file.close()

		self.config()
	# def IdentifyTAB(self, event):return self.note.tk.call(self.note._w, "identify", "tab", event.x, event.y)

	def videostart(self):
		response = utilities.url_request(f"{self.genaricurl}/channel/name/{self.name}/videos")

		if response.status == 200:
			self.videojson = json.loads(response.read())
			self.videojson.reverse()
			#print(self.videojson)
			column, row = -1, 0
			try:
				self.tabchild.destroy()
			except Exception:
				pass#print(traceback.format_exc())
			self.tabchild = Frame(self.VidFrame)
			self.tabchild.grid(column=0, row=0)
			raidoVlist = []
			for i in range(54, len(self.videojson)+54):
				column += 1
				if column >= 8:#9
					row += 1
					column=0

				#exec(f"self.rad{i} = Radiobutton(self.tabchild, text='video #{i}', variable=self.selvar, value={i}, command=self.videosel)")
				#exec(f"self.rad{i}.grid(sticky='NW', column={column}, row={row})")
				radvid = Radiobutton(self.tabchild, text=f'video #{i-54}', variable=self.selvar, value=i, command=self.videosel)
				radvid.grid(sticky='NW', column=column, row=row)
				raidoVlist.append(radvid)

	def videosel(self):
		videoindex = self.selvar.get()-54
		videothumb = self.videojson[videoindex]['thumbnails']['tablet']
		self.title = self.videojson[videoindex]['title']
		self.videofile = self.videojson[videoindex]['file']
		self.videostamp = self.videojson[videoindex]['timestamp']
		videoduration = self.videojson[videoindex]['duration']
		self.videofile = f"https://picarto.tv/{self.name}/videos/{self.videojson[videoindex]['id']}"
		response = utilities.url_request(videothumb, utilities.generic_header({"ua":'m5'}))
		if response.status == 200:
			self.thumbnaildata = response.read()
		title = self.title.replace('"', '\\"')
		self.streamaugs['title'] = f'-t "{self.name} - {title}"'

		runtime = utilities.time_since(datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(milliseconds=videoduration))
		self.duration.config(text=f'video duration: {runtime}')
		self.config()

	def openicon(self, event):
		if   event.num == 1:
			if self.onwhattab:
				linkicon = self.videofile
			else:
				linkicon = f'https://picarto.tv/{self.name}'
		elif event.num == 3:
			if self.onwhattab:
				linkicon = self.videofile.replace(f'{self.name}/videos', 'videopopout')
			else:
				linkicon = f'https://picarto.tv/streampopout/{self.name}/public'
		webbrowser.open(linkicon, new=1, autoraise=True)

	def config(self):
		if self.onwhattab:
			self.lastlive = self.videostamp.split(".")[0]
			self.tooltip.text = f"left click to open video\nright click to open video popout"
		else:
			self.tooltip.text = f"left click to open {self.name}'s profile\nright click to open stream popout"

		FWISO = datetime.datetime.fromisoformat(self.lastlive.replace(' ', 'T'))
		print(f'ISO {self.lastlive}')
		lastlive = utilities.time_amount(utilities.cut_convert(FWISO))
		#if self.onwhattab:
		#	videoindex = self.selvar.get()
		#	a = self.videojson[videoindex]["stream_name"]
		#	print(a)
		#	c = datetime.datetime.strptime(a.split("_")[1], "%Y.%m.%d.%H.%M.%S")
		#	print(c)
		#	since = utilities.time_since(utilities.cut_convert(FWISO), c)
		#else:
		since = utilities.time_since(utilities.cut_convert(FWISO))
		print(f"lastlive {lastlive}")
		print(f"live since {since}")


		for i in range(4 - len(self.multijson)): self.multijson.append({"user_id": None, "name": "Empty", "online": None, "adult": None})
		for i, (x, y) in enumerate(zip(self.multijson, [self.mul, self.mul1, self.mul2, self.mul3])):
			isempty = x['name'] != 'Empty'
			self.style.configure(f'M{i}.TRadiobutton', foreground='green' if x['online'] else 'red' if isempty else 'black')
			y.config(text=x['name'] if isempty else 'Empty')

		self.startbtn.config(state="normal" if self.onwhattab or self.online and not self.private else "disabled")
		self.note.tab(1, state="normal")
		self.Chat.config(state="normal")

		pos = self.selvar.get()
		if self.online:
			self.style.configure(f'R{pos}.TRadiobutton', foreground='green')
		else:
			self.style.configure(f'R{pos}.TRadiobutton', foreground='red')

		if self.private:
			self.style.configure(f'R{pos}.TRadiobutton', foreground='orange')
			self.label2.config(foreground='orange')
			#self.raidolist[pos].config(style=f'R{pos}.TRadiobutton')
		else:
			self.label2.config(foreground='black')
			#self.Chat.config(state="disabled")

		self.label.config(text=f"{self.name} is {'online' if self.online else 'offline'}")
		self.label1.config(text=f"NSFW is {self.NSFW}")#'NSFW' if self.NSFW else 'SFW'
		self.label2.config(text=f"Private is {self.private}")#, foreground='orange' if self.private else 'black')
		self.label3.config(text=f"Title: {self.title}")
		self.label4.config(text=f"Current viewers is \"{self.view}\"")
		self.label5.config(text=f"Game mode is {self.game}")
		#nl = '\n'
		#self.labelL.config(text=f"{f'Live for {since} or since{nl}' if self.online else 'Last Live '}{lastlive}")
		islive   = f"Live for {since} or since\n{lastlive}"
		#isvideo  = f"streamed on {lastlive}\nfor {since}"
		isofline = f"Last Live {lastlive}"
		self.labelL.config(text=islive if self.online else isofline)#and not self.onwhattab else isvideo if self.onwhattab 

		# set these last because if thay fail everything else will be set
		try:
			thumbnailim = Image.open(io.BytesIO(self.thumbnaildata))
			thumbnailimr = thumbnailim.resize((221, 124))
			self.thumbnailimg = ImageTk.PhotoImage(thumbnailimr)
			self.labelP.config(image=self.thumbnailimg)
		except Exception:
			self.labelP.config(image=self.defaultthumbnail)
			print(traceback.format_exc())

		try:
			try:
				self.labelI2.config(image=self.cache[self.name]["avatar"])
			except Exception:
				avatarim = Image.open(io.BytesIO(self.avatardata))
				avatarimr = avatarim.resize((100, 100))
				self.cache.update({self.name:{"avatar":ImageTk.PhotoImage(avatarimr)}})
				#print(self.cache)
				self.labelI2.config(image=self.cache[self.name]["avatar"])
		except Exception:print(traceback.format_exc())

	def Page(self, thepage):
		#if thepage:self.pagenum += 1
		#elif self.pagenum > 1:self.pagenum -= 1

		self.pagenum = thepage
		#for tabs in self.note.tabs():print(tabs)
		self.note.tab(tab_id=self.RadFrame, text=f'page {self.pagenum}')
		self.start(changepage=True)

	def menubarStart(self):
		self.menubar = tkinter.Menu(self.root)
		try:
			filemenu = tkinter.Menu(self.menubar, tearoff=0)
			#filemenu.add_command(label="Previous Page", command=lambda:self.Page(False))
			#filemenu.add_command(label="Next Page",     command=lambda:self.Page(True))
			filemenu.add_command(label="Page 1", command=lambda:self.Page(1))
			filemenu.add_command(label="Page 2", command=lambda:self.Page(2))
			filemenu.add_command(label="Page 3", command=lambda:self.Page(3))
			filemenu.add_command(label="Page 4", command=lambda:self.Page(4))
			filemenu.add_command(label="Page 5", command=lambda:self.Page(5))
			filemenu.add_command(label="Page 6", command=lambda:self.Page(6))
			filemenu.add_command(label="Page 7", command=lambda:self.Page(7))
			filemenu.add_command(label="Page 8", command=lambda:self.Page(8))
			filemenu.add_command(label="Page 9", command=lambda:self.Page(9))
			filemenu.add_command(label="Page 10", command=lambda:self.Page(10))
			self.menubar.add_cascade(label="Change Page", menu=filemenu)

			self.menubar.add_command(label="Online True", command=self.SO)#, cursor='hand2'

			augmenu = tkinter.Menu(self.menubar, tearoff=0)
			loglevel = tkinter.Menu(augmenu, tearoff=0)
			loglevel.add_command(label="None",    command=lambda: self.loglevel('None'))
			loglevel.add_command(label="error",   command=lambda: self.loglevel('error'))
			loglevel.add_command(label="warning", command=lambda: self.loglevel('warning'))
			loglevel.add_command(label="info",    command=lambda: self.loglevel('info'))
			loglevel.add_command(label="debug",   command=lambda: self.loglevel('debug'))
			loglevel.add_command(label="trace",   command=lambda: self.loglevel('trace'))

			ppt = tkinter.Menu(augmenu, tearoff=0)
			ppt.add_command(label='None', command=lambda:self.playerPT(None))
			ppt.add_command(label='hls',  command=lambda:self.playerPT('hls'))
			ppt.add_command(label='mp4',  command=lambda:self.playerPT('mp4'))
			ppt.add_command(label='http', command=lambda:self.playerPT('http'))

			augmenu.add_cascade(label="player-passthrough=None", menu=ppt)
			augmenu.add_command(label=f'player-continuous-http={self.pchbool}', command=self.playerCH)
			augmenu.add_command(label='hls-live-edge=3', command=self.playerHLE)
			augmenu.add_command(label=f'hls-segment-stream-data={self.PHttp}', command=self.playerhssd)
			augmenu.add_command(label=f'player-http={self.PHttp}', command=self.playerHttp)
			augmenu.add_command(label=f'player-fifo={self.Pfifo}', command=self.playerFI)
			augmenu.add_command(label='ringbuffer-size 50M', command=self.playerRBF)
			augmenu.add_cascade(label="loglevel None", menu=loglevel)

			picarto_server = tkinter.Menu(augmenu, tearoff=0)
			picarto_server.add_command(label='None',       command=lambda: self.switch_server('None'))
			picarto_server.add_command(label='newyork',    command=lambda:self.switch_server('edge1-us-newyork'))
			picarto_server.add_command(label='losangeles', command=lambda:self.switch_server('edge1-us-losangeles'))
			picarto_server.add_command(label='dallas',     command=lambda:self.switch_server('edge1-us-dallas'))
			picarto_server.add_command(label='dallas 1',   command=lambda:self.switch_server('1-edge1-us-dallas'))
			picarto_server.add_command(label='miami',      command=lambda:self.switch_server('edge1-us-miami'))
			augmenu.add_cascade(label="picarto server", menu=picarto_server)

			blank = tkinter.Menu(augmenu, tearoff=0)
			blank.add_command(label='blank')#, command=lambda:self.playerPT(None)
			augmenu.add_cascade(label="blank", menu=blank)
			self.menubar.add_cascade(label="stream augments", menu=augmenu)

			#print(self.menubar.entryconfigure(2)
			#self.menubar.add_command(label="SFW is False", command=self.nsfw)
		except Exception:
			print(traceback.format_exc())
		self.menubar.add_command(label="Refresh Streams", command=self.start)
		self.root.config(menu=self.menubar)

	def switch_server(self, event):
		self.url = f"https://{event}.picarto.tv/stream/hls/golive+{self.name}/index.m3u8"
		if event == 'None':
			self.url = f"https://picarto.tv/{self.name}"
	def loglevel(self, event):
		level = f"--loglevel {event}"
		self.streamaugs['level'] = level
		self.menubar.winfo_children()[1].entryconfigure(7, label=f"{level[2:]}")
		if event == 'None': del self.streamaugs['level']
		print(self.streamaugs)
	def playerRBF(self):
		#toplevel = tkinter.Toplevel()
		newframe = Frame(self.note)
		newtab =  self.note.add(newframe, text="ringbuffer-size")
		self.note.select(newtab)
		Label(newframe, text='''The maximum size of the ringbuffer. Mega- or kilobytes can be specified via the M or K suffix respectively.

The ringbuffer is used as a temporary storage between the stream and the player. 
This allows Streamlink to download the stream faster than the player which reads the data from the ringbuffer.

The smaller the size of the ringbuffer, the higher the chance of the player buffering if the download speed decreases, 
and the higher the size, the more data can be use as a storage to recover from volatile download speeds.

Most players have their own additional cache and will read the ringbuffer's content as soon as data is available. 
If the player stops reading data while playback is paused, 
Streamlink will continue to download the stream in the background as long as the ringbuffer doesn't get full.''').grid(sticky='N', column=0, row=0, columnspan=4)
		derent = Spinbox(newframe, from_=0, to=2147483647, width=15, command=lambda:derent.selection_clear())
		Label(newframe, text="\nthe upper limit 2,147,483,647 so dont try and scroll to it").grid(sticky='WN', column=0, row=1, columnspan=4)
		derent.set('50')
		derent.bind('<KeyRelease>', lambda e: self.max_value(e, 2147483647))
		#derent.bind('<B1-Motion>', self.spin_drag)
		trgtbtn = Button(newframe, width=5, text="ok", command=lambda:self.RBF(newframe, int(derent.get())))
		derent.grid(sticky='NE', column=1, row=2)
		trgtbtn.grid(sticky='NW', column=2, row=2)
	def RBF(self, TP, event):
		rbf = f"--ringbuffer-size {event}M"
		self.streamaugs['rbf'] = rbf
		self.menubar.winfo_children()[1].entryconfigure(6, label=rbf[2:])
		if event == 50: del self.streamaugs['rbf']
		TP.destroy()
	def playerHLE(self):
		#toplevel = tkinter.Toplevel()
		newframe = Frame(self.note)
		newtab =  self.note.add(newframe, text="hls-live-edge")
		self.note.select(newtab)
		Label(newframe, text="""Number of segments from the live stream's current live position to begin streaming.
The size or length of each segment is determined by the streaming provider.

Lower values will decrease the latency, but will also increase the chance of buffering,
as there is less time for Streamlink to download segments and write their data to the output buffer.""").grid(sticky='N', column=0, row=0, columnspan=4)
		Label(newframe, text="\nthe upper limit 2,147,483,647 so dont try and scroll to it").grid(sticky='WN', column=0, row=1, columnspan=4)
		derent = Spinbox(newframe, from_=0, to=2147483647, width=15, validate='key', validatecommand=self.vcmd, command=lambda:derent.selection_clear())
		derent.set(3)
		derent.bind('<KeyRelease>', lambda e: self.max_value(e, 2147483647))
		#derent.bind('<B1-Motion>', self.spin_drag)
		trgtbtn = Button(newframe, width=5, text="ok", command=lambda:self.HLE(newframe, int(derent.get())))
		derent.grid(sticky='NE', column=1, row=2)
		trgtbtn.grid(sticky='NW', column=2, row=2)
	def max_value(self, event, maxvalue):
		widget = event.widget
		value = int(widget.get())
		#print(value)
		#print(maxvalue)
		if value > maxvalue:
			value = maxvalue
		widget.set(value)
	#def spin_drag(self, event):
	#	old = int(event.widget.get())
	#	new = old + 1 if not old > event.y else -1
	#	event.widget.set(new)
	#	if new < 0 : event.widget.set(0)
	def HLE(self, TP, event):
		hle = f"--hls-live-edge={event}"
		self.streamaugs['hle'] = hle
		self.menubar.winfo_children()[1].entryconfigure(2, label=hle[2:])
		if event == 3:
			del self.streamaugs['hle']
		TP.destroy()
	def playerHttp(self):
		self.PHttp = False if self.PHttp else True
		PHttp = '--player-http'
		self.streamaugs['PHttp'] = PHttp
		self.menubar.winfo_children()[1].entryconfigure(4, label=f"{PHttp[2:]}={self.PHttp}")
		if not self.PHttp:
			del self.streamaugs['PHttp']
	def playerhssd(self):
		self.hssd = False if self.hssd else True
		hssd = '--hls-segment-stream-data'
		self.streamaugs['hssd'] = hssd
		self.menubar.winfo_children()[1].entryconfigure(3, label=f"{hssd[2:]}={self.hssd}")
		if not self.hssd:
			del self.streamaugs['hssd']
	def playerFI(self):
		self.Pfifo = False if self.Pfifo else True
		pfi = '--fifo'
		self.streamaugs['pfi'] = pfi
		self.menubar.winfo_children()[1].entryconfigure(5, label=f"player-fifo={self.Pfifo}")
		if not self.Pfifo:
			del self.streamaugs['pfi']
	def playerPT(self, event):
		ppt = f'--player-passthrough={event}'
		self.streamaugs['ppt'] = ppt
		self.menubar.winfo_children()[1].entryconfigure(0, label=ppt[2:])
		if not event:
			del self.streamaugs['ppt']
	def playerCH(self):
		self.pchbool = False if self.pchbool else True
		pch = '--player-continuous-http'
		self.streamaugs['pch'] = pch
		self.menubar.winfo_children()[1].entryconfigure(1, label=f"{pch[2:]}={self.pchbool}")
		if not self.pchbool:
			del self.streamaugs['pch']
	def SO(self):
		self.LiveFirst = False if self.LiveFirst else True
		self.menubar.entryconfig(2, label=f'Online {self.LiveFirst}')
		self.start()
	def nsfw(self):
		self.FWrating = False if self.FWrating else True
		self.menubar.entryconfig(3, label=f'SFW is {not self.FWrating}')
		#if self.FWrating:
		#	self.FWrating = False
		#	#print(self.FWrating)
		#	self.menubar.entryconfig(3, label=f'SFW is {not self.FWrating}')
		#else:
		#	self.FWrating = True
		#	#print(self.FWrating)
		#	self.menubar.entryconfig(3, label=f'SFW is {not self.FWrating}')
		print(f'SFW is {self.FWrating}')
		#self.start()
	def change(self, event):
		print(self.note.index(self.note.select()))
		if self.note.index(self.note.select()) == 0:
			self.onwhattab = False
			self.duration.config(text='')
			self.startbtn.config(text='Start Stream', command=lambda:self.start_thread(0))
			try:
				self.tooltip.text = f"left click to open {self.name}'s profile\nright click to open stream popout"
			except:
				pass
		if self.note.index(self.note.select()) == 1:
			self.onwhattab = True
			self.startbtn.config(text='Start Video', command=lambda:self.start_thread(1))
			self.duration.config(text='video duration: NA')
			self.tooltip.text = f"left click to open video\nright click to open video popout"
			self.videostart()

	def HeaderFormat(self, args):
		Headers = {}
		for k, v in args.items():
			if 'auth'     in k: key = 'Authorization'
			if 'bearer'   in v: value = f"Bearer {self.auth}"

		Headers[key] = value
		return Headers
	def subsrt(self):
		try:
			try:
				uri = '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'
				decodedavatarimg = Image.open(io.BytesIO(base64.b64decode(uri)))
				iconimg = ImageTk.PhotoImage(decodedavatarimg)
				avatarimr = decodedavatarimg.resize((100, 100))
				self.defaultavatar = ImageTk.PhotoImage(avatarimr)
			except Exception:pass
			try:
				uri = 'iVBORw0KGgoAAAANSUhEUgAAATYAAACuCAYAAAC8/iEzAAAABGdBTUEAALGPC/xhBQAAAAlwSFlzAAAOwAAADsABataJCQAAABZ0RVh0U29mdHdhcmUAcGFpbnQubmV0IDQuMUzvxf8AAAP+SURBVHhe7dSxbRxBEERR5aUclAQzZyIUaBAYLWpue5YgBBSe8Zy77p61/q/ff94+AJoIG1BH2IA6wgbcen9//0eaWV3nJ9Kdp4QN2EoBWp3OT1xvPiFswFYKz+p0fup695SwAVEKTnI6P7V+yylhA6IUm+R0/sT6PSeEDYhSaJLT+VPrN00JGxClyCSn80+s3zUhbECUApM82Tm1vjEhbECUApM82XlifeeOsAFRikvynd0T6Z0dYQOiFJck7U6kW6+kGzvCBkQpLknanUr3dtL+jrABUYpLknan0r2dtL8jbECU4pKk3al0byft7wgbEKW4JGl3It16Jd3YETYgSnFJvrN7Ir2zI2xAlOKSPNl5Yn3njrABUYpL8mTn1PrGhLABUQpMcjr/xPpdE8IGRCkwyen8qfWbpoQNiFJkktP5E+v3nBA2IEqhSU7np9ZvOSVsQJRikzzZubPefELYgCgFJ3my88p67ylhA6IUneQ7u6t05ylhA6IUnyTt/m/CBkQpYsnp/Gp972o6lwgbEK1heeVkNrm+u7uX5naEDYhSXJKT2eT67u5emtsRNiBKcUlOZncm764zd4QNiFJcktP55O7d9f8JYQOiFJhkuvvqv093/50QNiBKgUmmu5P/d7+fEjYgSpFJprt3/++se1PCBkQpMsl0dzJzdd2ZEjYgSqFJpruTmavrzpSwAVEKTTLdnc59SfNTwgZspeCs0s6n6Wya+5Lmp4QN2ErBWaWdTz81OyVswK0n4TmZP5mdEDagjrABdYQNqCNsQB1hA+oIG1BH2IA6wgbUETagjrABdYQNqCNsQB1hA+oIG1BH2IA6wgbUETagjrABdYQNqCNsQB1hA+oIG1BH2IA6wgbUETagjrABdYQNqCNsQB1hA+oIG1BH2IA6wgbUETagjrABdYQNqCNsQB1hA+oIG1BH2IA6wgbUETagjrABdYQNqCNsQB1hA+oIG1BH2IA6wgbUETagjrABdYQNqCNsQB1hA+oIG1BH2IA6wgbUETagjrABdYQNqCNsQB1hA+oIG1BH2IA6wgbUETagjrABdYQNqCNsQB1hA+oIG1BH2IA6wgbUETagjrABdYQNqCNsQB1hA+oIG1BH2IA6wgbUETagjrABdYQNqCNsQB1hA+oIG1BH2IA6wgbUETagjrABdYQNqCNsQB1hA+oIG1BH2IA6wgbUETagjrABdYQNqCNsQB1hA+oIG1BH2IA6wgbUETagjrABdYQNqCNsQB1hA+oIG1BH2IA6wgbUETagjrABdYQNqCNsQB1hA+oIG1BH2IA6wgbUETagjrABdYQNqCNsQB1hA+oIG1BH2IA6wgbUETagjrABdYQNKPP28Rd02U3wldOAaAAAAABJRU5ErkJggg=='
				decodedthumbnailimg = Image.open(io.BytesIO(base64.b64decode(uri)))
				thumbnailimr = decodedthumbnailimg.resize((221, 124))
				self.defaultthumbnail = ImageTk.PhotoImage(thumbnailimr)
			except Exception:pass
		except Exception:
			print(traceback.format_exc())

		self.note = Notebook(self.root)
		self.RadFrame = Frame(self.note, borderwidth=2, relief='sunken')#self.tab1
		self.VidFrame = Frame(self.note)
		self.note.add(self.RadFrame, text="page 1")#self.tab1
		self.note.add(self.VidFrame, text="videos")
		self.note.grid(sticky='S', row=8)
		self.note.bind("<<NotebookTabChanged>>", self.change)

		#self.RadFrame = Frame(self.tab1, borderwidth=2, relief='sunken')
		self.multiFrame = tkinter.LabelFrame(self.root, text='Multistream', relief='sunken')
		#self.RadFrame.grid(sticky='S', row=8)
		self.multiFrame.grid(sticky='SW', row=9)

		self.label = Label(self.root, text="Name")
		self.label1 = Label(self.root, text="NSFW")
		self.label2 = Label(self.root, text="Private")
		self.label3 = Label(self.root, text="Title")
		self.label4 = Label(self.root, text="Current viewers")
		self.label5 = Label(self.root, text="Game mode")
		#self.label6 = Label(self.multiFrame, text="Multistream:")

		self.labelF = Label(self.root, text="Follows online")
		self.duration = Label(self.root)
		self.labelI2 = Label(self.root, image=self.defaultavatar)
		self.labelI2.bind("<Button-1>", self.openicon)
		self.labelI2.bind("<Button-3>", self.openicon)
		self.tooltip = custom.HoverInfo.Tooltip(self.labelI2, bg='white', move_with_cursor=True)#click to open a web page to 
		self.labelP = Label(self.root, image=self.defaultthumbnail)
		self.labelL = Label(self.root, text="Last Live")

		self.root.iconphoto(self.root, iconimg)
		#self.root.config(bg='#243299')
		self.label.grid(sticky='NE', column=0, row=1)
		self.label1.grid(sticky='NE', column=0, row=2)
		self.label2.grid(sticky='NE', column=0, row=3)
		self.label3.grid(sticky='NW', column=0, row=1)
		self.label4.grid(sticky='NW', column=0, row=3)
		self.label5.grid(sticky='NW', column=0, row=2)
		#self.label6.grid(sticky='NW', column=0, row=0)

		self.labelF.grid(sticky='SE', column=0, row=7)
		self.duration.grid(sticky='SW', column=0, row=7)
		self.labelI2.grid(sticky='NW', column=0, row=6)
		self.labelP.grid(sticky='NE', column=0, row=6)
		self.labelL.grid(sticky='NE', column=0, row=4)

		self.chatlink = lambda e:webbrowser.open(f'https://picarto.tv/chatpopout/{e}/public', new=1, autoraise=True)
		self.Chat = Button(self.root, text="Open Chat", command=lambda:self.chatlink(self.name))#lambda:start_thread(34)
		self.startbtn = Button(self.root, text="Start Stream")#, command=lambda:self.start_thread(0)
		#refresh = Button(self.root, text="Refresh Streams", command=self.start)

		self.Chat.grid(sticky='SW', column=0, row=6)
		#refresh.grid(sticky='SW', column=0, row=5)
		self.startbtn.grid(sticky='NW', column=0, row=0)

		self.startbtn.config(state="disabled")
		self.Chat.config(state="disabled")
		self.note.tab(self.VidFrame, state="disabled")

		self.mul  = Radiobutton(self.multiFrame, text=self.multi,  style='M0.TRadiobutton', variable=self.selvar, value=self.multivalue[0], command=lambda: self.sel(True))
		self.mul1 = Radiobutton(self.multiFrame, text=self.multi1, style='M1.TRadiobutton', variable=self.selvar, value=self.multivalue[1], command=lambda: self.sel(True))
		self.mul2 = Radiobutton(self.multiFrame, text=self.multi2, style='M2.TRadiobutton', variable=self.selvar, value=self.multivalue[2], command=lambda: self.sel(True))
		self.mul3 = Radiobutton(self.multiFrame, text=self.multi3, style='M3.TRadiobutton', variable=self.selvar, value=self.multivalue[3], command=lambda: self.sel(True))
		self.mul.grid(sticky='NW', column=0, row=0)
		self.mul1.grid(sticky='NW', column=1, row=0)
		self.mul2.grid(sticky='NW', column=2, row=0)
		self.mul3.grid(sticky='NW', column=3, row=0)

if __name__ == "__main__":
	Picarto()
