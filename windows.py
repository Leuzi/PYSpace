""" Copyright Ramón Izuel Rios 2011
	Copyright Juan Antonio Pedraza Gutiérrez 2011
 * 
 * This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>
"""

﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import os
import pygame
from pygame.locals import *

ANCHO = 1200
ALTO = 700

def load_image(name,colorkey=False):

	"""Genera una superficie a partir de una archivo de imagen.

	Retornará la imagen junto con su tamaño en formato de tupla."""

	fullname = name

	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print 'No se puede cargar la imagen: ', fullname
		raise SystemExit, message

	image = image.convert()

	if colorkey:
		colorkey = image.get_at((0, 0))
		image.set_colorkey(colorkey, RLEACCEL)

	return (image, image.get_rect())

def load_sound(name):
	"""Carga un sonido a partir de un archivo.

	Si existe algun problema al cargar el sonido intenta crear
	un objeto Sound virtual."""

	class NoneSound:
		def play(self):
			pass

	if not pygame.mixer or not pygame.mixer.get_init():
		return NoneSound()

	fullname = os.path.join("datos", name)

	try:
		sound = pygame.mixer.Sound(fullname)
	except pygame.error, message:
		print 'No se pudo cargar el sonido: ', fullname
		raise SystemExit, message

	return sound
    
class Boom(pygame.sprite.Sprite):
	"""Representa una explosion de las naves enemigas"""
	
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self._load_images()
		self.step = 0
		self.delay = 2
		(self.image, self.rect) = load_image('datos/boom/1.png', True)
		self.rect.center = (x, y)

	def _load_images(self):
		"""Carga la lista 'self.frames' con todos los cuadros de animacion"""

		self.frames = []

		for n in range(1, 5):
			path = 'datos/boom/%d.png'
			new_image = load_image(path % n, True)[0]
			self.frames.append(new_image)
		
	def update(self,mover):
		self.image = self.frames[self.step]

		if self.delay < 0:
			self.delay = 2
			self.step += 1

			if self.step > 3:
				self.kill()
		else:
			self.delay -= 1

class Player(pygame.sprite.Sprite):

	def __init__(self,joystick):
		pygame.sprite.Sprite.__init__(self)
		(self.image, self.rect) = load_image('datos/nave.png', True)
		self.invisible_counter = 0
		self.joystick=joystick
		self.x_velocity = 0
		self.y_velocity = 0

	def mover_dcha(self):
		self.x_velocity += 5

	
	def mover_izda(self):
		self.x_velocity -= 5

	def can_be_killed(self):
		"""Informa si la nave puede ser eliminada por un disparo o choque."""
		return self.invisible_counter <= 0

	def update(self,mover):
		if pygame.joystick.get_count()>0:
			
			self.rect.move_ip((self.x_velocity, self.y_velocity))
			if(self.x_velocity>0):
				self.x_velocity-=0.1
			elif(self.x_velocity<0):
				self.x_velocity+=0.1	

		else:
			posicion = pygame.mouse.get_pos()
			self.rect.center = posicion

        # Evita que la nave salga del rango permitido.
		if self.rect.left < 0:
			self.rect.left = 0
			self.x_velocity=0
		elif self.rect.right > ANCHO:
			self.rect.right = ANCHO
			self.x_velocity=0

		self.rect.top = 610


