from tkinter import *
from threading import Thread
from itertools import product
from pyautogui import size
import pygame
import os
import shelve
from sys import exit
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
    'charteuse':(127,255,0),
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
fps=50
height,width=size()
thicknesses=()
show_grid=True
living=False
class Cell(pygame.sprite.Sprite):
	gap=1
	side=10
	tbk=[]
	tbb=[]
	rows=(height//(gap+side))+1
	columns=(width//(gap+side))+1
	all_cells=[]
	@staticmethod
	def elem_clicked(p):
		y,x=p
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
		self.alive=plan[arg1][arg2]=='1'
		self.image.fill(alive_color if self.alive else dead_color)
		self.rect=self.image.get_rect()
		self.row=arg1
		self.column=arg2
		y=self.column*(Cell.gap+Cell.side)
		x=self.row*(Cell.gap+Cell.side)
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
plan=[['0' for _ in range(Cell.columns+1)] for __ in range(Cell.rows+1)]
#------------------------
#functions
def display_text(text,font,size,color,x,y):
    font_name=pygame.font.match_font(font,bold=20)
    font=pygame.font.Font(font_name,size)
    text_surface=font.render(text,True,color)
    text_rect=text_surface.get_rect()
    text_rect.x,text_rect.y=(x,y)
    screen.blit(text_surface,text_rect)
def change_color_d(*args):
	global dead_color
	print('dead_change')
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
def pause():
	global living,p_button
	p_button.configure(text='Play >')
	living=False
def play():
	global living,p_button
	p_button.configure(text='Pause ||')
	living=True
def change_pause_stat():
	if living:
		pause()
	else:
		play()
def reset():
	for cell in Cell.all_cells:
		det=plan[cell.row][cell.column]
		if det=='0' and cell.alive:
			cell.die()
		elif det=='1' and not cell.alive:
			cell.be_born()
	pause()
def save():
	cur_state=[['0' for _ in range(Cell.columns+1)] for __ in range(Cell.rows+1)]
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
	for cell in Cell.all_cells:
		if cell.alive:
			cur_state[cell.row][cell.column]='1'
		else:
			cur_state[cell.row][cell.column]='0'
	with shelve.open(nf+'\\'+name) as game_save:
		game_save['dead color']=str(dc.get())
		game_save['alive color']=str(ac.get())
		game_save['grid color']=str(lc.get())
		game_save['state']=cur_state
def load():
	global plan,dead_color,alive_color,grid_color
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
		dead_color=colors[game_save['dead color']]
		alive_color=colors[game_save['alive color']]
		grid_color=colors[game_save['grid color']]
		plan=game_save['state']
	reset()
	plan=[['0' for _ in range(Cell.columns+1)] for __ in range(Cell.rows+1)]
#-------------
#threads
def gui_thread():
	control=Tk()
	global dc,ac,lc,p_button,grid_changer,save_entry,load_entry
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
	save_entry=Entry(control)
	save_entry.grid(row=r,column=0,columnspan=3)
	Button(control,text='Save',command=save).grid(row=r,column=3)
	r+=1
	load_entry=Entry(control)
	load_entry.grid(row=r,column=0,columnspan=3)
	Button(control,text='Load',command=load).grid(row=r,column=3)
	control.mainloop()
def game_thread():
	global screen,grid,living
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
		#input
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
		if living:
			for cell in Cell.all_cells:
				if cell.should_be_born():cell.tbb.append(cell)
				elif cell.should_die():Cell.tbk.append(cell)
			Cell.life_or_death()
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
#-----------------------------
