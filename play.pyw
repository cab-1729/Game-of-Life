from tkinter import *
from threading import Thread
from itertools import product
from pyautogui import size
import pygame
import os
import shelve
colors={
    'white':(255,255,255),
    'alice blue':(240,248,255),
    'grey':(169,169,169),
    'black':(0,0,0),
    'medium orchid':(186,85,211),
    'deep pink':(255,20,147),
    'dark orchid':(153,50,204),
    'deep blue':(0,0,255),
    'cyan':(0,255,255),
    'dark cyan':(0,139,139),
    'chartreuse':(127,255,0),
    'forest green':(34,139,34),
    'light green':(144,238,144),
    'yellow':(255,255,0),
    'khaki':(240,230,140),
    'gold':(255,215,0),
    'orange':(255,165,0),
    'light salmon':(255,160,122),
    'tomato':(255,99,71),
    'red':(255,0,0),
    'dark red':(139,0,0),
    'fire brick':(178,34,34),
}
#common env
color_ops=list(colors.keys())
dead_color=colors['white']
alive_color=colors['black']
grid_color=colors['grey']
fps=10
width,height=size()
thicknesses=()
size_each='__________ '
#boolean communication
show_grid=True
living=False
stop_rendering=False
stepping=False
#-----------------------------
class Cell(pygame.sprite.Sprite):
	sizes=(5,8,10,20,50,100)
	gap=1
	side=10
	tbk=[]
	tbb=[]
	rows=(height//(gap+side))+1
	columns=(width//(gap+side))+1
	all_cells=[]
	@staticmethod
	def elem_clicked(p):
		x,y=p
		r=(y//(Cell.side+Cell.gap))
		c=(x//(Cell.side+Cell.gap))
		return grid[r][c]
	@classmethod
	def life_or_death(cls):
		for i in cls.tbk:i.die()
		for i in cls.tbb:i.be_born()
		cls.tbk=[]
		cls.tbb=[]
	def __init__(self,arg1,arg2):
		pygame.sprite.Sprite.__init__(self)
		self.image=pygame.Surface((Cell.side,Cell.side))
		self.alive=False
		self.image.fill(alive_color if self.alive else dead_color)
		self.rect=self.image.get_rect()
		self.row=arg1
		self.column=arg2
		y=self.row*(Cell.gap+Cell.side)
		x=self.column*(Cell.gap+Cell.side)
		self.rect.x,self.rect.y=x,y
		self.neighbours=[]
		self.get_neighbours()
		Cell.all_cells.append(self)
	def should_die(self):
		alive_neighbours=0
		for n in self.neighbours:
			if grid[n[0]][n[1]].alive:
				alive_neighbours+=1
		if alive_neighbours<2 or alive_neighbours>3:#death by isolation and overpopulation
			return True
	def should_be_born(self):
		alive_neighbours = 0
		for n in self.neighbours:
			if grid[n[0]][n[1]].alive:
				alive_neighbours += 1
		if alive_neighbours==3:
			return True
	def be_born(self):
		self.alive=True
		self.image.fill(alive_color)
	def die(self):
		self.alive=False
		self.image.fill(dead_color)
	def get_neighbours(self):
		ces=[i for i in(self.column,self.column+1,self.column-1) if i>-1 and i<Cell.columns+1]
		res=[i for i in (self.row,self.row+1,self.row-1) if i>-1 and i<Cell.rows+1]
		self.neighbours=list(product(res,ces))
		own_address=(self.row,self.column)
		if own_address in self.neighbours:self.neighbours.remove(own_address)
	def __repr__(self):return ('Alive' if self.alive else 'Dead'+' cell at '+str(self.row)+','+str(self.column))
#------------------------
#functions
def change_color_d(*args):
	global dead_color
	dead_color=colors[str(dc.get())]
	for i in Cell.all_cells:
		if not i.alive:
			i.die()
def change_color_a(*args):
	global alive_color
	alive_color=colors[str(ac.get())]
	for i in Cell.all_cells:
		if i.alive:
			i.be_born()
def change_color_l(*args):
	global grid_color
	grid_color=colors[str(lc.get())]
def change_grid():
	global show_grid
	show_grid=not show_grid
	if show_grid:
		grid_changer.configure(text='Hide grid')
	else:
		grid_changer.configure(text='Show grid')
def increase_size():
	pause()
	global grid,stop_rendering
	stop_rendering=True
	former_state=[]
	for i in range(Cell.rows+1):
		t=[]
		for j in range(Cell.columns+1):
			if grid[i][j].alive:
				t.append(1)
			else:
				t.append(0)
		former_state.append(t)
	Cell.side=Cell.sizes[Cell.sizes.index(Cell.side)+1]
	Cell.rows=(height//(Cell.gap+Cell.side))+1
	Cell.columns=(width//(Cell.gap+Cell.side))+1
	# creation
	for cell in Cell.all_cells:
		cell.kill()
		del cell
	Cell.all_cells=[]
	grid=[]
	for r in range(Cell.rows+1):
		t=[]
		for c in range(Cell.columns+1):
			temp=Cell(r, c)
			t.append(temp)
			all_sprites.add(temp)
			if former_state[r][c]==1:
				temp.be_born()
		grid.append(t)
	if Cell.side==Cell.sizes[-1]:
		size_plus_button.configure(state='disabled')
	elif Cell.side==Cell.sizes[1]:
		size_minus_button.configure(state='active')
	size_disp.configure(text=size_each*Cell.sizes.index(Cell.side))
	stop_rendering=False
def decrease_size():
	pause()
	global grid,stop_rendering
	stop_rendering=True
	former_state=[]
	for i in range(Cell.rows+1):
		t=[]
		for j in range(Cell.columns+1):
			if grid[i][j].alive:
				t.append(1)
			else:
				t.append(0)
		former_state.append(t)
	Cell.side=Cell.sizes[Cell.sizes.index(Cell.side)-1]
	Cell.rows=(height//(Cell.gap+Cell.side))+1
	Cell.columns=(width//(Cell.gap+Cell.side))+1
	#creation
	for cell in Cell.all_cells:
		cell.kill()
		del cell
	Cell.all_cells=[]
	grid=[]
	for r in range(Cell.rows+1):
		t=[]
		for c in range(Cell.columns+1):
			temp=Cell(r,c)
			t.append(temp)
			all_sprites.add(temp)
			try:
				if former_state[r][c]==1:
					temp.be_born()
			except IndexError:
				continue
		grid.append(t)
	if Cell.side==Cell.sizes[0]:
		size_minus_button.configure(state='disabled')
	elif Cell.side==Cell.sizes[-2]:
		size_plus_button.configure(state='active')
	size_disp.configure(text=size_each*Cell.sizes.index(Cell.side))
	stop_rendering=False
def step():
	global stepping
	stepping=True
def pause():
	global living
	step_button.configure(state='active')
	p_button.configure(text='Play >')
	living=False
def play():
	global living
	step_button.configure(state='disabled')
	p_button.configure(text='Pause ||')
	living=True
def change_pause_stat():
	if living:
		pause()
	else:
		play()
def reset():
	pause()
	for cell in Cell.all_cells:
		if cell.alive:
			cell.die()
def save(*args):
	pause()
	name=str(save_entry.get())
	if name.replace(' ','')=='':
		save_entry.insert(0,'no name given')
		return
	save_entry.delete(0,END)
	rf=os.getcwd()
	nf=rf+'\\Saved\\'+name
	if not os.path.exists(nf):
		os.makedirs(nf)
	pygame.image.save(screen,nf+'\\screen.png')
	alive_cells=[(i.row,i.column) for i in Cell.all_cells if i.alive]
	with shelve.open(nf+'\\'+name) as game_save:
		game_save['dead color']=str(dc.get())
		game_save['alive color']=str(ac.get())
		game_save['grid color']=str(lc.get())
		game_save['living cells']=cur_state
		game_save['size']=Cell.side
		game_save['grid shown']=show_grid
def load(*args):
	pause()
	global dead_color,alive_color,grid_color,show_grid,stop_rendering,grid
	stop_rendering=True
	name=str(load_entry.get())
	if name.replace(' ','')=='':
		load_entry.insert(0,'no name given')
		return
	load_entry.delete(0,END)
	rf=os.getcwd()
	nf=rf+'\\Saved\\'+name
	if not os.path.exists(nf):
		load_entry.insert(0,'not found name')
	with shelve.open(nf+'\\'+name) as game_save:
		c1=game_save['dead color']
		c2=game_save['alive color']
		c3=game_save['grid color']
		dead_color=colors[game_save['dead color']]
		alive_color=colors[game_save['alive color']]
		grid_color=colors[game_save['grid color']]
		birth=game_save['living cells']
		show_grid=game_save['grid shown']
		Cell.side=game_save['size']
	dead_color=colors[c1];alive_color=colors[c2];grid_color=colors[c3]
	#remove original
	Cell.rows=(height//(Cell.gap+Cell.side))+1
	Cell.columns=(width//(Cell.gap+Cell.side))+1
	for cell in Cell.all_cells:
		cell.kill()
		del cell
	Cell.all_cells=[]
	#create new
	grid=[]
	for r in range(Cell.rows+1):
		t=[]
		for c in range(Cell.columns+1):
			temp=Cell(r,c)
			t.append(temp)
			all_sprites.add(temp)
			address=(r,c)
			if address in birth:
				temp.be_born()
		grid.append(t)
	#change interface
	if show_grid:grid_changer.configure(text='Hide grid')
	else:grid_changer.configure(text='Show grid')
	size_disp.configure(text=size_each*Cell.sizes.index(Cell.side))
	if Cell.side==Cell.sizes[-1]:size_plus_button.configure(state='disabled')
	else:size_plus_button.configure(state='active')
	if Cell.side==Cell.sizes[0]:size_minus_button.configure(state='disabled')
	else:size_minus_button.configure(state='active')
	dc.set(c1);ac.set(c2);lc.set(c3)
	stop_rendering=False
def go_down(*args):load_entry.focus()
def go_up(*args):save_entry.focus()
#-------------
#threads
def gui_thread():
	control=Tk()
	global dc,ac,lc,p_button,grid_changer,save_entry,load_entry,size_plus_button,size_minus_button,size_disp,step_button
	dc,ac,lc=StringVar(),StringVar(),StringVar()
	dc.set('white');ac.set('black');lc.set('grey')
	control.title('Conway\'s Game of Life')
	control.iconbitmap('Deps\\My face.ico')
	control.resizable(False,False)
	r=0
	p_button=Button(control,text='Play >',command=change_pause_stat)
	p_button.grid(row=r,columnspan=4);r+=1
	grid_changer=Button(control,text='Hide grid',command=change_grid)
	grid_changer.grid(row=r,columnspan=4);r+=1
	step_button=Button(control,text='Next gen',command=step)
	step_button.grid(row=r,columnspan=4);r+=1
	Button(control,text='Reset',command=reset).grid(row=r,columnspan=4);r+=1
	Label(control,text='Color : ').grid(row=r,column=0)
	Label(control,text='Alive').grid(row=r,column=1)
	Label(control,text='Dead').grid(row=r,column=2)
	Label(control,text='Grid').grid(row=r,column=3)
	r+=1
	OptionMenu(control,ac,*color_ops,command=change_color_a).grid(row=r,column=1)
	OptionMenu(control,dc,*color_ops,command=change_color_d).grid(row=r,column=2)
	OptionMenu(control,lc,*color_ops,command=change_color_l).grid(row=r,column=3)
	r+=1
	Label(control,text='Box size : ').grid(row=r,column=0)
	size_plus_button=Button(control,text='+',command=increase_size)
	size_plus_button.grid(row=r,column=2)
	size_minus_button=Button(control,text='-',command=decrease_size)
	size_minus_button.grid(row=r,column=3)
	r+=1
	size_disp=Label(control,text=size_each*Cell.sizes.index(Cell.side))
	size_disp.grid(row=r,columnspan=4,sticky=W)
	r+=1
	save_entry=Entry(control)
	save_entry.grid(row=r,column=0,columnspan=3)
	Button(control,text='Save',command=save).grid(row=r,column=3)
	save_entry.bind('<Return>',save);save_entry.bind('<Down>',go_down)
	r+=1
	load_entry=Entry(control)
	load_entry.grid(row=r,column=0,columnspan=3)
	Button(control,text='Load',command=load).grid(row=r,column=3)
	load_entry.bind('<Return>',load);load_entry.bind('<Up>',go_up)
	control.mainloop()
def game_thread():
	global screen,grid,living,all_sprites,stepping
	pygame.init()
	screen=pygame.display.set_mode((0,0),pygame.RESIZABLE)
	pygame.display.set_caption('Conway\'s Game of Life')
	clock=pygame.time.Clock()
	all_sprites=pygame.sprite.Group()
	#creation
	grid=[]
	for r in range(Cell.rows+1):
		t=[]
		for c in range(Cell.columns+1):
			temp=Cell(r,c)
			all_sprites.add(temp)
			t.append(temp)
		grid.append(t)
	#game loop
	b=False
	while True:
		#time
		clock.tick(fps)
		#event
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				b=True
				break
			elif event.type==pygame.MOUSEBUTTONDOWN:
				cell_clicked=Cell.elem_clicked(pygame.mouse.get_pos())
				cell_clicked.alive=not cell_clicked.alive
				cell_clicked.be_born() if cell_clicked.alive else cell_clicked.die()
		if b:break
		#next generation
		if living or stepping:
			for cell in Cell.all_cells:
				if cell.should_be_born():cell.tbb.append(cell)
				elif cell.should_die():Cell.tbk.append(cell)
			Cell.life_or_death()
			if stepping:stepping=False
		if not stop_rendering:
			#update
			all_sprites.update()
			#render
			screen.fill(grid_color if show_grid else dead_color)
			all_sprites.draw(screen)
			#flip
			pygame.display.flip()
#----------------------
#run
if __name__=='__main__':
	life_game=Thread(target=game_thread)
	life_game.start()
	gui_thread()