class Enemy(pygame.sprite.Sprite):
	"""Representa un enemigo del juego."""

	def __init__(self, enemy_lasers, sprites, shot_sound,i,j,enemigo):
		pygame.sprite.Sprite.__init__(self)
		self.load_image(enemigo)
		self.dcha=True
		self.abajo=False
		self.nivel=1
		self.set_initial_position(i,j)
		self.enemy_lasers = enemy_lasers
		self.sprites = sprites
		self.shot_sound = shot_sound

	def load_image(self,enemigo):
		(self.image, self.rect) = load_image(enemigo, True)

	def set_initial_position(self,i,j):
		self.rect.centerx = (ANCHO/15+20)*(j+1)
		self.rect.y = 85+60*i;
		self.y_velocity = 0

	def set_nivel(self,nivel):
		self.nivel = nivel

	def change_direccion(self,direccion):
		self.dcha=direccion
	
	def get_direccion(self):
		return self.dcha
		
	def bajar(self):
		self.abajo=True
		
	def puede_izq(self):
		return (self.rect.left-25 >= 0)
	
	def puede_dcha(self):
		return (self.rect.right+25 <= ANCHO)
		
	def update(self,mover):
		if(mover):
			if(self.abajo):
				self.rect.y+=50
				self.abajo=False
			else:
				if(self.dcha):
					self.rect.x+=50
			
				else:
					self.rect.x-=50
		
		fire = random.randint(1, 100000/(300*self.nivel))
		if fire == 1:
			self.create_shot()
			
	def create_shot(self):
		new_shot = EnemyShot(self.rect.midbottom)
		self.enemy_lasers.add(new_shot)
		self.sprites.add(new_shot)
		self.shot_sound.play()
            
# Laser de jugador #
class PlayerLaser(pygame.sprite.Sprite):

	def __init__(self, startpos):
		pygame.sprite.Sprite.__init__(self)
		(self.image, self.rect) = load_image('datos/euro.png', True)
		self.rect.center = startpos

	# Si se sale por la parte superior de la pantalla,lo matamos

	def update(self,mover):
		if self.rect.bottom <= 100:
			self.kill()
		else:
			self.rect.move_ip((0, -4))
         
            
class EnemyShot(pygame.sprite.Sprite):

	def __init__(self, startpos):
		pygame.sprite.Sprite.__init__(self)
		(self.image, self.rect) = load_image('datos/dollar.png', True)
		self.rect.midtop = startpos

	def update(self,mover):
		if self.rect.top >= ALTO-75:
			self.kill()
		else:
			self.rect.move_ip((0, 4))
	
def main():
	random.seed()
	pygame.display.init()
	pygame.font.init()
	pygame.joystick.init()
	pygame.mixer.init()

	# Definimos la pantalla
	size = (ANCHO,ALTO)
	screen = pygame.display.set_mode(size)
	pygame.display.set_caption('Invaders of Consumerism')


    # Anadimos la imagen de fondo
	(background_image, _) = load_image('datos/background.jpg')
	screen.blit(background_image, (0, 0))

	# Cargamos todos los sonidos
	explode_sound = load_sound('sonidos/explosion.ogg')
	shot_sound = load_sound('sonidos/disparo.ogg')
	move_sound = load_sound('sonidos/mover.ogg')
	explosion_final = load_sound('sonidos/explosionfinal.ogg')
	final = load_sound('sonidos/final.ogg')
	intro = load_sound('sonidos/intro.ogg')
	ultima = load_sound('sonidos/ultima.ogg')
	seleccion = load_sound('sonidos/seleccion.ogg')
	
	
	n_j = pygame.joystick.get_count()

	joystick='null'
	
	if(n_j>0):
		joystick = pygame.joystick.Joystick(0)
		joystick.init()
		
	# Cargamos todos los enemigos
	enemigos =[]
	
	for n in range(1, 11):
		path = 'datos/enemigos/%d.png'
		enemigos.append(path % n)
	
	# Creamos el grupo de sprites que se acualizan e imprimen
	sprites = pygame.sprite.RenderClear()

	# Se genera el resto de los grupos
	enemies = pygame.sprite.RenderClear()
	player_lasers = pygame.sprite.RenderClear()
	enemy_lasers = pygame.sprite.RenderClear()
	player = Player(joystick)
	sprites.add(player)

	# Contador para las apariciones de los malos
	creation_enemy_counter = 0

	# Reloj de juego
	clock = pygame.time.Clock()
	
	# Hacemos invisible el raton
	pygame.mouse.set_visible(False)

	# Fuente y puntajes
	fuente_intro = pygame.font.Font('datos/fuentes/Astrolyte.ttf', 30)
	fuente_menu = pygame.font.Font('datos/fuentes/Astrolyte.ttf',25)
	fuente_juego = pygame.font.Font('datos/fuentes/EricssonGA628.ttf',20)
	fuente_normal = pygame.font.Font('datos/fuentes/DejaVuSans.ttf',25)

	salir = False

	letras = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','0','1','2','3','4','5','6','7','8','9']



	while not salir:

		start = fuente_intro.render('P U L S A  S T A R T',1,(252,255,0))
		invaders = fuente_intro.render('I N V A D E R S   O F    C O N S U M E R I M S',1,(252,255,0))
		manolo = fuente_normal.render('Autor: Manuel Marcos Barrera Mago',1,(255,255,255))
		yo = fuente_normal.render('Colaborador: Ramon Izuel Rios',1,(255,255,255))
		cero = fuente_juego.render('0  L I V E S ',1,(255,255,255))
		while not salir:

			for event in pygame.event.get():
				if (event.type == KEYDOWN and event.key == K_SPACE) or event.type == JOYBUTTONDOWN:
					salir = True

			if((pygame.time.get_ticks()%2000)>1000):
				pygame.draw.rect(screen,(0,215,0),(350,200,450,100),5)
				pygame.draw.rect(screen,(0,215,0),(150,300,900,100),5)
				screen.blit(start, (380, 220))
				screen.blit(invaders, (162, 330))
				screen.blit(manolo,(220,620))
				screen.blit(yo,(220,650))
				pygame.display.flip()
				
			
			else:
				screen.blit(background_image, (0, 0))
				screen.blit(manolo,(220,620))
				screen.blit(yo,(220,650))
				pygame.display.flip()
				
		
		salir = False
		
		opcion = 1
			
		intro.play()

		inicio = fuente_menu.render(' I N I C I O ',1,(255,255,255))
		record = fuente_menu.render(' R E C O R D S',1,(255,255,255))
		creditos = fuente_menu.render(' C R E D I T O S',1,(255,255,255))		
			
		while not salir:

			for event in pygame.event.get():
				if (event.type == KEYDOWN and event.key == K_SPACE) or event.type == JOYBUTTONDOWN:
					salir = True
				
				if(n_j>0):
					if(event.type == JOYAXISMOTION):
						y = joystick.get_axis(1)
						if(y<(-0.5) and opcion != 1):
							opcion-=1
						elif(y>0.5 and opcion !=3):
							opcion+=1
							
				elif event.type == KEYDOWN and event.key == K_UP and opcion != 1:
					opcion-=1
				
				elif event.type == KEYDOWN and event.key == K_DOWN and opcion != 3:
					opcion +=1
			

			screen.blit(background_image,(0,0))		
			pygame.draw.rect(screen,(0,215,0),(400,200,400,300),5)
	


			if((pygame.time.get_ticks()%2000)>1000):

				if(opcion == 1):
					screen.blit(record,(460,340))
					screen.blit(creditos,(460,440))
				elif(opcion == 2):
					screen.blit(inicio,(460,240))
					screen.blit(creditos,(460,440))
				else:
					screen.blit(inicio,(460,240))
					screen.blit(record,(460,340))

			else:

				screen.blit(inicio,(460,240))
				screen.blit(record,(460,340))
				screen.blit(creditos,(460,440))
			
			pygame.display.flip()

		seleccion.play()
		pygame.time.wait(1000)

		if opcion == 1:
			# Bucle Principal
			# Puntos y nivel
			puntos = 0
			nivel = 1
			running = True
			sube = True
			mover = False
			screen.blit(background_image, (0, 0))
			pygame.display.flip()
			MOVER = USEREVENT + 1
			pygame.time.set_timer(MOVER,1000/nivel);
			intro.stop()

			puntuacion = fuente_intro.render( 'Level : ' + str(nivel) +'                          Score : ' +str(puntos),1,(255,255,255))		
			while running:
				clock.tick(50)
				# Genera naves 
				if sube:
					sprites.remove(enemy_lasers.sprites())
					sprites.remove(player_lasers.sprites())
					sprites.remove(enemies.sprites())
					enemies.empty()
					enemy_lasers.empty()
					player_lasers.empty()					
					pygame.draw.rect(screen,(0,212,0),(395,195,410,210),0)				
					pygame.draw.rect(screen,(0,0,0),(400,200,400,200),0)
					cartel = fuente_intro.render(('Nivel  ' + str(nivel)),1,(255,252,0))
					screen.blit(cartel,(540,280))
					pygame.display.flip()
					pygame.time.wait(nivel*1000)
					screen.blit(background_image,(0,0))
					
					
					if(nivel == 3):
						ultima.play(3,0)
						pygame.time.wait(1500)
						
			
					for i in range(0,4):
						for j in range(0,8):
							new_enemy = Enemy(enemy_lasers, sprites, shot_sound,i,j,enemigos[random.randint(0,9)])
							enemies.add(new_enemy)
							sprites.add(new_enemy)
					
					
					lista = enemies.sprites()
					
					for de in lista:
						de.set_nivel(nivel)
					
					sube = False

				# Procesa los eventos de la ventana, y la creacion de disparos.
				for event in pygame.event.get():
					if event.type == QUIT:
						running = False
					elif event.type == KEYDOWN and event.key == K_ESCAPE:
						running = False
					elif event.type == MOVER:
						sprites.update(True)
						move_sound.play()
					elif event.type == MOUSEBUTTONDOWN or event.type == pygame.locals.JOYBUTTONDOWN:

						lista = player_lasers.sprites()
						
						if (len(lista)<6):

							if event.button == 1:
								laser_1 = PlayerLaser(player.rect.midleft)
								laser_2 = PlayerLaser(player.rect.midright)

								new_lasers = [laser_1, laser_2]
								player_lasers.add(new_lasers)
								sprites.add(new_lasers)

								shot_sound.play()
					elif event.type == pygame.locals.JOYAXISMOTION:
						x = joystick.get_axis(0)
						if (x<(-0.5)):
							player.mover_izda()
						elif (x>(0.5)):
							player.mover_dcha()


				# Incremento de nivel
				lista = enemies.sprites();
				
				if len(lista) == 0 :
					nivel +=1
					sube = True
				
				if len(lista) > 0:	

					Todos = True
				
					direccion= lista[0].get_direccion();
					
					for de in lista:
						if(Todos):
							if( direccion):
								if( not (de.puede_dcha()) ):
									Todos = False

						
							else:
								if( not (de.puede_izq()) ):
									Todos = False
					
					if(Todos == False):
						for de in lista:
							de.change_direccion( not direccion)
							de.bajar()
					
				# Controla las colisiones entre los enemigos y nuestros disparos.
				for hit in pygame.sprite.groupcollide(enemies, player_lasers, 1, 1):
					# Hace explotar la nave
					(x, y) = hit.rect.center
					sprites.add(Boom(x, y))
					explode_sound.play()
					puntos += 50
					puntuacion = fuente_intro.render( 'Level : ' + str(nivel) +'                          Score : ' +str(puntos),1,(255,255,255))

				# Controla las colisiones ente la nave y los enemigos (o sus disparos)
				if player.can_be_killed():
					dangerous_sprites = pygame.sprite.Group(enemies, enemy_lasers)

					for hit in pygame.sprite.spritecollide(player, dangerous_sprites, 1):
						# Hace explotar la nave
						(x, y) = hit.rect.center
						explosion_final.play() 
						final.play()
						game_over=fuente_intro.render(' G A M E   O V E R',1,(255,255,255))
						consumismo= fuente_juego.render( ' El consumismo te ha vencido',1,(255,255,255))
						pygame.draw.rect(screen,(0,212,0),(395,175,510,210),0)				
						pygame.draw.rect(screen,(0,0,0),(400,180,500,200),0)
						screen.blit(game_over,(470,235))
						screen.blit(consumismo,(470,295))
						pygame.display.flip()
						
						

						#Cargamos las puntuaciones
						f = open('datos/Puntuaciones','r')
	
						jugadores = []
						records = []
	
						jugadores =f.readlines()
	
						f.close()
	
						for n in range(0,6):
							records.append([jugadores[n*2],(int(jugadores[n*2+1]))])

						encontrado = False
						posicion = -1
						for n in range(0,6):
							if(records[n][1]< puntos):
								if(encontrado != True):
									encontrado = True
									posicion = n
			
							
						if(encontrado):
							salir = False
							letrae=1
							letra1=0
							letra2=0
							letra3=0

							record = fuente_intro.render('N U E V O  R E C O R D',1,(255,252,0))
							puntuacion = fuente_intro.render('N U E V A  P U N T U A C I O N',1,(255,252,0))
							
							while not salir:

								pygame.draw.rect(screen,(0,212,0),(295,125,710,310),0)				
								pygame.draw.rect(screen,(0,0,0),(300,130,700,300),0)

								if(posicion == 0):

									screen.blit(record,(420,150))
								else:

									screen.blit(puntuacion,(380,150))
							
								for ev in pygame.event.get():
									if ev.type == KEYDOWN and ev.key == K_SPACE or ev.type == JOYBUTTONDOWN:
										salir=True
									if(letrae==1):
										if(((ev.type == KEYDOWN and ev.key==K_DOWN) or (ev.type==JOYAXISMOTION and joystick.get_axis(1)>0.5)) and letra1!=35):
											letra1+=1
										if(((ev.type == KEYDOWN and ev.key==K_UP) or (ev.type==JOYAXISMOTION and joystick.get_axis(1)< -0.5)) and  letra1!=0):
											letra1-=1
									elif(letrae==2):
										if(((ev.type == KEYDOWN and ev.key==K_DOWN) or (ev.type==JOYAXISMOTION and joystick.get_axis(1)>0.5)) and letra2!=35):
											letra2+=1
										if(((ev.type == KEYDOWN and ev.key==K_UP) or (ev.type==JOYAXISMOTION and joystick.get_axis(1)< -0.5)) and letra2!=0):
											letra2-=1
									elif(letrae==3):
										if(((ev.type == KEYDOWN and ev.key==K_DOWN) or (ev.type==JOYAXISMOTION and joystick.get_axis(1)>0.5)) and letra3!=35):
											letra3+=1
										if(((ev.type == KEYDOWN and ev.key==K_UP) or (ev.type==JOYAXISMOTION and joystick.get_axis(1)< -0.5)) and letra3!=0):
											letra3-=1

									if(((ev.type == KEYDOWN and ev.key==K_RIGHT) or (ev.type==JOYAXISMOTION and joystick.get_axis(0)>(0.5))) and letrae!=3):
										letrae+=1
									if(((ev.type == KEYDOWN and ev.key==K_LEFT) or (ev.type==JOYAXISMOTION and joystick.get_axis(0)<(-0.5))) and letrae!=1):
										letrae-=1

								nombre = letras[letra1] +'     ' + letras[letra2] + '     '+ letras[letra3]
								pl = fuente_intro.render(nombre,1,(255,252,0))
								screen.blit(pl,(540,300))
								pygame.display.flip()																
	
							nombre=letras[letra1] + letras[letra2] + letras[letra3]+'\n'
							i = 5
							for n in range (posicion,5):
								records[i][0]=records[i-1][0]
								records[i][1]=records[i-1][1]
								i-=1
							records[posicion][0]=nombre
							records[posicion][1]=puntos



							f = open('datos/Puntuaciones','w')

							meter=[]

							for n in range(0,6):
								linea1=records[n][0]
								linea2=str(records[n][1])+'\n'
								meter.append(linea1)
								meter.append(linea2)

							f.writelines(meter)

							f.close()
						
						sprites.remove(enemies.sprites())
						sprites.remove(player_lasers.sprites())
						sprites.remove(enemy_lasers.sprites())
						enemies.empty()
						enemy_lasers.empty()
						player_lasers.empty()		
						
						pygame.time.wait(7500)
						running = False
						salir=False
						
	
				sprites.update(False)
				sprites.clear(screen, background_image)
				sprites.draw(screen)
				pygame.draw.rect(screen,(0,212,0),(50,75,1100,3),0)
				pygame.draw.rect(screen,(0,212,0),(50,645,1100,3),0)
				pygame.draw.rect(screen,(0,0,0),(400,25,700,50),0)
				screen.blit(puntuacion,(300,25))
				screen.blit(cero,(50,650))
				
				pygame.display.flip()
		
		elif(opcion==2):

			#Cargamos las puntuaciones
			f = open('datos/Puntuaciones','r')
	
			jugadores = []
			records = []
	
			jugadores =f.readlines()
	
			f.close()
	
			for n in range(0,6):
				records.append([jugadores[n*2],(int(jugadores[n*2+1]))])

			salir = False
			record = fuente_intro.render(' R E C O R D S ',1,(252,255,0))
			pulsa = fuente_intro.render('< P u l s e   c u a l q u i e r   t e c l a >',1,(255,255,255))
			while not salir:
				for event in pygame.event.get():
					if event.type == QUIT:
						salir = True
					elif event.type == KEYDOWN or event.type == JOYBUTTONDOWN:
						salir = True
			
				screen.blit(background_image,(0,0))
				for n in range(0,6):
					jugador= records[n][0] + '--------------------------------------------------> ' + str(records[n][1])
					juga = fuente_intro.render(jugador,1,(0,212,0))
					screen.blit(juga,(40,150+n*75))

				if(pygame.time.get_ticks()%2000>1000):

					screen.blit(record,(450,20))
				else:
					screen.blit(pulsa,(270,650))
				
				pygame.display.flip()
			
			intro.stop()
			salir=False		
		
		
		elif(opcion==3):
			screen.blit(background_image,(0,0))		
	
			pygame.draw.rect(screen,(0,212,0),(295,125,710,310),0)				
			pygame.draw.rect(screen,(0,0,0),(300,130,700,300),0)
		
			autor = fuente_intro.render('A U T O R',1,(0,212,0))
			manolo = fuente_intro.render('Manuel Marcos Barrera "Mago"',1,(0,212,0))
			colaborador = fuente_intro.render('C O L A B O R A D O R',1,(0,212,0))
			yo = fuente_intro.render('Ramon Izuel Rios',1,(0,212,0))

			imagen = fuente_intro.render('I M A G E N  Y  S O N I D O',1,(0,212,0))
			programador = fuente_intro.render('P R O G R A M A C I O N',1,(0,212,0))
			granada =fuente_intro.render('G R A N A D A',1,(0,212,0))
			clase1 = fuente_intro.render('E S C U L T U R A  Y  N U E V A S  T E C N O L O G I A S',1,(0,212,0))
			clase2 = fuente_intro.render('F A C U L T A D  D E  B E L L A S  A R T E S',1,(0,212,0))
			
			salir = False

			while not salir:

				screen.blit(autor,(520,150))
				screen.blit(manolo,(420,200))
				screen.blit(colaborador,(440,290))
				screen.blit(yo,(500,350))
				pygame.display.flip()

				for event in pygame.event.get():
					if event.type == QUIT:
						salir = True
					elif event.type == KEYDOWN or event.type == JOYBUTTONDOWN:
						salir = True
			

			salir=False
			screen.blit(background_image,(0,0))
			pygame.draw.rect(screen,(0,212,0),(295,125,710,310),0)				
			pygame.draw.rect(screen,(0,0,0),(300,130,700,300),0)
			while not salir:
				screen.blit(imagen,(420,150))
				screen.blit(manolo,(420,200))
				screen.blit(programador,(440,290))
				screen.blit(yo,(500,350))
				pygame.display.flip()

				for event in pygame.event.get():
					if event.type == QUIT:
						salir = True
					elif event.type == KEYDOWN or event.type == JOYBUTTONDOWN:
						salir = True
						
			salir=False
			screen.blit(background_image,(0,0))

			while not salir:
				screen.blit(clase1,(50,200))
				screen.blit(clase2,(180,350))
				screen.blit(granada,(470,500))
				pygame.display.flip()

				for event in pygame.event.get():
					if event.type == QUIT:
						salir = True
					elif event.type == KEYDOWN or event.type == JOYBUTTONDOWN:
						salir = True	
						
			intro.stop()		

			salir= False
			
if __name__ == '__main__':
	main()


